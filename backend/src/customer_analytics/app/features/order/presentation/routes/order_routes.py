"""Order routes — API endpoints for order management."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    CurrentUserDep,
    require_permission,
)
from customer_analytics.app.features.order.application.usecases.create_order import (
    CreateOrderUseCaseImpl,
)
from customer_analytics.app.features.order.application.usecases.delete_order import (
    DeleteOrderUseCaseImpl,
)
from customer_analytics.app.features.order.application.usecases.get_order import (
    GetOrderUseCaseImpl,
)
from customer_analytics.app.features.order.application.usecases.get_orders import (
    GetOrdersUseCaseImpl,
)
from customer_analytics.app.features.order.application.usecases.update_order import (
    UpdateOrderUseCaseImpl,
)
from customer_analytics.app.features.order.infrastructure.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from customer_analytics.app.features.order.presentation.schema.order import (
    OrderCreateRequest,
    OrderErrorResponse,
    OrderResponse,
    OrderUpdateRequest,
    PaginatedOrdersResponse,
)
from customer_analytics.core.database import AsyncSessionFactory

router = APIRouter(prefix="/api/v1", tags=["Order Management"])


async def _get_order_repository(
    current_user: CurrentUserDep,
):
    """Create an order repository with a managed async session."""
    async with AsyncSessionFactory() as session:
        try:
            yield OrderRepositoryImpl(session, current_user)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── List Orders ────────────────────────────────────────────


@router.get(
    "/orders",
    response_model=PaginatedOrdersResponse,
    status_code=status.HTTP_200_OK,
    summary="List orders",
    description="Get paginated list of orders. Requires orders:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Orders list",
            "model": PaginatedOrdersResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": OrderErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": OrderErrorResponse},
    },
)
async def list_orders(
    current_user: Annotated[UserEntity, Depends(require_permission("orders:read"))],
    repository: Annotated[OrderRepositoryImpl, Depends(_get_order_repository)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 10,
    customer_id: Annotated[
        uuid.UUID | None, Query(description="Filter by customer ID")
    ] = None,
    order_status: Annotated[
        str | None, Query(alias="status", description="Filter by status")
    ] = None,
    search: Annotated[
        str | None, Query(max_length=100, description="Search order or customer")
    ] = None,
) -> PaginatedOrdersResponse:
    """List orders with pagination and optional customer/order search."""
    skip = (page - 1) * size
    use_case = GetOrdersUseCaseImpl(repository)
    result = await use_case(
        (skip, size, str(customer_id) if customer_id else None, order_status, search)
    )

    return PaginatedOrdersResponse(
        current=result.current,
        size=result.size,
        total=result.total,
        pages=result.pages,
        records=[
            OrderResponse(
                id=r.id,
                customer_id=r.customer_id,
                order_number=r.order_number,
                order_date=r.order_date,
                total_amount=r.total_amount,
                refund_amount=r.refund_amount,
                net_amount=r.net_amount,
                status=r.status,
                channel=r.channel,
                notes=r.notes,
                items=r.items,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
            for r in result.records
        ],
    )


# ── Get Order ──────────────────────────────────────────────


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get order",
    description="Get order by ID. Requires orders:read permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Order info",
            "model": OrderResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": OrderErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": OrderErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": OrderErrorResponse},
    },
)
async def get_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("orders:read"))],
    repository: Annotated[OrderRepositoryImpl, Depends(_get_order_repository)],
) -> OrderResponse:
    """Lấy thông tin đơn hàng."""
    use_case = GetOrderUseCaseImpl(repository)
    result = await use_case((str(order_id),))
    return OrderResponse.model_validate(result)


# ── Create Order ───────────────────────────────────────────


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Create a new order. Requires orders:create permission.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Order created successfully",
            "model": OrderResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": OrderErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": OrderErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": OrderErrorResponse},
    },
)
async def create_order(
    body: OrderCreateRequest,
    current_user: Annotated[UserEntity, Depends(require_permission("orders:create"))],
    repository: Annotated[OrderRepositoryImpl, Depends(_get_order_repository)],
) -> OrderResponse:
    """Tạo đơn hàng mới."""
    from customer_analytics.app.features.order.application.dto.order_command_model import (
        OrderCreateModel,
        OrderItemCreateModel,
    )

    create_model = OrderCreateModel(
        customer_id=str(body.customer_id),
        order_date=body.order_date,
        refund_amount=body.refund_amount,
        channel=body.channel,
        notes=body.notes,
        items=[
            OrderItemCreateModel(
                product_id=str(item.product_id),
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in body.items
        ],
    )
    use_case = CreateOrderUseCaseImpl(repository)
    result = await use_case((create_model,))
    return OrderResponse.model_validate(result)


# ── Update Order ───────────────────────────────────────────


@router.patch(
    "/orders/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update order",
    description="Update an order. Requires orders:update permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Order updated successfully",
            "model": OrderResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {"model": OrderErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": OrderErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": OrderErrorResponse},
    },
)
async def update_order(
    order_id: uuid.UUID,
    body: OrderUpdateRequest,
    current_user: Annotated[UserEntity, Depends(require_permission("orders:update"))],
    repository: Annotated[OrderRepositoryImpl, Depends(_get_order_repository)],
) -> OrderResponse:
    """Cập nhật đơn hàng."""
    from customer_analytics.app.features.order.application.dto.order_command_model import (
        OrderUpdateModel,
    )

    update_model = OrderUpdateModel(
        status=body.status,
        refund_amount=body.refund_amount,
        notes=body.notes,
    )
    use_case = UpdateOrderUseCaseImpl(repository)
    result = await use_case((str(order_id), update_model))
    return OrderResponse.model_validate(result)


# ── Delete Order ───────────────────────────────────────────


@router.delete(
    "/orders/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel order",
    description="Cancel an order. Requires orders:delete permission.",
    responses={
        status.HTTP_200_OK: {
            "description": "Order cancelled successfully",
            "model": OrderResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": OrderErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": OrderErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": OrderErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": OrderErrorResponse},
    },
)
async def delete_order(
    order_id: uuid.UUID,
    current_user: Annotated[UserEntity, Depends(require_permission("orders:delete"))],
    repository: Annotated[OrderRepositoryImpl, Depends(_get_order_repository)],
) -> OrderResponse:
    """Hủy đơn hàng."""
    use_case = DeleteOrderUseCaseImpl(repository)
    result = await use_case((str(order_id),))
    return OrderResponse.model_validate(result)
