"""Refresh token repository interface."""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from typing import Any


class RefreshTokenRepository:
    """Refresh token repository interface."""

    @abstractmethod
    async def save(
        self,
        token_hash: str,
        user_id: str,
        family_id: str,
        expires_at: datetime,
        created_ip: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        """Save a new refresh token."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> dict[str, Any] | None:
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
    async def revoke_all_by_user(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user. Returns count of revoked tokens."""
        raise NotImplementedError()

    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete expired and revoked refresh tokens."""
        raise NotImplementedError()

    @abstractmethod
    async def find_active_by_user(self, user_id: str) -> list[dict[str, Any]]:
        """Find all active (non-revoked, non-expired) refresh tokens for a user."""
        raise NotImplementedError()
