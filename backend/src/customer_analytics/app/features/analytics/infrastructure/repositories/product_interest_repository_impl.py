"""PostgreSQL queries for product-interest analytics."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.domain.repositories.product_interest_repository import (
    ProductInterestRepository,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def _trend_metrics(current_views: int, previous_views: int) -> tuple[float | None, str]:
    """Calculate growth and the agreed product-interest trend bucket."""
    if previous_views == 0:
        return None, "NEW_TREND" if current_views > 0 else "STABLE"

    growth_percent = round(
        (current_views - previous_views) / previous_views * 100,
        2,
    )
    if growth_percent >= 50:
        status = "STRONG_TRENDING"
    elif growth_percent >= 20:
        status = "TRENDING"
    elif growth_percent <= -20:
        status = "DECLINING"
    else:
        status = "STABLE"
    return growth_percent, status


class ProductInterestRepositoryImpl(ProductInterestRepository):
    """Read product-view events with the authenticated customer scope applied."""

    def __init__(
        self, session: AsyncSession, current_user: UserEntity | None = None
    ) -> None:
        self._session = session
        self._current_user = current_user

    def _scope_filter(self, alias: str = "c") -> tuple[str, dict[str, Any]]:
        """Restrict staff users to their assigned customers."""
        user = self._current_user
        if user is None or user.role_code == "ADMIN":
            return "", {}
        if not user.id_:
            return f" AND {alias}.id IS NULL", {}
        return (
            f" AND {alias}.assigned_user_id = CAST(:scope_user_id AS uuid)",
            {"scope_user_id": user.id_},
        )

    @staticmethod
    def _utc_window(from_date: date, to_date: date) -> tuple[datetime, datetime]:
        """Interpret API dates in the configured business timezone."""
        timezone = ZoneInfo(settings.ANALYSIS_TIMEZONE)
        start = datetime.combine(from_date, time.min, tzinfo=timezone)
        end = datetime.combine(to_date + timedelta(days=1), time.min, tzinfo=timezone)
        return start.astimezone(UTC), end.astimezone(UTC)

    async def _product(self, product_id: str) -> dict[str, Any]:
        """Resolve UUID, product code, or source product ID to product metadata."""
        try:
            identifier = uuid.UUID(product_id)
        except ValueError:
            identifier = None

        if identifier is not None:
            condition = "p.id = CAST(:product_uuid AS uuid)"
            params: dict[str, Any] = {"product_uuid": str(identifier)}
        else:
            condition = (
                "(p.product_code = :product_ref OR p.source_product_id = :product_ref)"
            )
            params = {"product_ref": product_id}

        result = await self._session.execute(
            text(
                f"""
                SELECT p.id::text AS product_id, p.product_code, p.name
                FROM products p
                WHERE {condition} AND p.is_deleted = false
                """
            ),
            params,
        )
        product = result.mappings().first()
        if product is None:
            raise AppException(ErrorCode.NOT_FOUND, "Product not found")
        return dict(product)

    async def get_product_summary(
        self, product_id: str, from_date: date, to_date: date
    ) -> dict[str, Any]:
        """Count product-view events and distinct viewers."""
        product = await self._product(product_id)
        from_utc, to_utc = self._utc_window(from_date, to_date)
        scope_sql, scope_params = self._scope_filter()
        result = await self._session.execute(
            text(
                f"""
                SELECT COUNT(*)::int AS total_views,
                       COUNT(DISTINCT ci.customer_id)::int AS unique_viewers
                FROM customer_interactions ci
                JOIN customers c ON c.id = ci.customer_id
                WHERE ci.product_id = CAST(:product_id AS uuid)
                  AND ci.interaction_type = 'product_view'
                  AND ci.interaction_timestamp >= :from_utc
                  AND ci.interaction_timestamp < :to_utc
                  AND c.is_deleted = false
                  {scope_sql}
                """
            ),
            {
                "product_id": product["product_id"],
                "from_utc": from_utc,
                "to_utc": to_utc,
                **scope_params,
            },
        )
        summary = dict(result.mappings().one())
        return {**product, **summary}

    async def get_product_viewers(
        self, product_id: str, from_date: date, to_date: date, limit: int
    ) -> list[dict[str, Any]]:
        """Rank customers by repeated views of one product."""
        product = await self._product(product_id)
        from_utc, to_utc = self._utc_window(from_date, to_date)
        scope_sql, scope_params = self._scope_filter()
        result = await self._session.execute(
            text(
                f"""
                SELECT c.id::text AS customer_id,
                       c.customer_code,
                       c.name AS customer_name,
                       COUNT(*)::int AS views,
                       MAX(ci.interaction_timestamp) AS last_view_at
                FROM customer_interactions ci
                JOIN customers c ON c.id = ci.customer_id
                WHERE ci.product_id = CAST(:product_id AS uuid)
                  AND ci.interaction_type = 'product_view'
                  AND ci.interaction_timestamp >= :from_utc
                  AND ci.interaction_timestamp < :to_utc
                  AND c.is_deleted = false
                  {scope_sql}
                GROUP BY c.id, c.customer_code, c.name
                ORDER BY views DESC, last_view_at DESC, c.id
                LIMIT :limit
                """
            ),
            {
                "product_id": product["product_id"],
                "from_utc": from_utc,
                "to_utc": to_utc,
                "limit": limit,
                **scope_params,
            },
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_product_trend(
        self,
        product_id: str,
        from_date: date,
        to_date: date,
        group_by: str,
    ) -> list[dict[str, Any]]:
        """Aggregate product-view events by day, week, or month."""
        product = await self._product(product_id)
        from_utc, to_utc = self._utc_window(from_date, to_date)
        scope_sql, scope_params = self._scope_filter()
        bucket_expression = {
            "day": "(ci.interaction_timestamp AT TIME ZONE :timezone)::date",
            "week": (
                "date_trunc('week', "
                "ci.interaction_timestamp AT TIME ZONE :timezone)::date"
            ),
            "month": (
                "date_trunc('month', "
                "ci.interaction_timestamp AT TIME ZONE :timezone)::date"
            ),
        }[group_by]
        result = await self._session.execute(
            text(
                f"""
                SELECT {bucket_expression} AS period_start, COUNT(*)::int AS views
                FROM customer_interactions ci
                JOIN customers c ON c.id = ci.customer_id
                WHERE ci.product_id = CAST(:product_id AS uuid)
                  AND ci.interaction_type = 'product_view'
                  AND ci.interaction_timestamp >= :from_utc
                  AND ci.interaction_timestamp < :to_utc
                  AND c.is_deleted = false
                  {scope_sql}
                GROUP BY period_start
                ORDER BY period_start
                """
            ),
            {
                "product_id": product["product_id"],
                "from_utc": from_utc,
                "to_utc": to_utc,
                "timezone": settings.ANALYSIS_TIMEZONE,
                **scope_params,
            },
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_trending_products(
        self, to_date: date, period_days: int, limit: int
    ) -> list[dict[str, Any]]:
        """Compare equal current and previous product-view periods."""
        timezone = ZoneInfo(settings.ANALYSIS_TIMEZONE)
        current_start_date = to_date - timedelta(days=period_days - 1)
        previous_start_date = to_date - timedelta(days=(period_days * 2) - 1)
        current_start = datetime.combine(current_start_date, time.min, tzinfo=timezone)
        current_end = datetime.combine(
            to_date + timedelta(days=1), time.min, tzinfo=timezone
        )
        previous_start = datetime.combine(
            previous_start_date, time.min, tzinfo=timezone
        )
        scope_sql, scope_params = self._scope_filter()
        result = await self._session.execute(
            text(
                f"""
                SELECT p.id::text AS product_id,
                       p.product_code,
                       p.name AS product_name,
                       COUNT(*) FILTER (
                           WHERE ci.interaction_timestamp >= :current_start
                       )::int AS current_period_views,
                       COUNT(*) FILTER (
                           WHERE ci.interaction_timestamp < :current_start
                       )::int AS previous_period_views
                FROM products p
                JOIN customer_interactions ci ON ci.product_id = p.id
                JOIN customers c ON c.id = ci.customer_id
                WHERE p.is_deleted = false
                  AND ci.interaction_type = 'product_view'
                  AND ci.interaction_timestamp >= :previous_start
                  AND ci.interaction_timestamp < :current_end
                  AND c.is_deleted = false
                  {scope_sql}
                GROUP BY p.id, p.product_code, p.name
                ORDER BY current_period_views DESC, previous_period_views ASC, p.id
                LIMIT :limit
                """
            ),
            {
                "previous_start": previous_start.astimezone(UTC),
                "current_start": current_start.astimezone(UTC),
                "current_end": current_end.astimezone(UTC),
                "limit": limit,
                **scope_params,
            },
        )
        records: list[dict[str, Any]] = []
        for row in result.mappings().all():
            record = dict(row)
            current = int(record["current_period_views"])
            previous = int(record["previous_period_views"])
            growth_percent, status = _trend_metrics(current, previous)
            record["growth_percent"] = growth_percent
            record["trend_status"] = status
            records.append(record)
        records.sort(
            key=lambda item: (
                item["growth_percent"] is None,
                item["growth_percent"] if item["growth_percent"] is not None else 0,
                item["current_period_views"],
            ),
            reverse=True,
        )
        return records
