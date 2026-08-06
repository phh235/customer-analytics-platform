"""Base repository interface — Abstract base for all repositories."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseRepository[T](ABC):
    """Abstract base repository interface.

    Defines common CRUD operations for all repositories.
    """

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_id(self, id_: str) -> T | None:
        """Find an entity by ID."""
        raise NotImplementedError()

    @abstractmethod
    async def find_all(self) -> list[T]:
        """Find all entities."""
        raise NotImplementedError()

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id_: str) -> None:
        """Delete an entity by ID."""
        raise NotImplementedError()
