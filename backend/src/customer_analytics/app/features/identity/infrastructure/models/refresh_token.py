"""Refresh token persistence model."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    pass


class RefreshTokenModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Refresh token storage for rotation and revocation."""

    __tablename__ = "refresh_tokens"

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA-256 hash of refresh token",
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    family_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Token family ID (one per login session)",
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_ip: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Client IP for audit",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent for audit",
    )

    __table_args__ = (
        Index("ix_refresh_tokens_user_family", "user_id", "family_id"),
    )

    @property
    def is_revoked(self) -> bool:
        """Check if token has been revoked."""
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.now(UTC) > self.expires_at

    def __repr__(self) -> str:
        return (
            f"<RefreshTokenModel(id={self.id}, user_id='{self.user_id}', "
            f"family_id='{self.family_id}')>"
        )
