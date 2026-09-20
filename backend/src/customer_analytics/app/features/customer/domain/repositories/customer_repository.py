"""Customer repository interface."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.customer.domain.entities.customer_entity import (
    CustomerEntity,
)
from customer_analytics.core.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[CustomerEntity]):
    """Customer repository interface."""

    @abstractmethod
    async def find_by_email(self, email: str) -> CustomerEntity | None:
        """Find a customer by email."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_phone(self, phone: str) -> CustomerEntity | None:
        """Find a customer by phone."""
        raise NotImplementedError()

    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        status: str | None = None,
    ) -> list[CustomerEntity]:
        """Find all customers with pagination and search."""
        raise NotImplementedError()

    @abstractmethod
    async def next_customer_code(self) -> str:
        """Generate the next customer-facing reference code."""
        raise NotImplementedError()

    @abstractmethod
    async def count_customers(self, search: str | None = None) -> int:
        """Count total customers."""
        raise NotImplementedError()
