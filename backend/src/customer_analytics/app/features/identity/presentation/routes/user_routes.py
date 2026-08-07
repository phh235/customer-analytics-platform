"""User routes — API endpoints for user management."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
    UserCreateModel,
    UserUpdateModel,
)
from customer_analytics.app.features.identity.application.dto.user_query_model import (
    SortOrder,
    UserListQueryModel,
    UserRoleFilter,
    UserSortField,
    UserStatusFilter,
)
from customer_analytics.app.features.identity.application.usecases.create_user import (
    CreateUserUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.delete_user import (
    DeleteUserUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.get_users import (
    GetUsersUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.update_user import (
    UpdateUserUseCaseImpl,
)
from customer_analytics.app.features.identity.domain.enums import UserStatus
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
    UpdateUserRequest,
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
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 10,
    search: Annotated[str | None, Query(description="Search by email or name")] = None,
    role_code: Annotated[
        UserRoleFilter | None, Query(description="Filter by role code")
    ] = None,
    user_status: Annotated[
        UserStatusFilter | None,
        Query(alias="status", description="Filter by account status"),
    ] = None,
    sort_by: Annotated[
        UserSortField, Query(description="Secondary sort field after role priority")
    ] = "created_at",
    sort_order: Annotated[SortOrder, Query(description="Sort direction")] = "desc",
) -> PaginatedUsersResponse:
    """Lay danh sach nguoi dung (can quyen users:read)."""
    skip = (page - 1) * size
    use_case = GetUsersUseCaseImpl(unit_of_work)
    result = await use_case(
        UserListQueryModel(
            skip=skip,
            limit=size,
            search=search,
            role_code=role_code,
            status=user_status,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    )

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


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update a user account. ADMIN only.",
    responses={
        status.HTTP_200_OK: {
            "description": "User updated successfully",
            "model": UserResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    current_user: AdminDep,
    unit_of_work: UnitOfWorkDep,
) -> UserResponse:
    """Cap nhat tai khoan (ADMIN only)."""
    update_model = UserUpdateModel(
        full_name=body.full_name,
        role_code=body.role_code,
        status=UserStatus(body.status) if body.status is not None else None,
    )
    use_case = UpdateUserUseCaseImpl(unit_of_work)
    result = await use_case((str(user_id), update_model, str(current_user.id_)))
    return UserResponse.model_validate(result)


@router.delete(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable user",
    description="Disable a user account (soft delete). ADMIN only.",
    responses={
        status.HTTP_200_OK: {
            "description": "User disabled successfully",
            "model": UserResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    },
)
async def delete_user(
    user_id: uuid.UUID,
    current_user: AdminDep,
    unit_of_work: UnitOfWorkDep,
) -> UserResponse:
    """Vo hieu hoa tai khoan (soft delete, ADMIN only)."""
    use_case = DeleteUserUseCaseImpl(unit_of_work)
    result = await use_case((str(user_id), str(current_user.id_)))
    return UserResponse.model_validate(result)
