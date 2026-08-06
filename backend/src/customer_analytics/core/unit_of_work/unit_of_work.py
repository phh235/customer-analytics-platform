"""Base unit of work interface — Abstract base for transaction management."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseUnitOfWork(ABC):
    """Abstract base unit of work interface.

    Manages transactions and ensures consistency across multiple operations.
    """

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        raise NotImplementedError()

    async def __aenter__(self) -> BaseUnitOfWork:
        return self

    async def __aexit__(
        self, exc_type: type, exc_val: Exception, exc_tb: Any
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
