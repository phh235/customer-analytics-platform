"""SQLAlchemy implementation for password reset challenges."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.identity.domain.entities.password_reset_challenge import (  # noqa: E501
    PasswordResetChallenge,
)
from customer_analytics.app.features.identity.domain.repositories.password_reset_repository import (  # noqa: E501
    PasswordResetRepository,
)
from customer_analytics.app.features.identity.infrastructure.models.password_reset_challenge import (  # noqa: E501
    PasswordResetChallengeModel,
)


class PasswordResetRepositoryImpl(PasswordResetRepository):
    """Persist password reset challenges in PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: PasswordResetChallengeModel) -> PasswordResetChallenge:
        """Convert a persistence model to a domain entity."""
        return PasswordResetChallenge(
            id_=str(model.id),
            email=model.email,
            user_id=str(model.user_id),
            otp_hash=model.otp_hash,
            expires_at=model.expires_at,
            attempt_count=model.attempt_count,
            verified_at=model.verified_at,
            reset_token_hash=model.reset_token_hash,
            reset_token_expires_at=model.reset_token_expires_at,
            consumed_at=model.consumed_at,
            requested_ip=model.requested_ip,
            user_agent=model.user_agent,
            created_at=model.created_at,
        )

    async def invalidate_active(self, email: str) -> None:
        """Invalidate all previous unconsumed challenges for an email."""
        await self._session.execute(
            update(PasswordResetChallengeModel)
            .where(
                PasswordResetChallengeModel.email == email,
                PasswordResetChallengeModel.consumed_at.is_(None),
            )
            .values(consumed_at=datetime.now(UTC))
        )
        await self._session.flush()

    async def create(self, challenge: PasswordResetChallenge) -> None:
        """Persist a new password reset challenge."""
        self._session.add(
            PasswordResetChallengeModel(
                id=uuid.UUID(challenge.id_),
                email=challenge.email,
                user_id=uuid.UUID(challenge.user_id),
                otp_hash=challenge.otp_hash,
                expires_at=challenge.expires_at,
                attempt_count=challenge.attempt_count,
                requested_ip=challenge.requested_ip,
                user_agent=challenge.user_agent,
            )
        )
        await self._session.flush()

    async def has_recent_request(self, email: str, since: datetime) -> bool:
        """Check the per-email resend cooldown."""
        result = await self._session.execute(
            select(PasswordResetChallengeModel.id)
            .where(
                PasswordResetChallengeModel.email == email,
                PasswordResetChallengeModel.created_at >= since,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def find_active_by_email(
        self, email: str, now: datetime
    ) -> PasswordResetChallenge | None:
        """Find the newest unexpired, unverified challenge."""
        result = await self._session.execute(
            select(PasswordResetChallengeModel)
            .where(
                PasswordResetChallengeModel.email == email,
                PasswordResetChallengeModel.consumed_at.is_(None),
                PasswordResetChallengeModel.verified_at.is_(None),
                PasswordResetChallengeModel.expires_at > now,
                PasswordResetChallengeModel.attempt_count < 5,
            )
            .order_by(PasswordResetChallengeModel.created_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def increment_attempts(self, challenge_id: str) -> None:
        """Increment failed OTP attempts."""
        await self._session.execute(
            update(PasswordResetChallengeModel)
            .where(PasswordResetChallengeModel.id == uuid.UUID(challenge_id))
            .values(attempt_count=PasswordResetChallengeModel.attempt_count + 1)
        )
        await self._session.flush()

    async def mark_verified(
        self,
        challenge_id: str,
        reset_token_hash: str,
        reset_token_expires_at: datetime,
        verified_at: datetime,
    ) -> None:
        """Store the short-lived reset token hash."""
        await self._session.execute(
            update(PasswordResetChallengeModel)
            .where(PasswordResetChallengeModel.id == uuid.UUID(challenge_id))
            .values(
                verified_at=verified_at,
                reset_token_hash=reset_token_hash,
                reset_token_expires_at=reset_token_expires_at,
            )
        )
        await self._session.flush()

    async def find_by_reset_token(
        self, reset_token_hash: str, now: datetime
    ) -> PasswordResetChallenge | None:
        """Find a valid, verified and unconsumed reset token."""
        result = await self._session.execute(
            select(PasswordResetChallengeModel).where(
                PasswordResetChallengeModel.reset_token_hash == reset_token_hash,
                PasswordResetChallengeModel.verified_at.is_not(None),
                PasswordResetChallengeModel.consumed_at.is_(None),
                PasswordResetChallengeModel.reset_token_expires_at > now,
            )
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def consume(self, challenge_id: str, consumed_at: datetime) -> None:
        """Consume a reset challenge."""
        await self._session.execute(
            update(PasswordResetChallengeModel)
            .where(PasswordResetChallengeModel.id == uuid.UUID(challenge_id))
            .values(consumed_at=consumed_at)
        )
        await self._session.flush()
