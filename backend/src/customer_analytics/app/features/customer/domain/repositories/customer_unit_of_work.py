"""Customer Unit of Work interface."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.customer.domain.repositories.customer_repository import (
    CustomerRepository,
)


class CustomerUnitOfWork:
    """Customer Unit of Work interface."""

    repository: CustomerRepository

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError()
