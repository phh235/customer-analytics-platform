"""Refresh token repository implementation — SQLAlchemy."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.identity.domain.repositories.refresh_token_repository import (  # noqa: E501
    RefreshTokenRepository,
)
from customer_analytics.app.features.identity.infrastructure.models.refresh_token import (  # noqa: E501
    RefreshTokenModel,
)


def _now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


class RefreshTokenRepositoryImpl(RefreshTokenRepository):
    """Refresh token repository using SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
        model = RefreshTokenModel(
            token_hash=token_hash,
            user_id=user_id,
            family_id=family_id,
            expires_at=expires_at,
            created_ip=created_ip,
            user_agent=user_agent,
        )
        self._session.add(model)
        await self._session.flush()

    async def find_by_token_hash(self, token_hash: str) -> dict | None:
        """Find a refresh token by its hash."""
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return {
            "id": str(model.id),
            "token_hash": model.token_hash,
            "user_id": str(model.user_id),
            "family_id": str(model.family_id),
            "revoked_at": model.revoked_at,
            "expires_at": model.expires_at,
        }

    async def revoke_by_token_hash(self, token_hash: str) -> None:
        """Revoke a refresh token by its hash."""
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(revoked_at=_now_utc())
        )
        await self._session.flush()

    async def revoke_all_by_family(self, family_id: str) -> int:
        """Revoke all refresh tokens in a family. Returns count of revoked tokens."""
        result = await self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.family_id == family_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=_now_utc())
        )
        await self._session.flush()
        return result.rowcount  # type: ignore[return-value]

    async def revoke_all_by_user(self, user_id: uuid.UUID) -> int:
        """Revoke all refresh tokens for a user. Returns count of revoked tokens."""
        result = await self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=_now_utc())
        )
        await self._session.flush()
        return result.rowcount  # type: ignore[return-value]

    async def delete_expired(self) -> int:
        """Delete expired and revoked refresh tokens."""
        from sqlalchemy import or_

        result = await self._session.execute(
            select(RefreshTokenModel).where(
                or_(
                    RefreshTokenModel.expires_at < _now_utc(),
                    RefreshTokenModel.revoked_at.isnot(None),
                )
            )
        )
        models = result.scalars().all()
        count = len(models)
        for model in models:
            await self._session.delete(model)
        await self._session.flush()
        return count

    async def find_active_by_user(self, user_id: uuid.UUID) -> list[dict]:
        """Find all active (non-revoked, non-expired) refresh tokens for a user."""
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
                RefreshTokenModel.expires_at > _now_utc(),
            )
        )
        models = result.scalars().all()
        return [
            {
                "id": str(m.id),
                "token_hash": m.token_hash,
                "family_id": str(m.family_id),
                "expires_at": m.expires_at,
            }
            for m in models
        ]
