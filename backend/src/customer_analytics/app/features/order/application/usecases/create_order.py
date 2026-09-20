"""Create order use case — Business logic for creating a new order."""

from __future__ import annotations

import uuid
from abc import abstractmethod
from datetime import UTC, datetime
from decimal import Decimal

from customer_analytics.app.features.order.application.dto.order_command_model import (
    OrderCreateModel,
)
from customer_analytics.app.features.order.application.dto.order_query_model import (
    OrderReadModel,
)
from customer_analytics.app.features.order.domain.entities.order_entity import (
    OrderEntity,
    OrderItemEntity,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class CreateOrderUseCase(BaseUseCase[tuple[OrderCreateModel], OrderReadModel]):
    """Create order use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[OrderCreateModel]) -> OrderReadModel:
        raise NotImplementedError()


class CreateOrderUseCaseImpl(CreateOrderUseCase):
    """Create order use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[OrderCreateModel]) -> OrderReadModel:
        (data,) = args

        # Tạo mã đơn hàng duy nhất theo ngày hiện tại.
        order_number = (
            f"ORD-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        )

        # Tính tổng tiền từ các dòng hàng.
        total_amount = Decimal("0")
        order_items = []

        for item_data in data.items:
            subtotal = item_data.unit_price * item_data.quantity
            total_amount += subtotal
            order_items.append(
                OrderItemEntity(
                    id_=None,
                    order_id="",  # Sẽ được gắn sau khi tạo order.
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    unit_price=item_data.unit_price,
                    subtotal=subtotal,
                )
            )
        # Không cho phép số tiền hoàn lớn hơn tổng đơn.
        if data.refund_amount > total_amount:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="refund_amount cannot exceed total_amount.",
            )

        # Tạo entity order sau khi đã tính và kiểm tra dữ liệu.
        order = OrderEntity(
            id_=None,
            customer_id=data.customer_id,
            order_number=order_number,
            order_date=data.order_date,
            total_amount=total_amount,
            refund_amount=data.refund_amount,
            status="COMPLETED",
            channel=data.channel,
            notes=data.notes,
            items=order_items,
        )

        created_order = await self.repository.create(order)
        return OrderReadModel.from_entity(created_order)
