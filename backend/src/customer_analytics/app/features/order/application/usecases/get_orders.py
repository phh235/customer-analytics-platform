"""Get orders use case — Business logic for listing orders."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.order.application.dto.order_query_model import (
    OrderListResult,
    OrderReadModel,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetOrdersUseCase(
    BaseUseCase[tuple[int, int, str | None, str | None, str | None], OrderListResult]
):
    """Get orders use case interface."""

    @abstractmethod
    async def __call__(
        self, args: tuple[int, int, str | None, str | None, str | None]
    ) -> OrderListResult:
        raise NotImplementedError()


class GetOrdersUseCaseImpl(GetOrdersUseCase):
    """Get orders use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(
        self, args: tuple[int, int, str | None, str | None, str | None]
    ) -> OrderListResult:
        skip, limit, customer_id, status, search = args

        orders = await self.repository.find_all(
            skip=skip,
            limit=limit,
            customer_id=customer_id,
            status=status,
            search=search,
        )

        # Count total (simplified)
        all_orders = await self.repository.find_all(
            customer_id=customer_id,
            status=status,
            search=search,
        )
        total = len(all_orders)
        pages = (total + limit - 1) // limit if limit > 0 else 1
        current = (skip // limit) + 1 if limit > 0 else 1

        return OrderListResult(
            current=current,
            size=limit,
            total=total,
            pages=pages,
            records=[OrderReadModel.from_entity(o) for o in orders],
        )
