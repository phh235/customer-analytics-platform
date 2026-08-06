"""User routes — API endpoints for user management."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
    UserCreateModel,
)
from customer_analytics.app.features.identity.application.usecases.create_user import (
    CreateUserUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.get_users import (
    GetUsersUseCaseImpl,
)
from customer_analytics.app.features.identity.infrastructure.repositories.user_unit_of_work_impl import (  # noqa: E501
    UserUnitOfWorkImpl,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    AdminDep,
    CurrentUserDep,
    require_permission,
)
from customer_analytics.app.features.identity.presentation.schema.user import (
    ErrorResponse,
    PaginatedUsersResponse,
    RegisterRequest,
    UserResponse,
)
from customer_analytics.core.dependencies import DatabaseSessionDep

router = APIRouter(prefix="/api/v1", tags=["User Management"])


def _get_user_unit_of_work(session: DatabaseSessionDep) -> UserUnitOfWorkImpl:
    """Dependency to get user unit of work."""
    return UserUnitOfWorkImpl(session)


# Type alias for UnitOfWork dependency
UnitOfWorkDep = Annotated[UserUnitOfWorkImpl, Depends(_get_user_unit_of_work)]


@router.get(
    "/users",
    response_model=PaginatedUsersResponse,
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Get paginated list of users. Requires users:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Users list",
            "model": PaginatedUsersResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or missing token",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions",
            "model": ErrorResponse,
        },
    },
)
async def list_users(
    current_user: Annotated[CurrentUserDep, Depends(require_permission("users:read"))],
    unit_of_work: UnitOfWorkDep,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: str | None = Query(None, description="Search by email or name"),
) -> PaginatedUsersResponse:
    """Lay danh sach nguoi dung (can quyen users:read)."""
    skip = (page - 1) * size
    use_case = GetUsersUseCaseImpl(unit_of_work)
    result = await use_case((skip, size, search))

    return PaginatedUsersResponse(
        current=result.current,
        size=result.size,
        total=result.total,
        pages=result.pages,
        records=[
            UserResponse(
                id=r.id,
                email=r.email,
                full_name=r.full_name,
                status=r.status,
                role_code=r.role_code,
                permissions=r.permissions,
                created_at=r.created_at,
                last_login_at=r.last_login_at,
            )
            for r in result.records
        ],
    )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account. ADMIN only.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "User created successfully",
            "model": UserResponse,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Validation error",
            "model": ErrorResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or missing token",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions",
            "model": ErrorResponse,
        },
        status.HTTP_409_CONFLICT: {
            "description": "Email already exists",
            "model": ErrorResponse,
        },
    },
)
async def create_user(
    body: RegisterRequest,
    current_user: AdminDep,
    unit_of_work: UnitOfWorkDep,
) -> UserResponse:
    """Tao tai khoan moi (ADMIN only)."""
    # Convert RegisterRequest to UserCreateModel for the use case
    create_model = UserCreateModel(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        role_code=body.role_code,
    )
    use_case = CreateUserUseCaseImpl(unit_of_work)
    result = await use_case((create_model,))
    return UserResponse.model_validate(result)
