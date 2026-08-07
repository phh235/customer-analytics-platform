"""Refresh token repository interface."""

from __future__ import annotations

import uuid
from abc import abstractmethod, ABC
from datetime import datetime


class RefreshTokenRepository(ABC):
    """Refresh token repository interface."""

    @abstractmethod
    async def save(
        self,
        token_hash: str,
        user_id: uuid.UUID,
        family_id: str,
        expires_at: datetime,
        created_ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Save a new refresh token."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> dict | None:
        """Find a refresh token by its hash."""
        raise NotImplementedError()

    @abstractmethod
    async def revoke_by_token_hash(self, token_hash: str) -> None:
        """Revoke a refresh token by its hash."""
        raise NotImplementedError()

    @abstractmethod
    async def revoke_all_by_family(self, family_id: str) -> int:
        """Revoke all refresh tokens in a family. Returns count of revoked tokens."""
        raise NotImplementedError()

    @abstractmethod
    async def revoke_all_by_user(self, user_id: uuid.UUID) -> int:
        """Revoke all refresh tokens for a user. Returns count of revoked tokens."""
        raise NotImplementedError()

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete expired and revoked refresh tokens."""
        raise NotImplementedError()

    @abstractmethod
    async def find_active_by_user(self, user_id: uuid.UUID) -> list[dict]:
        """Find all active (non-revoked, non-expired) refresh tokens for a user."""
        raise NotImplementedError()
