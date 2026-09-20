"""Order repository interface — Abstract base for order data access."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.order.domain.entities.order_entity import (
    OrderEntity,
)
from customer_analytics.core.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[OrderEntity]):
    """Order repository interface."""

    @abstractmethod
    async def find_by_customer_id(
        self, customer_id: str, skip: int = 0, limit: int = 100
    ) -> list[OrderEntity]:
        """Find orders by customer ID."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_order_number(self, order_number: str) -> OrderEntity | None:
        """Find order by order number."""
        raise NotImplementedError()

    @abstractmethod
    async def count_by_customer_id(self, customer_id: str) -> int:
        """Count orders by customer ID."""
        raise NotImplementedError()

    @abstractmethod
    async def get_customer_stats(
        self, customer_id: str
    ) -> dict[str, int | float] | None:
        """Get aggregated stats for a customer."""
        raise NotImplementedError()
