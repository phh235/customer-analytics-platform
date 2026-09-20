"""Read-only EXPLAIN and execution guard for validated analytics SQL."""

from __future__ import annotations

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.config import Settings
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.sql_safety import (
    ValidatedQuery,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


@dataclass(frozen=True)
class QueryExecution:
    """Safe query result and execution metadata."""

    rows: list[dict[str, Any]]
    execution_time_ms: int
    estimated_cost: float


class AnalyticsQueryExecutor:
    """Execute only validated SQL inside a read-only transaction."""

    def __init__(self, config: Settings) -> None:
        self._config = config

    async def execute(
        self,
        session: AsyncSession,
        query: ValidatedQuery,
    ) -> QueryExecution:
        """EXPLAIN and execute a validated query with hard server limits."""
        await session.execute(text("SET TRANSACTION READ ONLY"))
        timeout = self._config.AI_ANALYTICS_STATEMENT_TIMEOUT_MS
        await session.execute(text(f"SET LOCAL statement_timeout = '{timeout}ms'"))

        explain_result = await session.execute(
            text(f"EXPLAIN (FORMAT JSON) {query.sql}")
        )
        estimated_cost = _extract_total_cost(explain_result.scalar_one_or_none())
        if estimated_cost > self._config.AI_ANALYTICS_MAX_QUERY_COST:
            raise AppException(
                ErrorCode.ANALYTICS_QUERY_REJECTED,
                message="Query estimated cost exceeds the configured limit.",
            )

        started = time.perf_counter()
        result = await session.execute(text(query.sql))
        rows = [_json_safe(dict(row)) for row in result.mappings().all()]
        execution_time_ms = round((time.perf_counter() - started) * 1000)
        return QueryExecution(rows, execution_time_ms, estimated_cost)


def _extract_total_cost(payload: Any) -> float:
    """Read PostgreSQL's top-level Total Cost from EXPLAIN JSON."""
    if not isinstance(payload, list) or not payload:
        return 0.0
    plan = payload[0].get("Plan") if isinstance(payload[0], dict) else None
    if not isinstance(plan, dict):
        return 0.0
    try:
        return float(plan.get("Total Cost", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    return value
