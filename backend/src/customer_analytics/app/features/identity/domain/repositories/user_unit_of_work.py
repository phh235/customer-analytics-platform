"""User unit of work interface — Abstract base for transaction management."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.domain.repositories.user_repository import (  # noqa: E501
    UserRepository,
)
from customer_analytics.core.unit_of_work.unit_of_work import BaseUnitOfWork


class UserUnitOfWork(BaseUnitOfWork):
    """User unit of work interface — Manages user transactions."""

    repository: UserRepository

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError()
