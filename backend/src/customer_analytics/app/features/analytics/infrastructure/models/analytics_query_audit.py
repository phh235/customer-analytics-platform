"""Audit records for controlled natural-language analytics queries."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AnalyticsQueryAuditModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persisted security and execution metadata for an AI query."""

    __tablename__ = "ai_query_audits"

    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True, index=True)
    organization_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    validated_sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model: Mapped[str] = mapped_column(String(150), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
