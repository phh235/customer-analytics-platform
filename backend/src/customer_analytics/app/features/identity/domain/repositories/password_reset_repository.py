"""Password reset challenge repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from customer_analytics.app.features.identity.domain.entities.password_reset_challenge import (
    PasswordResetChallenge,
)


class PasswordResetRepository(ABC):
    """Persistence contract for password reset OTP challenges."""

    @abstractmethod
    async def invalidate_active(self, email: str) -> None:
        """Invalidate pending challenges for an email."""
        raise NotImplementedError()

    @abstractmethod
    async def create(self, challenge: PasswordResetChallenge) -> None:
        """Persist a new reset challenge."""
        raise NotImplementedError()

    @abstractmethod
    async def has_recent_request(self, email: str, since: datetime) -> bool:
        """Return whether an email has a recent reset request."""
        raise NotImplementedError()

    @abstractmethod
    async def find_active_by_email(
        self, email: str, now: datetime
    ) -> PasswordResetChallenge | None:
        """Find the latest usable OTP challenge for an email."""
        raise NotImplementedError()

    @abstractmethod
    async def increment_attempts(self, challenge_id: str) -> None:
        """Increment failed OTP attempts."""
        raise NotImplementedError()

    @abstractmethod
    async def mark_verified(
        self,
        challenge_id: str,
        reset_token_hash: str,
        reset_token_expires_at: datetime,
        verified_at: datetime,
    ) -> None:
        """Mark OTP verified and persist the one-time reset token hash."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_reset_token(
        self, reset_token_hash: str, now: datetime
    ) -> PasswordResetChallenge | None:
        """Find a verified, unconsumed reset token."""
        raise NotImplementedError()

    @abstractmethod
    async def consume(self, challenge_id: str, consumed_at: datetime) -> None:
        """Consume a reset challenge after changing the password."""
        raise NotImplementedError()
