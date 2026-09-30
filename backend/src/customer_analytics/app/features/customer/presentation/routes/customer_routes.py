"""Customer routes — API endpoints for customer management."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from customer_analytics.app.config import settings
from customer_analytics.app.features.customer.application.usecases.create_customer import (
    CreateCustomerUseCaseImpl,
)
from customer_analytics.app.features.customer.application.usecases.delete_customer import (
    DeleteCustomerUseCaseImpl,
)
from customer_analytics.app.features.customer.application.usecases.get_customer import (
    GetCustomerUseCaseImpl,
)
from customer_analytics.app.features.customer.application.usecases.get_customers import (
    GetCustomersUseCaseImpl,
)
from customer_analytics.app.features.customer.application.usecases.update_customer import (
    UpdateCustomerUseCaseImpl,
)
from customer_analytics.app.features.customer.infrastructure.repositories.customer_unit_of_work_impl import (
    CustomerUnitOfWorkImpl,
)
from customer_analytics.app.features.customer.presentation.schema.customer import (
    CustomerCreateRequest,
    CustomerErrorResponse,
    CustomerResponse,
    CustomerUpdateRequest,
    PaginatedCustomersResponse,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    get_current_user,
    require_permission,
)
from customer_analytics.app.shared.cloudinary_service import CloudinaryImageService
from customer_analytics.core.dependencies import DatabaseSessionDep

router = APIRouter(prefix="/api/v1", tags=["Customer Management"])


def _get_customer_unit_of_work(
    session: DatabaseSessionDep,
    current_user: UserEntity = Depends(get_current_user),
) -> CustomerUnitOfWorkImpl:
    """Dependency to get customer unit of work with data scope."""
    return CustomerUnitOfWorkImpl(session, current_user)


# Type alias for UnitOfWork dependency
UnitOfWorkDep = Annotated[CustomerUnitOfWorkImpl, Depends(_get_customer_unit_of_work)]


@router.get(
    "/customers",
    response_model=PaginatedCustomersResponse,
    status_code=status.HTTP_200_OK,
    summary="List customers",
    description="Get paginated list of customers. Requires customers:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Customers list",
            "model": PaginatedCustomersResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or missing token",
            "model": CustomerErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient permissions",
            "model": CustomerErrorResponse,
        },
    },
)
async def list_customers(
    current_user: Annotated[UserEntity, Depends(require_permission("customers:read"))],
    unit_of_work: UnitOfWorkDep,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 10,
    search: Annotated[
        str | None, Query(description="Search by name, email, or phone")
    ] = None,
) -> PaginatedCustomersResponse:
    """Lay danh sach khach hang (can quyen customers:read)."""
    skip = (page - 1) * size
    use_case = GetCustomersUseCaseImpl(unit_of_work)
    result = await use_case((skip, size, search))

    return PaginatedCustomersResponse(
        current=result.current,
        size=result.size,
        total=result.total,
        pages=result.pages,
        records=[
            CustomerResponse(
                id=r.id,
                image_url=r.image_url,
                customer_code=r.customer_code,
                name=r.name,
                email=r.email,
                phone=r.phone,
                address=r.address,
                status=r.status,
                gender=r.gender,
                date_of_birth=r.date_of_birth,
                region=r.region,
                assigned_user_id=r.assigned_user_id,
                team_id=r.team_id,
                customer_since=r.customer_since,
                total_orders=r.total_orders,
                total_spent=r.total_spent,
                avg_order_value=r.avg_order_value,
                last_purchase_date=r.last_purchase_date,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in result.records
        ],
    )


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Get customer",
    description="Get customer by ID. Requires customers:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Customer info",
            "model": CustomerResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": CustomerErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": CustomerErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": CustomerErrorResponse},
    },
)
async def get_customer(
    customer_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("customers:read"))],
    unit_of_work: UnitOfWorkDep,
) -> CustomerResponse:
    """Lay thong tin khach hang."""
    use_case = GetCustomerUseCaseImpl(unit_of_work)
    result = await use_case((str(customer_id),))
    return CustomerResponse.model_validate(result)


@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create customer",
    description="Create a new customer. Requires customers:create permission.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Customer created successfully",
            "model": CustomerResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": CustomerErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": CustomerErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": CustomerErrorResponse},
        status.HTTP_409_CONFLICT: {"model": CustomerErrorResponse},
    },
)
async def create_customer(
    body: CustomerCreateRequest,
    current_user: Annotated[
        UserEntity, Depends(require_permission("customers:create"))
    ],
    unit_of_work: UnitOfWorkDep,
) -> CustomerResponse:
    """Tao khach hang moi."""
    from customer_analytics.app.features.customer.application.dto.customer_command_model import (
        CustomerCreateModel,
    )

    create_model = CustomerCreateModel(
        name=body.name,
        image_url=body.image_url,
        email=body.email,
        phone=body.phone,
        address=body.address,
    )
    use_case = CreateCustomerUseCaseImpl(unit_of_work)
    result = await use_case((create_model,))
    return CustomerResponse.model_validate(result)


@router.patch(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Update customer",
    description="Update a customer. Requires customers:update permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Customer updated successfully",
            "model": CustomerResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": CustomerErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": CustomerErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": CustomerErrorResponse},
    },
)
async def update_customer(
    customer_id: uuid.UUID,
    body: CustomerUpdateRequest,
    current_user: Annotated[
        UserEntity, Depends(require_permission("customers:update"))
    ],
    unit_of_work: UnitOfWorkDep,
) -> CustomerResponse:
    """Cap nhat khach hang."""
    from customer_analytics.app.features.customer.application.dto.customer_command_model import (
        CustomerUpdateModel,
    )

    update_model = CustomerUpdateModel(
        name=body.name,
        image_url=body.image_url,
        email=body.email,
        phone=body.phone,
        address=body.address,
        status=body.status,
    )
    use_case = UpdateCustomerUseCaseImpl(unit_of_work)
    result = await use_case((str(customer_id), update_model))
    return CustomerResponse.model_validate(result)


@router.post(
    "/customers/{customer_id}/image",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload customer image",
    description="Upload a customer image to Cloudinary.",
    responses={
        status.HTTP_200_OK: {"model": CustomerResponse},
        status.HTTP_400_BAD_REQUEST: {"model": CustomerErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": CustomerErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": CustomerErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": CustomerErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": CustomerErrorResponse},
    },
)
async def upload_customer_image(
    customer_id: uuid.UUID,
    current_user: Annotated[
        UserEntity, Depends(require_permission("customers:update"))
    ],
    unit_of_work: UnitOfWorkDep,
    image: Annotated[UploadFile, File(...)],
) -> CustomerResponse:
    """Upload and persist a customer image URL."""
    from customer_analytics.app.features.customer.application.dto.customer_command_model import (
        CustomerUpdateModel,
    )
    from customer_analytics.app.shared.errors import ErrorCode
    from customer_analytics.app.shared.exceptions import AppException

    if not image.content_type or not image.content_type.startswith("image/"):
        raise AppException(
            error_code=ErrorCode.BAD_REQUEST,
            message="Tệp tải lên phải là ảnh.",
        )

    content = await image.read()
    if len(content) > 10 * 1024 * 1024:
        raise AppException(
            error_code=ErrorCode.BAD_REQUEST,
            message="Ảnh không được vượt quá 10 MB.",
        )

    image_url = await CloudinaryImageService(
        settings.CLOUDINARY_CUSTOMER_FOLDER
    ).upload(content, image.filename)
    use_case = UpdateCustomerUseCaseImpl(unit_of_work)
    result = await use_case(
        (str(customer_id), CustomerUpdateModel(image_url=image_url))
    )
    return CustomerResponse.model_validate(result)


@router.delete(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable customer",
    description="Disable a customer (soft delete). Requires customers:delete permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Customer disabled successfully",
            "model": CustomerResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": CustomerErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": CustomerErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": CustomerErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": CustomerErrorResponse},
    },
)
async def delete_customer(
    customer_id: uuid.UUID,
    current_user: Annotated[
        UserEntity, Depends(require_permission("customers:delete"))
    ],
    unit_of_work: UnitOfWorkDep,
) -> CustomerResponse:
    """Vo hieu hoa khach hang (soft delete)."""
    use_case = DeleteCustomerUseCaseImpl(unit_of_work)
    result = await use_case((str(customer_id),))
    return CustomerResponse.model_validate(result)
