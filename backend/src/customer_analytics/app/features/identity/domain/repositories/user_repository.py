"""User repository interface — Abstract base for user data access."""

from __future__ import annotations

import uuid
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
    async def find_by_google_id(self, google_id: str) -> UserEntity | None:
        """Find a user by Google ID."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_email_with_permissions(
        self, email: str
    ) -> tuple[UserEntity, list[str]] | None:
        """Find a user and their permissions by email."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_id(self, id_: str) -> UserEntity | None:
        """Find a user by ID."""
        raise NotImplementedError()

    @abstractmethod
    async def find_role_id_by_code(self, role_code: str) -> uuid.UUID | None:
        """Find a role ID by its stable role code."""
        raise NotImplementedError()

    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        role_code: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[UserEntity]:
        """Find users with pagination, filters, and deterministic ordering."""
        raise NotImplementedError()

    @abstractmethod
    async def count_users(
        self,
        search: str | None = None,
        role_code: str | None = None,
        status: str | None = None,
    ) -> int:
        """Count users matching the supplied filters."""
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

    @abstractmethod
    async def get_users_permissions_batch(
        self, user_ids: list[str]
    ) -> dict[str, list[str]]:
        """Get permissions for multiple users in one query."""
        raise NotImplementedError()
