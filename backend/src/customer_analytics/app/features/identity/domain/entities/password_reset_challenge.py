"""Password reset challenge domain entity."""

from __future__ import annotations

import uuid
from datetime import datetime


class PasswordResetChallenge:
    """Persisted state for one password reset OTP flow."""

    def __init__(
        self,
        id_: str | None,
        email: str,
        user_id: str,
        otp_hash: str,
        expires_at: datetime,
        attempt_count: int = 0,
        verified_at: datetime | None = None,
        reset_token_hash: str | None = None,
        reset_token_expires_at: datetime | None = None,
        consumed_at: datetime | None = None,
        requested_ip: str | None = None,
        user_agent: str | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.id_ = id_ or str(uuid.uuid4())
        self.email = email
        self.user_id = user_id
        self.otp_hash = otp_hash
        self.expires_at = expires_at
        self.attempt_count = attempt_count
        self.verified_at = verified_at
        self.reset_token_hash = reset_token_hash
        self.reset_token_expires_at = reset_token_expires_at
        self.consumed_at = consumed_at
        self.requested_ip = requested_ip
        self.user_agent = user_agent
        self.created_at = created_at

    @property
    def is_consumed(self) -> bool:
        """Return whether this challenge has already completed a reset."""
        return self.consumed_at is not None

    @property
    def is_verified(self) -> bool:
        """Return whether the OTP has been verified."""
        return self.verified_at is not None and self.reset_token_hash is not None
