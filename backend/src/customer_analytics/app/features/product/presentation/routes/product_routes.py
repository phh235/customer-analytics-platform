"""Product routes — API endpoints for product management."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status

from customer_analytics.app.config import settings
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    require_permission,
)
from customer_analytics.app.features.product.application.usecases.create_product import (
    CreateProductUseCaseImpl,
)
from customer_analytics.app.features.product.application.usecases.delete_product import (
    DeleteProductUseCaseImpl,
)
from customer_analytics.app.features.product.application.usecases.get_product import (
    GetProductUseCaseImpl,
)
from customer_analytics.app.features.product.application.usecases.get_products import (
    GetProductsUseCaseImpl,
)
from customer_analytics.app.features.product.application.usecases.update_product import (
    UpdateProductUseCaseImpl,
)
from customer_analytics.app.features.product.infrastructure.repositories.product_interaction_repository_impl import (
    ProductInteractionRepositoryImpl,
)
from customer_analytics.app.features.product.infrastructure.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from customer_analytics.app.features.product.presentation.schema.product import (
    PaginatedProductsResponse,
    ProductCreateRequest,
    ProductDetailResponse,
    ProductErrorResponse,
    ProductResponse,
    ProductUpdateRequest,
    ProductViewRecordedResponse,
)
from customer_analytics.app.shared.cloudinary_service import CloudinaryImageService
from customer_analytics.core.database import AsyncSessionFactory

router = APIRouter(prefix="/api/v1", tags=["Product Management"])


async def _get_product_repository(request: Request):
    """Create product repository with a managed async session."""
    async with AsyncSessionFactory() as session:
        try:
            yield ProductRepositoryImpl(session)
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                await session.commit()
        except Exception:
            await session.rollback()
            raise


async def _get_product_interaction_repository(
    request: Request,
) -> AsyncGenerator[ProductInteractionRepositoryImpl]:
    """Create a transaction-scoped product interaction repository."""
    async with AsyncSessionFactory() as session:
        try:
            yield ProductInteractionRepositoryImpl(session)
            if request.method not in {"GET", "HEAD", "OPTIONS"}:
                await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── List Products ──────────────────────────────────────────


@router.get(
    "/products",
    response_model=PaginatedProductsResponse,
    status_code=status.HTTP_200_OK,
    summary="List products",
    description="Get paginated list of products. Requires products:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Products list",
            "model": PaginatedProductsResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
    },
)
async def list_products(
    current_user: Annotated[UserEntity, Depends(require_permission("products:read"))],
    repository: Annotated[ProductRepositoryImpl, Depends(_get_product_repository)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 10,
    category: Annotated[str | None, Query(description="Filter by category")] = None,
) -> PaginatedProductsResponse:
    """Lấy danh sách sản phẩm (cần quyền products:read)."""
    skip = (page - 1) * size
    use_case = GetProductsUseCaseImpl(repository)
    result = await use_case((skip, size, category))

    return PaginatedProductsResponse(
        current=result.current,
        size=result.size,
        total=result.total,
        pages=result.pages,
        records=[
            ProductResponse(
                id=r.id,
                product_code=r.product_code,
                name=r.name,
                sku=r.sku,
                category=r.category,
                description=r.description,
                image_url=r.image_url,
                price=r.price,
                status=r.status,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in result.records
        ],
    )


# ── Get Product ────────────────────────────────────────────


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product",
    description="Get product by ID. Requires products:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product info",
            "model": ProductDetailResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ProductErrorResponse},
    },
)
async def get_product(
    product_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("products:read"))],
    repository: Annotated[ProductRepositoryImpl, Depends(_get_product_repository)],
) -> ProductDetailResponse:
    from customer_analytics.app.features.product.application.dto.product_query_model import (
        ProductReadModel,
    )

    use_case = GetProductUseCaseImpl(repository)
    result = await use_case((str(product_id),))
    related_products = await repository.find_related(
        category=result.category,
        exclude_id=str(product_id),
    )
    response = ProductDetailResponse.model_validate(result)
    response.related_products = [
        ProductResponse.model_validate(ProductReadModel.from_entity(related))
        for related in related_products
    ]
    return response


@router.post(
    "/products/{product_id}/view",
    response_model=ProductViewRecordedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a product view",
    description="Record one product_view event for the authenticated customer.",
    responses={
        status.HTTP_201_CREATED: {"model": ProductViewRecordedResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ProductErrorResponse},
    },
)
async def record_product_view(
    product_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("products:read"))],
    repository: Annotated[
        ProductInteractionRepositoryImpl,
        Depends(_get_product_interaction_repository),
    ],
) -> ProductViewRecordedResponse:
    """Persist one product_view event without trusting a client customer ID."""
    if not current_user.id_:
        from customer_analytics.app.shared.errors import ErrorCode
        from customer_analytics.app.shared.exceptions import AppException

        raise AppException(ErrorCode.UNAUTHORIZED, "Authentication required")
    event_id = await repository.record_product_view(
        product_id,
        user_id=uuid.UUID(current_user.id_),
        email=current_user.email,
        full_name=current_user.full_name,
        customer_id=(
            uuid.UUID(current_user.customer_id) if current_user.customer_id else None
        ),
    )
    return ProductViewRecordedResponse(event_id=event_id)


# ── Upload Product Image ───────────────────────────────────


@router.post(
    "/products/{product_id}/image",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload product image",
    description="Upload a product image to Cloudinary.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product image uploaded",
            "model": ProductResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ProductErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ProductErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ProductErrorResponse},
    },
)
async def upload_product_image(
    product_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("products:update"))],
    repository: Annotated[ProductRepositoryImpl, Depends(_get_product_repository)],
    image: Annotated[UploadFile, File(...)],
) -> ProductResponse:
    """Upload and persist a product image URL."""
    from customer_analytics.app.features.product.application.dto.product_command_model import (
        ProductUpdateModel,
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

    image_url = await CloudinaryImageService(settings.CLOUDINARY_PRODUCT_FOLDER).upload(
        content, image.filename
    )
    use_case = UpdateProductUseCaseImpl(repository)
    result = await use_case((str(product_id), ProductUpdateModel(image_url=image_url)))
    return ProductResponse.model_validate(result)


# ── Create Product ─────────────────────────────────────────


@router.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product. Requires products:create permission.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Product created successfully",
            "model": ProductResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ProductErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ProductErrorResponse},
    },
)
async def create_product(
    body: ProductCreateRequest,
    current_user: Annotated[UserEntity, Depends(require_permission("products:create"))],
    repository: Annotated[ProductRepositoryImpl, Depends(_get_product_repository)],
) -> ProductResponse:
    """Tạo sản phẩm mới."""
    from customer_analytics.app.features.product.application.dto.product_command_model import (
        ProductCreateModel,
    )

    create_model = ProductCreateModel(
        name=body.name,
        sku=body.sku,
        category=body.category,
        description=body.description,
        image_url=body.image_url,
        price=body.price,
        status=body.status,
    )
    use_case = CreateProductUseCaseImpl(repository)
    result = await use_case((create_model,))
    return ProductResponse.model_validate(result)


# ── Update Product ─────────────────────────────────────────


@router.patch(
    "/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product",
    description="Update a product. Requires products:update permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product updated successfully",
            "model": ProductResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ProductErrorResponse},
    },
)
async def update_product(
    product_id: uuid.UUID,
    body: ProductUpdateRequest,
    current_user: Annotated[UserEntity, Depends(require_permission("products:update"))],
    repository: Annotated[ProductRepositoryImpl, Depends(_get_product_repository)],
) -> ProductResponse:
    """Cập nhật sản phẩm."""
    from customer_analytics.app.features.product.application.dto.product_command_model import (
        ProductUpdateModel,
    )

    update_model = ProductUpdateModel.model_validate(
        body.model_dump(exclude_unset=True)
    )
    use_case = UpdateProductUseCaseImpl(repository)
    result = await use_case((str(product_id), update_model))
    return ProductResponse.model_validate(result)


# ── Delete Product ─────────────────────────────────────────


@router.delete(
    "/products/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable product",
    description="Disable a product (soft delete). Requires products:delete permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Product disabled successfully",
            "model": ProductResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ProductErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ProductErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ProductErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ProductErrorResponse},
    },
)
async def delete_product(
    product_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("products:delete"))],
    repository: Annotated[ProductRepositoryImpl, Depends(_get_product_repository)],
) -> ProductResponse:
    """Vô hiệu hóa sản phẩm (soft delete)."""
    use_case = DeleteProductUseCaseImpl(repository)
    result = await use_case((str(product_id),))
    return ProductResponse.model_validate(result)
