"""Persistence adapter for controlled analytics audit records."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.config import Settings
from customer_analytics.app.features.analytics.infrastructure.models.analytics_query_audit import (
    AnalyticsQueryAuditModel,
)


class AnalyticsAuditRepository:
    """Write-only audit repository backed by the application database."""

    def __init__(self, session: AsyncSession, config: Settings) -> None:
        self._session = session
        self._config = config

    async def record(
        self,
        *,
        query_id: uuid.UUID,
        user_id: uuid.UUID | None,
        question: str,
        status: str,
        generated_sql: str | None = None,
        validated_sql: str | None = None,
        rejection_reason: str | None = None,
        row_count: int | None = None,
        execution_time_ms: int | None = None,
    ) -> None:
        self._session.add(
            AnalyticsQueryAuditModel(
                id=query_id,
                user_id=user_id,
                question=question,
                generated_sql=generated_sql,
                validated_sql=validated_sql,
                status=status,
                rejection_reason=rejection_reason,
                row_count=row_count,
                execution_time_ms=execution_time_ms,
                model=self._config.GROQ_MODEL,
                created_at=datetime.now(UTC),
            )
        )
        await self._session.commit()
