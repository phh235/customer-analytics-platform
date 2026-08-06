"""User repository interface — Abstract base for user data access."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.core.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    """User repository interface — Defines user data access operations."""

    @abstractmethod
    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find a user by email."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_id(self, id_: str) -> UserEntity | None:
        """Find a user by ID."""
        raise NotImplementedError()

    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[UserEntity]:
        """Find all users with pagination and search."""
        raise NotImplementedError()

    @abstractmethod
    async def count_users(self, search: str | None = None) -> int:
        """Count total users."""
        raise NotImplementedError()

    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> list[str]:
        """Get list of permission codes for a user.

        Args:
            user_id: User's UUID.

        Returns:
            List of permission codes (e.g., ["users:create", "analytics:read"]).
        """
        raise NotImplementedError()
