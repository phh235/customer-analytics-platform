"""Update order use case — Business logic for updating an order."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.order.application.dto.order_command_model import (
    OrderUpdateModel,
)
from customer_analytics.app.features.order.application.dto.order_query_model import (
    OrderReadModel,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class UpdateOrderUseCase(BaseUseCase[tuple[str, OrderUpdateModel], OrderReadModel]):
    """Update order use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[str, OrderUpdateModel]) -> OrderReadModel:
        raise NotImplementedError()


class UpdateOrderUseCaseImpl(UpdateOrderUseCase):
    """Update order use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[str, OrderUpdateModel]) -> OrderReadModel:
        order_id, data = args

        # Find existing order
        order = await self.repository.find_by_id(order_id)
        if order is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Order with ID '{order_id}' không tồn tại.",
            )

        update_data = data.model_dump(exclude_unset=True)
        if "refund_amount" in update_data:
            refund_amount = update_data.pop("refund_amount")
            if refund_amount is None:
                refund_amount = order.refund_amount
            from customer_analytics.app.features.order.domain.rules import (
                calculate_net_amount,
            )

            order.refund_amount = refund_amount
            order.net_amount = calculate_net_amount(order.total_amount, refund_amount)
        if "status" in update_data and update_data["status"] is not None:
            from customer_analytics.app.features.order.domain.rules import (
                validate_order_status,
            )

            update_data["status"] = validate_order_status(update_data["status"])
        for key, value in update_data.items():
            setattr(order, key, value)

        updated_order = await self.repository.update(order)
        return OrderReadModel.from_entity(updated_order)
