"""Get order use case — Business logic for getting a single order."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.order.application.dto.order_query_model import (
    OrderReadModel,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetOrderUseCase(BaseUseCase[tuple[str], OrderReadModel]):
    """Get order use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> OrderReadModel:
        raise NotImplementedError()


class GetOrderUseCaseImpl(GetOrderUseCase):
    """Get order use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[str]) -> OrderReadModel:
        (order_id,) = args

        order = await self.repository.find_by_id(order_id)
        if order is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Order with ID '{order_id}' không tồn tại.",
            )

        return OrderReadModel.from_entity(order)
