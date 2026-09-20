"""Verify-password-reset-OTP use case."""

from __future__ import annotations

import hmac
from datetime import UTC, datetime, timedelta

from customer_analytics.app.features.identity.application.password_reset_tokens import (
    generate_reset_token,
    hash_reset_secret,
)
from customer_analytics.app.features.identity.domain.repositories.password_reset_repository import (
    PasswordResetRepository,
)


class VerifyPasswordResetUseCaseImpl:
    """Verify an OTP and issue a short-lived reset token."""

    def __init__(self, reset_repository: PasswordResetRepository) -> None:
        self.reset_repository = reset_repository

    async def __call__(self, email: str, otp: str) -> str | None:
        """Return a reset token, or None after recording an invalid OTP attempt."""
        now = datetime.now(UTC)
        challenge = await self.reset_repository.find_active_by_email(email.lower(), now)
        if challenge is None:
            return None

        provided_hash = hash_reset_secret(otp)
        if not hmac.compare_digest(provided_hash, challenge.otp_hash):
            await self.reset_repository.increment_attempts(challenge.id_)
            return None

        reset_token = generate_reset_token()
        await self.reset_repository.mark_verified(
            challenge_id=challenge.id_,
            reset_token_hash=hash_reset_secret(reset_token),
            reset_token_expires_at=now + timedelta(minutes=10),
            verified_at=now,
        )
        return reset_token
