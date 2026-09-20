"""Raw-SQL analytics repository implementation."""

import json
import uuid
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from math import ceil
from pathlib import Path
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.application.services.purchase_model import (
    predict_purchase_probability,
)
from customer_analytics.app.features.analytics.domain.analysis_window import (
    resolve_analysis_window,
)
from customer_analytics.app.features.analytics.domain.dashboard_overview import (
    BUSINESS_TIMEZONE as DASHBOARD_TIMEZONE,
)
from customer_analytics.app.features.analytics.domain.dashboard_overview import (
    DashboardOverviewQuery,
)
from customer_analytics.app.features.analytics.domain.entities import (
    PotentialScoreEntity,
    RFMEntity,
    SegmentEntity,
)
from customer_analytics.app.features.analytics.domain.enums import (
    ScoreLevel,
    SegmentType,
)
from customer_analytics.app.features.analytics.domain.repositories import (
    AnalyticsRepository,
)
from customer_analytics.app.features.analytics.infrastructure.models.analytics_history import (
    CurrentPotentialScoreModel,
    PurchasePredictionModel,
    SegmentHistoryModel,
)
from customer_analytics.app.features.analytics.infrastructure.models.model_registry import (
    ModelLifecycleStatus,
    ModelRegistryModel,
)
from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class AnalyticsRepositoryImpl(AnalyticsRepository):
    """Analytics repository backed by PostgreSQL raw SQL queries."""

    def __init__(
        self,
        session: AsyncSession,
        current_user: UserEntity | None = None,
    ) -> None:
        self._session = session
        self._current_user = current_user

    def _scope_filter(self, alias: str = "c") -> tuple[str, dict[str, Any]]:
        """Return SQL and parameters for the authenticated customer scope."""
        user = self._current_user
        if user is None or user.role_code == "ADMIN":
            return "", {}
        if not user.id_:
            return f" AND {alias}.id IS NULL", {}
        return (
            f" AND {alias}.assigned_user_id = CAST(:scope_user_id AS uuid)",
            {"scope_user_id": user.id_},
        )

    @property
    def _valid_order_status_sql(self) -> str:
        """Return configured valid statuses in dataset and API casing."""
        values: list[str] = []
        for raw_status in settings.VALID_ORDER_STATUSES:
            for status in (raw_status, raw_status.lower()):
                if status not in values:
                    values.append(status)
        escaped = (status.replace("'", "''") for status in values)
        return ", ".join(f"'{status}'" for status in escaped)

    async def create(self, entity: RFMEntity) -> RFMEntity:
        """Analytics is computed on demand and cannot be persisted here."""
        raise AppException(
            ErrorCode.NOT_IMPLEMENTED,
            "Analytics create is not supported",
        )

    async def find_by_id(self, id_: str) -> RFMEntity | None:
        """Find analytics by customer ID via RFM calculation."""
        return await self.calculate_rfm(id_)

    async def find_all(self) -> list[RFMEntity]:
        """Find all computed RFM analytics."""
        return await self.calculate_all_rfm()

    async def update(self, entity: RFMEntity) -> RFMEntity:
        """Analytics is computed on demand and cannot be updated here."""
        raise AppException(
            ErrorCode.NOT_IMPLEMENTED,
            "Analytics update is not supported",
        )

    async def delete(self, id_: str) -> None:
        """Analytics is computed on demand and cannot be deleted here."""
        raise AppException(
            ErrorCode.NOT_IMPLEMENTED,
            "Analytics delete is not supported",
        )

    async def calculate_rfm(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> RFMEntity | None:
        """Calculate RFM metrics for a single customer."""
        rfm_entities = await self._build_rfm_entities(
            days=days, analysis_date=analysis_date
        )
        for entity in rfm_entities:
            if entity.customer_id == customer_id:
                return entity
        return None

    async def calculate_all_rfm(
        self, days: int = 365, analysis_date: date | None = None
    ) -> list[RFMEntity]:
        """Calculate RFM metrics for all customers."""
        return await self._build_rfm_entities(days=days, analysis_date=analysis_date)

    async def get_customer_segment(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> SegmentEntity | None:
        """Get segment for a single customer."""
        segments = await self.get_all_segments(days=days, analysis_date=analysis_date)
        for segment in segments:
            if segment.customer_id == customer_id:
                return segment
        return None

    async def get_all_segments(
        self,
        days: int = 365,
        rows: list[dict[str, Any]] | None = None,
        analysis_date: date | None = None,
    ) -> list[SegmentEntity]:
        """Get customer segments for all customers."""
        calculated_at = datetime.now(UTC)
        segments: list[SegmentEntity] = []

        for rfm in await self._build_rfm_entities(
            days=days, rows=rows, analysis_date=analysis_date
        ):
            score, weights, missing_components = self._potential_score_details(rfm)
            potential_level = self._potential_level(score)
            segment_type, reason = self._determine_segment(rfm, score)
            segment = SegmentEntity(
                customer_code=rfm.customer_code,
                customer_id=rfm.customer_id,
                segment_type=segment_type,
                reason=reason,
                calculated_at=calculated_at,
                potential_score=score,
                potential_level=potential_level,
                analysis_date=rfm.analysis_date,
                rfm=self._rfm_snapshot(rfm),
                score_components=self._score_components(
                    rfm, weights, missing_components
                ),
            )
            segment.name = getattr(rfm, "name", None)
            segment.customer_code = rfm.customer_code
            segments.append(segment)

        return segments

    async def get_latest_analysis_date(self) -> date | None:
        """Return the newest completed analysis-run date, if one exists."""
        result = await self._session.execute(
            text(
                """
                SELECT MAX(analysis_date) AS analysis_date
                FROM analysis_runs
                WHERE status IN ('COMPLETED', 'SUCCESS')
                """
            )
        )
        row = result.mappings().first()
        return row["analysis_date"] if row and row["analysis_date"] else None

    async def get_potential_score(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> PotentialScoreEntity | None:
        """Get potential score for a single customer."""
        scores = await self.get_all_potential_scores(
            days=days, analysis_date=analysis_date
        )
        for score in scores:
            if score.customer_id == customer_id:
                return score
        return None

    async def get_all_potential_scores(
        self,
        days: int = 365,
        rows: list[dict[str, Any]] | None = None,
        analysis_date: date | None = None,
    ) -> list[PotentialScoreEntity]:
        """Get potential scores for all customers."""
        calculated_at = datetime.now(UTC)
        rows = (
            rows
            if rows is not None
            else await self._fetch_rfm_rows(days=days, analysis_date=analysis_date)
        )
        rfm_entities = await self._build_rfm_entities(
            days=days, rows=rows, analysis_date=analysis_date
        )
        scores: list[PotentialScoreEntity] = []

        for rfm in rfm_entities:
            score, weights, missing_components = self._potential_score_details(rfm)
            components = self._score_components(rfm, weights, missing_components)
            level = self._potential_level(score)

            potential_score = PotentialScoreEntity(
                customer_id=rfm.customer_id,
                customer_code=rfm.customer_code,
                analysis_date=rfm.analysis_date,
                score=score,
                level=level,
                components=components,
                calculated_at=calculated_at,
            )
            potential_score.name = getattr(rfm, "name", None)
            potential_score.customer_code = rfm.customer_code
            scores.append(potential_score)

        scores.sort(
            key=lambda item: (
                item.score is not None,
                item.score or -1,
            ),
            reverse=True,
        )
        return scores

    async def get_customer_360(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> dict[str, Any] | None:
        """Build customer 360 payload from customer, order, and product data."""
        scope_sql, scope_params = self._scope_filter()
        customer_query = text(
            f"""
            SELECT
                c.id::text AS customer_id,
                c.customer_code,
                c.name,
                c.email,
                c.phone,
                c.address,
                c.status,
                c.gender,
                c.date_of_birth,
                c.region,
                c.customer_since,
                c.total_orders,
                c.total_spent,
                c.avg_order_value,
                c.last_purchase_date,
                c.created_at,
                c.updated_at
            FROM customers c
            WHERE c.id = CAST(:customer_id AS uuid)
              {scope_sql}
            """
        )
        customer_result = await self._session.execute(
            customer_query,
            {"customer_id": customer_id, **scope_params},
        )
        customer = customer_result.mappings().one_or_none()
        if customer is None:
            return None

        rfm = await self.calculate_rfm(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        segment = await self.get_customer_segment(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        potential_score = await self.get_potential_score(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        behavior = await self.get_behavior_metrics(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        try:
            prediction = await self.get_customer_prediction(
                customer_id=customer_id,
                days=days,
                analysis_date=analysis_date,
            )
        except AppException as exc:
            if exc.error_code != ErrorCode.MODEL_NOT_AVAILABLE:
                raise
            prediction = None

        top_products_query = text(
            f"""
            SELECT
                p.id::text AS product_id,
                p.name,
                p.category,
                SUM(oi.quantity)::int AS total_quantity,
                COALESCE(SUM(oi.subtotal), 0) AS total_revenue
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            JOIN products p ON p.id = oi.product_id
            WHERE o.customer_id = CAST(:customer_id AS uuid)
              AND o.status IN ({self._valid_order_status_sql})
            GROUP BY p.id, p.name, p.category
            ORDER BY total_quantity DESC, total_revenue DESC
            LIMIT 5
            """
        )
        top_products_result = await self._session.execute(
            top_products_query, {"customer_id": customer_id}
        )
        top_products = [
            {
                "product_id": row["product_id"],
                "name": row["name"],
                "category": row["category"],
                "total_quantity": row["total_quantity"],
                "total_revenue": Decimal(str(row["total_revenue"])),
            }
            for row in top_products_result.mappings().all()
        ]

        recent_orders_query = text(
            f"""
            SELECT
                o.id::text AS order_id,
                o.order_number,
                o.order_date,
                o.total_amount,
                o.refund_amount,
                o.net_amount,
                o.status,
                o.channel
            FROM orders o
            WHERE o.customer_id = CAST(:customer_id AS uuid)
              AND o.status IN ({self._valid_order_status_sql})
            ORDER BY o.order_date DESC
            LIMIT 10
            """
        )
        recent_orders_result = await self._session.execute(
            recent_orders_query, {"customer_id": customer_id}
        )
        recent_orders = [
            {
                "order_id": row["order_id"],
                "order_number": row["order_number"],
                "order_date": row["order_date"],
                "total_amount": Decimal(str(row["total_amount"])),
                "refund_amount": Decimal(str(row["refund_amount"])),
                "net_amount": Decimal(str(row["net_amount"])),
                "status": row["status"],
                "channel": row["channel"],
            }
            for row in recent_orders_result.mappings().all()
        ]

        return {
            "customer_id": customer["customer_id"],
            "customer_code": customer.get("customer_code"),
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "address": customer["address"],
            "status": customer["status"],
            "gender": customer["gender"],
            "date_of_birth": customer["date_of_birth"],
            "region": customer["region"],
            "customer_since": customer["customer_since"],
            "total_orders": (
                behavior["frequency"]
                if behavior is not None
                else customer["total_orders"]
            ),
            "total_spent": (
                behavior["monetary"]
                if behavior is not None
                else Decimal(str(customer["total_spent"]))
            ),
            "avg_order_value": (
                behavior["aov"]
                if behavior is not None
                else Decimal(str(customer["avg_order_value"]))
            ),
            "last_purchase_date": customer["last_purchase_date"],
            "created_at": customer["created_at"],
            "updated_at": customer["updated_at"],
            "rfm": rfm.to_dict() if rfm else None,
            "behavior": behavior,
            "segment": segment.to_dict() if segment else None,
            "potential_score": potential_score.to_dict() if potential_score else None,
            "prediction": prediction,
            "top_products": top_products,
            "recent_orders": recent_orders,
        }

    async def get_behavior_metrics(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> dict[str, Any] | None:
        """Calculate purchase behavior metrics for a customer."""
        scope_sql, scope_params = self._scope_filter()
        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        query = text(
            f"""
            SELECT
                (
                    SELECT c.customer_code
                    FROM customers c
                    WHERE c.id = CAST(:customer_id AS uuid)
                      {scope_sql}
                ) AS customer_code,
                COUNT(DISTINCT o.id)::int AS frequency,
                COALESCE(SUM(o.net_amount), 0) AS monetary,
                MAX(o.order_date) AS last_purchase_date,
                MIN(o.order_date) AS first_purchase_date,
                COUNT(DISTINCT o.channel)::int AS channel_count,
                COALESCE(
                    (
                        SELECT COUNT(DISTINCT oi.product_id)::int
                        FROM orders product_orders
                        JOIN order_items oi ON oi.order_id = product_orders.id
                        WHERE product_orders.customer_id = CAST(:customer_id AS uuid)
                          AND product_orders.status IN (
                              {self._valid_order_status_sql}
                          )
                          AND product_orders.order_date >= :from_utc
                          AND product_orders.order_date < :to_utc
                    ),
                    0
                ) AS product_diversity,
                (
                    SELECT AVG(r.score)
                    FROM reviews r
                    WHERE r.customer_id = CAST(:customer_id AS uuid)
                ) AS review_score,
                COALESCE(
                    (
                        SELECT COALESCE(
                            SUM(COALESCE(ci.interaction_value, 0)),
                            0
                        )
                        FROM customer_interactions ci
                        WHERE ci.customer_id = CAST(:customer_id AS uuid)
                    ),
                    0
                ) AS interaction_score
            FROM orders o
            WHERE o.customer_id = CAST(:customer_id AS uuid)
              AND o.status IN ({self._valid_order_status_sql})
              AND o.order_date >= :from_utc
              AND EXISTS (
                  SELECT 1
                  FROM customers c
                  WHERE c.id = o.customer_id
                    {scope_sql}
              )
              AND o.order_date < :to_utc
            """
        )
        params = {
            "customer_id": customer_id,
            "from_utc": window.from_utc,
            "to_utc": window.to_utc,
            **scope_params,
        }
        row = (await self._session.execute(query, params)).mappings().one_or_none()
        if row is None:
            return None

        dates_query = text(
            f"""
            SELECT o.order_date
            FROM orders o
            WHERE o.customer_id = CAST(:customer_id AS uuid)
              AND o.status IN ({self._valid_order_status_sql})
              AND o.order_date >= :from_utc
              AND o.order_date < :to_utc
              AND EXISTS (
                  SELECT 1
                  FROM customers c
                  WHERE c.id = o.customer_id
                    {scope_sql}
              )
            ORDER BY o.order_date
            """
        )
        dates = [
            item["order_date"]
            for item in (await self._session.execute(dates_query, params))
            .mappings()
            .all()
        ]
        cycles = [
            (later - earlier).total_seconds() / 86400
            for earlier, later in zip(dates, dates[1:], strict=False)
        ]
        frequency = int(row["frequency"] or 0)
        monetary = Decimal(str(row["monetary"] or 0))
        return {
            "customer_id": customer_id,
            "customer_code": row.get("customer_code"),
            "recency_days": (
                (window.to_utc - row["last_purchase_date"]).total_seconds() / 86400
                if row["last_purchase_date"]
                else None
            ),
            "frequency": frequency,
            "monetary": monetary,
            "aov": monetary / frequency if frequency else Decimal("0"),
            "purchase_cycle_days": sum(cycles) / len(cycles) if cycles else None,
            "product_preference": await self._top_product_category(
                customer_id, days, analysis_date
            ),
            "product_diversity": int(row["product_diversity"] or 0),
            "review_score": (
                float(row["review_score"]) if row["review_score"] is not None else None
            ),
            "trend": await self._trend_label(customer_id, days, analysis_date),
            "channel_count": int(row["channel_count"] or 0),
            "interaction_score": float(row["interaction_score"] or 0),
        }

    async def _top_product_category(
        self,
        customer_id: str,
        days: int,
        analysis_date: date | None = None,
    ) -> str | None:
        scope_sql, scope_params = self._scope_filter()
        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        result = await self._session.execute(
            text(
                f"""
                SELECT p.category
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.id
                JOIN products p ON p.id = oi.product_id
                JOIN customers c ON c.id = o.customer_id
                WHERE o.customer_id = CAST(:customer_id AS uuid)
                  {scope_sql}
                  AND o.status IN ({self._valid_order_status_sql})
                  AND o.order_date >= :from_utc
                  AND o.order_date < :to_utc
                GROUP BY p.category
                ORDER BY SUM(oi.quantity) DESC
                LIMIT 1
                """
            ),
            {
                "customer_id": customer_id,
                "from_utc": window.from_utc,
                "to_utc": window.to_utc,
                **scope_params,
            },
        )
        row = result.mappings().first()
        return row["category"] if row else None

    async def _trend_label(
        self,
        customer_id: str,
        days: int,
        analysis_date: date | None = None,
    ) -> str:
        recent_days = max(30, min(days // 4, 90))
        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        scope_sql, scope_params = self._scope_filter()
        recent_from = window.to_utc - timedelta(days=recent_days)
        previous_from = window.to_utc - timedelta(days=recent_days * 2)
        result = await self._session.execute(
            text(
                f"""
                SELECT
                    COALESCE(
                        SUM(
                            CASE
                                WHEN o.order_date >= :recent_from
                                THEN o.net_amount
                                ELSE 0
                            END
                        ),
                        0
                    ) AS recent,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN o.order_date < :recent_from
                                 AND o.order_date >= :previous_from
                                THEN o.net_amount
                                ELSE 0
                            END
                        ),
                        0
                    ) AS previous
                FROM orders o
                WHERE o.customer_id = CAST(:customer_id AS uuid)
                  AND EXISTS (
                      SELECT 1
                      FROM customers c
                      WHERE c.id = o.customer_id
                        {scope_sql}
                  )
                  AND o.status IN ({self._valid_order_status_sql})
                  AND o.order_date >= :previous_from
                  AND o.order_date < :to_utc
                """
            ),
            {
                "customer_id": customer_id,
                "recent_from": recent_from,
                "previous_from": previous_from,
                "to_utc": window.to_utc,
                **scope_params,
            },
        )
        row = result.mappings().one()
        return self._trend_label_from_spend(
            Decimal(str(row["recent"] or 0)),
            Decimal(str(row["previous"] or 0)),
        )

    async def get_dashboard(
        self,
        days: int = 365,
        channel: str | None = None,
        category: str | None = None,
        segment: str | None = None,
        level: str | None = None,
        analysis_date: date | None = None,
    ) -> dict[str, Any]:
        """Calculate transaction-only dashboard aggregates with filters."""
        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        scope_sql, scope_params = self._scope_filter()
        order_filters = (
            f"AND o.status IN ({self._valid_order_status_sql})\n"
            "  AND o.order_date >= :from_utc\n"
            "  AND o.order_date < :to_utc"
        )
        params: dict[str, Any] = {
            "from_utc": window.from_utc,
            "to_utc": window.to_utc,
            **scope_params,
        }
        if channel:
            order_filters += "\n  AND o.channel = :channel"
            params["channel"] = channel

        result = await self._session.execute(
            text(
                f"""
                SELECT COUNT(DISTINCT c.id)::int AS customers,
                       COUNT(o.id)::int AS orders,
                       COALESCE(SUM(o.net_amount), 0) AS revenue
                FROM customers c
                LEFT JOIN orders o ON o.customer_id = c.id
                  {order_filters}
                WHERE 1 = 1
                  {scope_sql}
                """
            ),
            params,
        )
        row = result.mappings().one()
        orders = int(row["orders"] or 0)
        rfm_rows = await self._fetch_rfm_rows(days=days, analysis_date=analysis_date)
        scores = await self.get_all_potential_scores(
            days=days, rows=rfm_rows, analysis_date=analysis_date
        )
        segments = await self.get_all_segments(
            days=days, rows=rfm_rows, analysis_date=analysis_date
        )

        top_scores = [
            score
            for score in scores
            if score.score is not None and (level is None or score.level.value == level)
        ]
        target_segment = SegmentType(segment) if segment else SegmentType.AT_RISK
        segment_customers = [s for s in segments if s.segment_type == target_segment]

        return {
            "days": days,
            "analysis_date": window.analysis_date,
            "filters": {
                "channel": channel,
                "category": category,
                "segment": segment,
                "level": level,
            },
            "total_customers": int(row["customers"] or 0),
            "total_orders": orders,
            "total_revenue": Decimal(str(row["revenue"] or 0)),
            "aov": Decimal(str(row["revenue"] or 0)) / orders
            if orders
            else Decimal("0"),
            "segment_distribution": self._count_values(segments, "segment_type"),
            "potential_distribution": self._count_values(scores, "level"),
            "top_potential_customers": [s.to_dict() for s in top_scores[:10]],
            "top_at_risk_customers": [s.to_dict() for s in segment_customers[:10]],
            "top_product_categories": await self._fetch_top_product_categories(
                days=days,
                channel=channel,
                category=category,
                analysis_date=analysis_date,
            ),
        }

    async def get_dashboard_overview(
        self, query: DashboardOverviewQuery
    ) -> dict[str, Any]:
        """Build the live dashboard contract from scoped aggregates."""
        window = query.resolve_window()
        rfm_rows = await self._fetch_rfm_rows(
            days=window.days,
            analysis_date=window.to_date,
        )
        scores = await self.get_all_potential_scores(
            days=window.days,
            rows=rfm_rows,
            analysis_date=window.to_date,
        )
        segments = await self.get_all_segments(
            days=window.days,
            rows=rfm_rows,
            analysis_date=window.to_date,
        )
        score_by_customer = {score.customer_id: score for score in scores}
        segment_by_customer = {segment.customer_id: segment for segment in segments}
        eligible_ids = {row["customer_id"] for row in rfm_rows}
        eligible_ids &= await self._dashboard_active_customer_ids()
        if query.employee != "all":
            eligible_ids &= await self._dashboard_employee_customer_ids(query.employee)
        if query.category != "all":
            eligible_ids &= await self._dashboard_category_customer_ids(
                window, query.category
            )
        if query.segment != "all":
            eligible_ids = {
                customer_id
                for customer_id in eligible_ids
                if segment_by_customer.get(customer_id)
                and segment_by_customer[customer_id].segment_type.value == query.segment
            }
        if query.potential != "all":
            eligible_ids = {
                customer_id
                for customer_id in eligible_ids
                if score_by_customer.get(customer_id)
                and score_by_customer[customer_id].level.value == query.potential
            }

        current_metrics = await self._dashboard_period_metrics(
            window.from_utc,
            window.to_utc_exclusive,
            eligible_ids,
            query.category,
        )
        previous_metrics = await self._dashboard_period_metrics(
            window.previous_from_utc,
            window.previous_to_utc_exclusive,
            eligible_ids,
            query.category,
        )
        current_series = await self._dashboard_daily_series(
            window.from_date,
            window.to_date,
            eligible_ids,
            query.category,
        )
        previous_series = await self._dashboard_daily_series(
            window.previous_from,
            window.previous_to,
            eligible_ids,
            query.category,
        )
        revenue_by_customer = await self._dashboard_customer_revenues(
            window.from_utc,
            window.to_utc_exclusive,
            eligible_ids,
            query.category,
        )
        predictions, prediction_by_customer = await self._dashboard_predictions(
            eligible_ids
        )
        metadata = await self._dashboard_metadata(window.to_date)
        categories = await self._dashboard_categories(
            window.from_utc,
            window.to_utc_exclusive,
            eligible_ids,
            query.category,
        )
        data_quality = await self._dashboard_data_quality(
            window.from_utc,
            window.to_utc_exclusive,
            eligible_ids,
            len(
                [
                    score
                    for customer_id, score in score_by_customer.items()
                    if customer_id in eligible_ids and score.score is None
                ]
            ),
            current_metrics["orders"],
        )

        trend = []
        for index, point in enumerate(current_series):
            previous_point = (
                previous_series[index]
                if index < len(previous_series)
                else {"revenue": 0, "orders": 0}
            )
            trend.append(
                {
                    "date": point["date"],
                    "previous_date": window.previous_from + timedelta(days=index),
                    "revenue": _money_int(point["revenue"]),
                    "previous_revenue": _money_int(previous_point["revenue"]),
                    "orders": int(point["orders"]),
                    "previous_orders": int(previous_point["orders"]),
                }
            )

        segment_counts = {segment_type.value: 0 for segment_type in SegmentType}
        for customer_id in eligible_ids:
            segment = segment_by_customer.get(customer_id)
            if segment is not None:
                segment_counts[segment.segment_type.value] += 1
        segments_response = [
            {
                "key": key,
                "label": _segment_label(key),
                "count": count,
            }
            for key, count in segment_counts.items()
        ]

        score_values: list[float] = []
        for customer_id in eligible_ids:
            score = score_by_customer.get(customer_id)
            if score is not None and score.score is not None:
                score_values.append(float(score.score))
        potential_distribution = _score_distribution(score_values)
        high_threshold = float(settings.POTENTIAL_HIGH_THRESHOLD)
        potential_threshold = float(settings.POTENTIAL_THRESHOLD)
        high_scores = []
        for customer_id in eligible_ids:
            score = score_by_customer.get(customer_id)
            if score is not None and score.score is not None:
                if float(score.score) >= high_threshold:
                    high_scores.append(score)
        high_scores.sort(
            key=lambda score: (-float(score.score or 0), score.customer_id)
        )
        priority_customers = [
            {
                "id": score.customer_id,
                "customer_code": getattr(score, "customer_code", None),
                "name": getattr(score, "name", "Unknown Customer"),
                "segment": (
                    segment_by_customer[score.customer_id].segment_type.value
                    if score.customer_id in segment_by_customer
                    else SegmentType.INSUFFICIENT_DATA.value
                ),
                "potential_score": float(score.score or 0),
                "purchase_probability": (prediction_by_customer.get(score.customer_id)),
                "revenue": _money_int(revenue_by_customer.get(score.customer_id, 0)),
            }
            for score in high_scores
        ]
        opportunity_customers = [
            {
                "id": score.customer_id,
                "customer_code": getattr(score, "customer_code", None),
                "name": getattr(score, "name", "Unknown Customer"),
                "segment": (
                    segment_by_customer[score.customer_id].segment_type.value
                    if score.customer_id in segment_by_customer
                    else SegmentType.INSUFFICIENT_DATA.value
                ),
                "potential_score": float(score.score or 0),
                "purchase_probability": float(
                    prediction_by_customer[score.customer_id]
                ),
                "revenue": _money_int(revenue_by_customer.get(score.customer_id, 0)),
            }
            for score in score_by_customer.values()
            if score.customer_id in eligible_ids
            and score.score is not None
            and score.customer_id in prediction_by_customer
        ]
        opportunity_customers.sort(key=_opportunity_sort_key)
        opportunity_pagination = _pagination(
            len(opportunity_customers),
            query.opportunity_page,
            query.opportunity_page_size,
        )
        priority_pagination = _pagination(
            len(priority_customers),
            query.priority_page,
            query.priority_page_size,
        )
        opportunity_customers = _paginate(
            opportunity_customers,
            query.opportunity_page,
            query.opportunity_page_size,
        )
        priority_customers = _paginate(
            priority_customers,
            query.priority_page,
            query.priority_page_size,
        )

        current_revenue = _money_int(current_metrics["revenue"])
        previous_revenue = _money_int(previous_metrics["revenue"])
        current_orders = int(current_metrics["orders"])
        previous_orders = int(previous_metrics["orders"])
        current_aov = current_revenue / current_orders if current_orders else 0
        previous_aov = previous_revenue / previous_orders if previous_orders else 0
        return {
            "meta": metadata,
            "period": {
                "from": window.from_date,
                "to": window.to_date,
                "previous_from": window.previous_from,
                "previous_to": window.previous_to,
            },
            "filters": {
                "period": query.period.value,
                "from": window.from_date,
                "to": window.to_date,
                "segment": query.segment,
                "potential": query.potential,
                "category": query.category,
                "employee": query.employee,
            },
            "metrics": {
                "customers": {
                    "current": len(eligible_ids),
                    "previous": len(eligible_ids),
                    "change_percent": None,
                },
                "orders": {
                    "current": current_orders,
                    "previous": previous_orders,
                    "change_percent": _change_percent(current_orders, previous_orders),
                },
                "revenue": {
                    "current": current_revenue,
                    "previous": previous_revenue,
                    "change_percent": _change_percent(
                        current_revenue, previous_revenue
                    ),
                },
                "aov": {
                    "current": current_aov,
                    "previous": previous_aov,
                    "change_percent": _change_percent(current_aov, previous_aov),
                },
            },
            "trend": trend,
            "segments": segments_response,
            "potential": {
                "distribution": potential_distribution,
                "high_count": len(high_scores),
                "eligible_count": len(score_values),
                "insufficient_count": len(eligible_ids) - len(score_values),
                "average_score": (
                    round(sum(score_values) / len(score_values), 2)
                    if score_values
                    else None
                ),
                "thresholds": {
                    "high": high_threshold,
                    "potential": potential_threshold,
                },
                "weights": {
                    key: value
                    for key, value in settings.score_weights.items()
                    if key != "trend"
                },
            },
            "categories": categories,
            "predictions": predictions,
            "opportunity_customers": opportunity_customers,
            "priority_customers": priority_customers,
            "opportunity_pagination": opportunity_pagination,
            "priority_pagination": priority_pagination,
            "priority_total": len(high_scores),
            "data_quality": data_quality,
        }

    async def get_dashboard_options(self) -> dict[str, Any]:
        """Return options constrained to the current user's customer scope."""
        scope_sql, scope_params = self._scope_filter()
        categories_result = await self._session.execute(
            text(
                f"""
                SELECT DISTINCT p.category AS id, p.category AS name
                FROM products p
                JOIN order_items oi ON oi.product_id = p.id
                JOIN orders o ON o.id = oi.order_id
                JOIN customers c ON c.id = o.customer_id
                WHERE c.is_deleted = false
                  {scope_sql}
                ORDER BY p.category
                """
            ),
            scope_params,
        )
        employees_result = await self._session.execute(
            text(
                f"""
                SELECT DISTINCT e.id::text AS id, e.name
                FROM employees e
                JOIN customers c ON c.owner_id = e.id
                WHERE c.is_deleted = false
                  {scope_sql}
                ORDER BY e.name
                """
            ),
            scope_params,
        )
        analysis_date = datetime.now(DASHBOARD_TIMEZONE).date()
        return {
            "segments": [
                {"id": value.value, "name": _segment_label(value.value)}
                for value in SegmentType
            ],
            "potential_levels": [
                {"id": value.value, "name": value.value} for value in ScoreLevel
            ],
            "categories": [
                {"id": row["id"], "name": row["name"]}
                for row in categories_result.mappings().all()
            ],
            "employees": [
                {"id": row["id"], "name": row["name"]}
                for row in employees_result.mappings().all()
            ],
            "thresholds": {
                "high": float(settings.POTENTIAL_HIGH_THRESHOLD),
                "potential": float(settings.POTENTIAL_THRESHOLD),
            },
            "weights": {
                key: value
                for key, value in settings.score_weights.items()
                if key != "trend"
            },
            "analysis_date": analysis_date,
            "max_custom_range_days": 366,
        }

    async def _dashboard_active_customer_ids(self) -> set[str]:
        """Return non-deleted customers in the authenticated scope."""
        scope_sql, scope_params = self._scope_filter()
        result = await self._session.execute(
            text(
                f"""
                SELECT c.id::text
                FROM customers c
                WHERE c.is_deleted = false
                  {scope_sql}
                """
            ),
            scope_params,
        )
        return {row[0] for row in result.all()}

    async def _dashboard_employee_customer_ids(self, employee: str) -> set[str]:
        """Return scoped customers owned by one employee."""
        scope_sql, scope_params = self._scope_filter()
        result = await self._session.execute(
            text(
                f"""
                SELECT c.id::text
                FROM customers c
                WHERE c.is_deleted = false
                  {scope_sql}
                  AND EXISTS (
                      SELECT 1 FROM employees e
                      WHERE e.id = c.owner_id
                        AND (e.id::text = :employee OR e.employee_code = :employee)
                  )
                """
            ),
            {"employee": employee, **scope_params},
        )
        return {row[0] for row in result.all()}

    async def _dashboard_category_customer_ids(
        self, window: Any, category: str
    ) -> set[str]:
        """Return customers buying one category in the current period."""
        scope_sql, scope_params = self._scope_filter()
        result = await self._session.execute(
            text(
                f"""
                SELECT DISTINCT o.customer_id::text
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.id
                JOIN products p ON p.id = oi.product_id
                JOIN customers c ON c.id = o.customer_id
                WHERE o.status IN ({self._valid_order_status_sql})
                  AND o.order_date >= :from_utc
                  AND o.order_date < :to_utc
                  AND p.category = :category
                  AND c.is_deleted = false
                  {scope_sql}
                """
            ),
            {
                "from_utc": window.from_utc,
                "to_utc": window.to_utc_exclusive,
                "category": category,
                **scope_params,
            },
        )
        return {row[0] for row in result.all()}

    async def _dashboard_period_metrics(
        self,
        from_utc: datetime,
        to_utc: datetime,
        customer_ids: set[str],
        category: str,
    ) -> dict[str, Any]:
        """Aggregate distinct orders and revenue for one period."""
        if not customer_ids:
            return {"orders": 0, "revenue": Decimal("0")}
        join_sql = ""
        revenue_sql = "o.net_amount"
        category_sql = ""
        if category != "all":
            join_sql = (
                "JOIN order_items oi ON oi.order_id = o.id "
                "JOIN products p ON p.id = oi.product_id"
            )
            revenue_sql = "COALESCE(oi.line_total, oi.line_amount, oi.subtotal, 0)"
            category_sql = "AND p.category = :category"
        result = await self._session.execute(
            text(
                f"""
                SELECT COUNT(DISTINCT o.id)::int AS orders,
                       COALESCE(SUM({revenue_sql}), 0) AS revenue
                FROM orders o
                {join_sql}
                WHERE o.customer_id = ANY(CAST(:customer_ids AS uuid[]))
                  AND o.status IN ({self._valid_order_status_sql})
                  AND o.order_date >= :from_utc
                  AND o.order_date < :to_utc
                  {category_sql}
                """
            ),
            {
                "customer_ids": _uuid_array(customer_ids),
                "from_utc": from_utc,
                "to_utc": to_utc,
                "category": category,
            },
        )
        row = result.mappings().one()
        return {"orders": int(row["orders"] or 0), "revenue": row["revenue"] or 0}

    async def _dashboard_daily_series(
        self,
        from_date: date,
        to_date: date,
        customer_ids: set[str],
        category: str,
    ) -> list[dict[str, Any]]:
        """Return one zero-filled aggregate for every local business date."""
        if not customer_ids:
            return [
                {"date": day, "revenue": 0, "orders": 0}
                for day in _date_range(from_date, to_date)
            ]
        join_sql = ""
        revenue_sql = "o.net_amount"
        orders_sql = "COUNT(DISTINCT o.id)::int"
        if category != "all":
            join_sql = (
                "LEFT JOIN order_items oi ON oi.order_id = o.id "
                "LEFT JOIN products p ON p.id = oi.product_id "
                "AND p.category = :category"
            )
            revenue_sql = (
                "CASE WHEN p.id IS NOT NULL "
                "THEN COALESCE(oi.line_total, oi.line_amount, oi.subtotal, 0) "
                "ELSE 0 END"
            )
            orders_sql = "COUNT(DISTINCT CASE WHEN p.id IS NOT NULL THEN o.id END)::int"
        result = await self._session.execute(
            text(
                f"""
                SELECT series.day::date AS date,
                       COALESCE(SUM({revenue_sql}), 0) AS revenue,
                       {orders_sql} AS orders
                FROM generate_series(
                    CAST(:from_date AS date),
                    CAST(:to_date AS date),
                    interval '1 day'
                ) AS series(day)
                LEFT JOIN orders o
                  ON (o.order_date AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
                     = series.day::date
                 AND o.customer_id = ANY(CAST(:customer_ids AS uuid[]))
                 AND o.status IN ({self._valid_order_status_sql})
                {join_sql}
                GROUP BY series.day
                ORDER BY series.day
                """
            ),
            {
                "from_date": from_date,
                "to_date": to_date,
                "customer_ids": _uuid_array(customer_ids),
                "category": category,
            },
        )
        return [dict(row) for row in result.mappings().all()]

    async def _dashboard_customer_revenues(
        self,
        from_utc: datetime,
        to_utc: datetime,
        customer_ids: set[str],
        category: str,
    ) -> dict[str, Any]:
        """Aggregate current-period revenue by customer."""
        if not customer_ids:
            return {}
        join_sql = ""
        revenue_sql = "o.net_amount"
        category_sql = ""
        if category != "all":
            join_sql = (
                "JOIN order_items oi ON oi.order_id = o.id "
                "JOIN products p ON p.id = oi.product_id"
            )
            revenue_sql = "COALESCE(oi.line_total, oi.line_amount, oi.subtotal, 0)"
            category_sql = "AND p.category = :category"
        result = await self._session.execute(
            text(
                f"""
                SELECT o.customer_id::text AS customer_id,
                       COALESCE(SUM({revenue_sql}), 0) AS revenue
                FROM orders o
                {join_sql}
                WHERE o.customer_id = ANY(CAST(:customer_ids AS uuid[]))
                  AND o.status IN ({self._valid_order_status_sql})
                  AND o.order_date >= :from_utc
                  AND o.order_date < :to_utc
                  {category_sql}
                GROUP BY o.customer_id
                """
            ),
            {
                "customer_ids": _uuid_array(customer_ids),
                "from_utc": from_utc,
                "to_utc": to_utc,
                "category": category,
            },
        )
        return {
            row["customer_id"]: row["revenue"] or 0 for row in result.mappings().all()
        }

    async def _dashboard_categories(
        self,
        from_utc: datetime,
        to_utc: datetime,
        customer_ids: set[str],
        category: str,
    ) -> list[dict[str, Any]]:
        """Aggregate category revenue, orders, units, and customers."""
        if not customer_ids:
            return []
        category_sql = "AND p.category = :category" if category != "all" else ""
        result = await self._session.execute(
            text(
                f"""
                SELECT p.category AS id,
                       p.category AS name,
                       COALESCE(
                           SUM(COALESCE(oi.line_total, oi.line_amount, oi.subtotal, 0)),
                           0
                       ) AS revenue,
                       COUNT(DISTINCT o.id)::int AS orders,
                       COALESCE(SUM(oi.quantity), 0)::int AS units,
                       COUNT(DISTINCT o.customer_id)::int AS customers
                FROM order_items oi
                JOIN products p ON p.id = oi.product_id
                JOIN orders o ON o.id = oi.order_id
                WHERE o.customer_id = ANY(CAST(:customer_ids AS uuid[]))
                  AND o.status IN ({self._valid_order_status_sql})
                  AND o.order_date >= :from_utc
                  AND o.order_date < :to_utc
                  {category_sql}
                GROUP BY p.category
                ORDER BY revenue DESC, p.category
                """
            ),
            {
                "customer_ids": _uuid_array(customer_ids),
                "from_utc": from_utc,
                "to_utc": to_utc,
                "category": category,
            },
        )
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "revenue": _money_int(row["revenue"]),
                "orders": int(row["orders"] or 0),
                "units": int(row["units"] or 0),
                "customers": int(row["customers"] or 0),
            }
            for row in result.mappings().all()
        ]

    async def _dashboard_predictions(
        self, customer_ids: set[str]
    ) -> tuple[dict[str, Any], dict[str, float]]:
        """Read the newest persisted prediction snapshot for the cohort."""
        empty_distribution = _probability_distribution([])
        deployed_result = await self._session.execute(
            select(ModelRegistryModel).where(
                ModelRegistryModel.status == ModelLifecycleStatus.DEPLOYED
            )
        )
        model = deployed_result.scalar_one_or_none()
        if model is None:
            return (
                {
                    "status": "not_deployed",
                    "model_version": None,
                    "prediction_date": None,
                    "horizon_days": None,
                    "feature_window": None,
                    "evaluated_customers": 0,
                    "insufficient_count": len(customer_ids),
                    "distribution": empty_distribution,
                },
                {},
            )
        if not customer_ids:
            return (
                {
                    "status": "insufficient_data",
                    "model_version": model.version,
                    "prediction_date": None,
                    "horizon_days": model.prediction_horizon_days,
                    "feature_window": model.feature_window_days,
                    "evaluated_customers": 0,
                    "insufficient_count": 0,
                    "distribution": empty_distribution,
                },
                {},
            )
        result = await self._session.execute(
            text(
                """
                SELECT customer_id::text AS customer_id,
                       prediction_date,
                       prediction_horizon_days,
                       feature_window_days,
                       purchase_probability
                FROM purchase_predictions
                WHERE customer_id = ANY(CAST(:customer_ids AS uuid[]))
                  AND model_version = :model_version
                ORDER BY customer_id, prediction_date DESC
                """
            ),
            {
                "customer_ids": _uuid_array(customer_ids),
                "model_version": model.version,
            },
        )
        latest: dict[str, dict[str, Any]] = {}
        for row in result.mappings().all():
            latest.setdefault(row["customer_id"], dict(row))
        values = {
            customer_id: float(row["purchase_probability"])
            for customer_id, row in latest.items()
        }
        rows = list(latest.values())
        status = "available" if rows else "insufficient_data"
        latest_row = max(rows, key=lambda row: row["prediction_date"], default=None)
        return (
            {
                "status": status,
                "model_version": model.version,
                "prediction_date": (
                    latest_row["prediction_date"] if latest_row else None
                ),
                "horizon_days": (
                    latest_row["prediction_horizon_days"]
                    if latest_row
                    else model.prediction_horizon_days
                ),
                "feature_window": (
                    latest_row["feature_window_days"]
                    if latest_row
                    else model.feature_window_days
                ),
                "evaluated_customers": len(values),
                "insufficient_count": len(customer_ids) - len(values),
                "distribution": _probability_distribution(list(values.values())),
            },
            values,
        )

    async def _dashboard_metadata(self, analysis_date: date) -> dict[str, Any]:
        """Load the latest completed run metadata without mutating state."""
        result = await self._session.execute(
            text(
                """
                SELECT ar.run_code,
                       COALESCE(cv.version, :fallback_config) AS config_version
                FROM analysis_runs ar
                LEFT JOIN configuration_versions cv
                  ON cv.id = ar.configuration_version_id
                WHERE ar.analysis_date <= :analysis_date
                  AND ar.status IN ('COMPLETED', 'SUCCESS')
                ORDER BY ar.analysis_date DESC, ar.completed_at DESC NULLS LAST
                LIMIT 1
                """
            ),
            {
                "analysis_date": analysis_date,
                "fallback_config": settings.SCORING_CONFIGURATION_VERSION,
            },
        )
        row = result.mappings().first()
        return {
            "source": "live",
            "generated_at": datetime.now(UTC),
            "analysis_date": analysis_date,
            "run_id": row["run_code"] if row else None,
            "config_version": (
                row["config_version"] if row else settings.SCORING_CONFIGURATION_VERSION
            ),
            "currency": "VND",
            "timezone": "Asia/Ho_Chi_Minh",
        }

    async def _dashboard_data_quality(
        self,
        from_utc: datetime,
        to_utc: datetime,
        customer_ids: set[str],
        unscored_customers: int,
        valid_orders: int,
    ) -> dict[str, Any]:
        """Return quality counters for the scoped dashboard cohort."""
        if not customer_ids:
            return {
                "valid_orders": valid_orders,
                "excluded_orders": 0,
                "unscored_customers": unscored_customers,
                "interaction_source": "real",
            }
        result = await self._session.execute(
            text(
                f"""
                SELECT COUNT(*) FILTER (
                           WHERE o.status NOT IN ({self._valid_order_status_sql})
                       )::int AS excluded_orders
                FROM orders o
                WHERE o.customer_id = ANY(CAST(:customer_ids AS uuid[]))
                  AND o.order_date >= :from_utc
                  AND o.order_date < :to_utc
                """
            ),
            {
                "customer_ids": _uuid_array(customer_ids),
                "from_utc": from_utc,
                "to_utc": to_utc,
            },
        )
        excluded_orders = int(result.scalar_one() or 0)
        interaction_result = await self._session.execute(
            text(
                """
                SELECT COALESCE(BOOL_OR(ci.is_mock_data), false) AS simulated,
                       COUNT(*)::int AS total
                FROM customer_interactions ci
                WHERE ci.customer_id = ANY(CAST(:customer_ids AS uuid[]))
                  AND ci.interaction_timestamp >= :from_utc
                  AND ci.interaction_timestamp < :to_utc
                """
            ),
            {
                "customer_ids": _uuid_array(customer_ids),
                "from_utc": from_utc,
                "to_utc": to_utc,
            },
        )
        interaction = interaction_result.mappings().one()
        return {
            "valid_orders": valid_orders,
            "excluded_orders": excluded_orders,
            "unscored_customers": unscored_customers,
            "interaction_source": ("simulated" if interaction["simulated"] else "real"),
        }

    async def _fetch_top_product_categories(
        self,
        days: int,
        channel: str | None = None,
        category: str | None = None,
        analysis_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Aggregate most-purchased product categories."""
        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        scope_sql, scope_params = self._scope_filter()
        params: dict[str, Any] = {
            "from_utc": window.from_utc,
            "to_utc": window.to_utc,
            **scope_params,
        }
        filters = ""
        if channel:
            filters += "\n  AND o.channel = :channel"
            params["channel"] = channel
        if category:
            filters += "\n  AND p.category = :category"
            params["category"] = category
        query = text(
            f"""
            SELECT p.category,
                   SUM(oi.quantity)::int AS total_quantity,
                   COALESCE(SUM(oi.subtotal), 0) AS total_revenue,
                   COUNT(DISTINCT o.id)::int AS order_count
            FROM order_items oi
            JOIN products p ON p.id = oi.product_id
            JOIN orders o ON o.id = oi.order_id
            JOIN customers c ON c.id = o.customer_id
            WHERE o.status IN ({self._valid_order_status_sql})
              AND o.order_date >= :from_utc
              AND o.order_date < :to_utc
              {scope_sql}
              {filters}
            GROUP BY p.category
            ORDER BY total_revenue DESC
            LIMIT 8
            """
        )
        result = await self._session.execute(query, params)
        return [
            {
                "category": row["category"],
                "total_quantity": int(row["total_quantity"] or 0),
                "total_revenue": Decimal(str(row["total_revenue"] or 0)),
                "order_count": int(row["order_count"] or 0),
            }
            for row in result.mappings().all()
        ]

    async def get_purchase_predictions(
        self,
        days: int = 365,
        horizon_days: int = 90,
        analysis_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Return predictions only from an explicitly deployed model."""
        deployed_result = await self._session.execute(
            select(ModelRegistryModel).where(
                ModelRegistryModel.status == ModelLifecycleStatus.DEPLOYED
            )
        )
        deployed_model = deployed_result.scalar_one_or_none()
        if deployed_model is None:
            raise AppException(
                ErrorCode.MODEL_NOT_AVAILABLE,
                "No deployed purchase prediction model is available.",
            )

        if not deployed_model.artifact_uri:
            raise AppException(
                ErrorCode.MODEL_NOT_AVAILABLE,
                "The deployed model has no serialized artifact.",
            )
        artifact_path = Path(deployed_model.artifact_uri)
        if not artifact_path.is_file():
            raise AppException(
                ErrorCode.MODEL_NOT_AVAILABLE,
                "The deployed model artifact cannot be read.",
            )
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        rows = await self._fetch_rfm_rows(days=days, analysis_date=analysis_date)
        now = datetime.now(UTC)
        predictions: list[dict[str, Any]] = []
        for row in rows:
            if row["recency_days"] is None:
                continue
            behavior = await self.get_behavior_metrics(
                customer_id=row["customer_id"],
                days=days,
                analysis_date=analysis_date,
            )
            feature_row = {
                "recency": row["recency_days"],
                "frequency": row["frequency"],
                "monetary": row["monetary"],
                "aov": (
                    behavior["aov"] if behavior and behavior["aov"] is not None else 0
                ),
                "purchase_cycle": (
                    behavior["purchase_cycle_days"]
                    if behavior and behavior["purchase_cycle_days"] is not None
                    else 0
                ),
                "interaction_score": row["interaction_score"],
                "product_diversity": behavior["product_diversity"] if behavior else 0,
                "review_score": (
                    behavior["review_score"]
                    if behavior and behavior["review_score"] is not None
                    else 0
                ),
            }
            predictions.append(
                {
                    "customer_id": row["customer_id"],
                    "customer_code": row.get("customer_code"),
                    "name": row["name"],
                    "prediction_date": now,
                    "prediction_horizon_days": horizon_days,
                    "feature_window_days": days,
                    "purchase_probability": predict_purchase_probability(
                        artifact, feature_row
                    ),
                    "model_version": deployed_model.version,
                }
            )
        return sorted(
            predictions, key=lambda item: item["purchase_probability"], reverse=True
        )

    async def get_training_feature_rows(
        self,
        days: int = 365,
        horizon_days: int = 90,
        analysis_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Build historical features and 90-day purchase labels."""
        if analysis_date is None:
            latest_order_result = await self._session.execute(
                text(
                    f"""
                    SELECT MAX(order_date)::date
                    FROM orders
                    WHERE status IN ({self._valid_order_status_sql})
                    """
                )
            )
            latest_order_date = latest_order_result.scalar_one_or_none()
            if latest_order_date is not None:
                analysis_date = latest_order_date - timedelta(days=horizon_days)

        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        scope_sql, scope_params = self._scope_filter()
        label_result = await self._session.execute(
            text(
                f"""
                SELECT
                    c.id::text AS customer_id,
                    EXISTS (
                        SELECT 1
                        FROM orders future_orders
                        WHERE future_orders.customer_id = c.id
                          AND future_orders.status IN (
                              {self._valid_order_status_sql}
                          )
                          AND future_orders.order_date >= :horizon_from
                          AND future_orders.order_date < :horizon_to
                    ) AS label
                FROM customers c
                WHERE 1 = 1
                  {scope_sql}
                """
            ),
            {
                "horizon_from": window.to_utc,
                "horizon_to": window.to_utc + timedelta(days=horizon_days),
                **scope_params,
            },
        )
        labels = {
            row["customer_id"]: int(row["label"])
            for row in label_result.mappings().all()
        }
        base_rows = await self._fetch_rfm_rows(
            days=days,
            analysis_date=analysis_date,
        )
        feature_rows: list[dict[str, Any]] = []
        for row in base_rows:
            if row["recency_days"] is None:
                continue
            behavior = await self.get_behavior_metrics(
                customer_id=row["customer_id"],
                days=days,
                analysis_date=analysis_date,
            )
            feature_rows.append(
                {
                    "customer_id": row["customer_id"],
                    "customer_code": row.get("customer_code"),
                    "name": row["name"],
                    "label": labels.get(row["customer_id"], 0),
                    "recency": row["recency_days"],
                    "frequency": row["frequency"],
                    "monetary": row["monetary"],
                    "aov": (
                        behavior["aov"]
                        if behavior and behavior["aov"] is not None
                        else 0
                    ),
                    "purchase_cycle": (
                        behavior["purchase_cycle_days"]
                        if behavior and behavior["purchase_cycle_days"] is not None
                        else 0
                    ),
                    "interaction_score": row["interaction_score"],
                    "product_diversity": (
                        behavior["product_diversity"] if behavior else 0
                    ),
                    "review_score": (
                        behavior["review_score"]
                        if behavior and behavior["review_score"] is not None
                        else 0
                    ),
                }
            )
        return feature_rows

    async def get_customer_prediction(
        self,
        customer_id: str,
        days: int = 365,
        horizon_days: int = 90,
        analysis_date: date | None = None,
    ) -> dict[str, Any] | None:
        """Get one prediction from the deployed model."""
        predictions = await self.get_purchase_predictions(
            days, horizon_days, analysis_date
        )
        for prediction in predictions:
            if prediction["customer_id"] == customer_id:
                return prediction
        return None

    async def get_segment_history(
        self,
        customer_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch persisted segment snapshots, newest first."""
        stmt = (
            select(SegmentHistoryModel, CustomerModel.customer_code)
            .join(
                CustomerModel,
                CustomerModel.id == SegmentHistoryModel.customer_id,
            )
            .order_by(SegmentHistoryModel.calculated_at.desc())
        )
        user = self._current_user
        if user is not None and user.role_code != "ADMIN":
            stmt = stmt.where(
                CustomerModel.assigned_user_id
                == (uuid.UUID(user.id_) if user.id_ else None)
            )
        if customer_id:
            stmt = stmt.where(SegmentHistoryModel.customer_id == uuid.UUID(customer_id))
        stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        return [
            {
                "customer_id": str(row.customer_id),
                "customer_code": customer_code,
                "segment_type": row.segment_type,
                "reason": row.reason,
                "calculated_at": row.calculated_at,
                "recorded_at": row.created_at,
            }
            for row, customer_code in result.all()
        ]

    async def save_current_potential_scores(
        self, scores: list[PotentialScoreEntity], days: int
    ) -> None:
        """Replace the canonical potential-score snapshot for all customers."""
        if not scores:
            return
        values = [
            {
                "customer_id": uuid.UUID(score.customer_id),
                "potential_score": score.score,
                "potential_level": score.level.value,
                "analysis_date": score.analysis_date,
                "feature_window_days": days,
                "calculated_at": score.calculated_at,
                "scoring_configuration_version": (
                    settings.SCORING_CONFIGURATION_VERSION
                ),
            }
            for score in scores
        ]
        statement = insert(CurrentPotentialScoreModel).values(values)
        await self._session.execute(
            statement.on_conflict_do_update(
                index_elements=[CurrentPotentialScoreModel.customer_id],
                set_={
                    "potential_score": statement.excluded.potential_score,
                    "potential_level": statement.excluded.potential_level,
                    "analysis_date": statement.excluded.analysis_date,
                    "feature_window_days": statement.excluded.feature_window_days,
                    "calculated_at": statement.excluded.calculated_at,
                    "scoring_configuration_version": (
                        statement.excluded.scoring_configuration_version
                    ),
                },
            )
        )
        await self._session.flush()

    async def save_segment_history(self, segments: list[SegmentEntity]) -> None:
        """Persist a segmentation snapshot without replacing prior history."""
        for segment in segments:
            self._session.add(
                SegmentHistoryModel(
                    customer_id=uuid.UUID(segment.customer_id),
                    segment_type=segment.segment_type.value,
                    reason=segment.reason,
                    calculated_at=segment.calculated_at,
                )
            )
        await self._session.flush()

    async def save_purchase_predictions(
        self, predictions: list[dict[str, Any]]
    ) -> None:
        """Persist predictions with their feature-window metadata."""
        for prediction in predictions:
            self._session.add(
                PurchasePredictionModel(
                    id=uuid.uuid4(),
                    customer_id=uuid.UUID(prediction["customer_id"]),
                    prediction_date=prediction["prediction_date"],
                    prediction_horizon_days=prediction["prediction_horizon_days"],
                    feature_window_days=prediction["feature_window_days"],
                    purchase_probability=prediction["purchase_probability"],
                    model_version=prediction["model_version"],
                    features={"baseline": True},
                )
            )
        await self._session.flush()

    async def commit(self) -> None:
        """Commit analytics snapshots."""
        await self._session.commit()

    @staticmethod
    def _count_values(items: list[Any], attribute: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = getattr(item, attribute)
            key = value.value if hasattr(value, "value") else str(value)
            counts[key] = counts.get(key, 0) + 1
        return counts

    async def _fetch_rfm_rows(
        self,
        days: int,
        analysis_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch base RFM and order aggregates for the approved UTC window."""
        scope_sql, scope_params = self._scope_filter()
        window = resolve_analysis_window(days=days, analysis_date=analysis_date)
        recent_days = max(30, min(days // 4, 90))
        recent_from = window.to_utc - timedelta(days=recent_days)
        previous_from = window.to_utc - timedelta(days=recent_days * 2)
        query = text(
            f"""
            SELECT
                c.id::text AS customer_id,
                c.customer_code,
                c.name,
                EXTRACT(
                    EPOCH FROM (:to_utc - MAX(o.order_date))
                ) / 86400.0 AS recency_days,
                COUNT(DISTINCT o.id)::int AS frequency,
                COALESCE(
                    (
                        SELECT COUNT(DISTINCT lifetime_orders.id)::int
                        FROM orders lifetime_orders
                        WHERE lifetime_orders.customer_id = c.id
                          AND lifetime_orders.status IN ({self._valid_order_status_sql})
                          AND lifetime_orders.order_date < :to_utc
                    ),
                    0
                ) AS lifetime_frequency,
                COALESCE(SUM(o.net_amount), 0) AS monetary,
                MIN(o.order_date) AS first_purchase_date,
                COALESCE(
                    SUM(
                        CASE
                            WHEN o.order_date >= :recent_from
                            THEN o.net_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS recent_spend,
                COALESCE(
                    SUM(
                        CASE
                            WHEN o.order_date < :recent_from
                             AND o.order_date >= :previous_from
                            THEN o.net_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS previous_spend,
                COALESCE(
                    (
                        SELECT COALESCE(
                            SUM(COALESCE(ci.interaction_value, 0)),
                            0
                        )
                        FROM customer_interactions ci
                        WHERE ci.customer_id = c.id
                    ),
                    0
                ) AS interaction_score
            FROM customers c
            LEFT JOIN orders o
              ON o.customer_id = c.id
             AND o.status IN ({self._valid_order_status_sql})
             AND o.order_date >= :from_utc
             AND o.order_date < :to_utc
            WHERE 1 = 1
              {scope_sql}
            GROUP BY c.id, c.name, c.customer_code
            ORDER BY c.name ASC
            """
        )
        params = {
            "from_utc": window.from_utc,
            "to_utc": window.to_utc,
            "recent_from": recent_from,
            "previous_from": previous_from,
            **scope_params,
        }
        result = await self._session.execute(query, params)
        return [dict(row) for row in result.mappings().all()]

    async def _build_rfm_entities(
        self,
        days: int,
        rows: list[dict[str, Any]] | None = None,
        analysis_date: date | None = None,
    ) -> list[RFMEntity]:
        """Build scored RFM entities from raw aggregates."""
        analytics_rows = (
            await self._fetch_rfm_rows(days=days, analysis_date=analysis_date)
            if rows is None
            else rows
        )
        if not analytics_rows:
            return []

        resolved_date = resolve_analysis_window(
            days=days, analysis_date=analysis_date
        ).analysis_date
        active_rows = [row for row in analytics_rows if int(row["frequency"] or 0) > 0]
        recency_scores = self._rank_scores(
            active_rows,
            lambda row: float(row["recency_days"]),
            descending=False,
        )
        frequency_scores = self._percentile_scores(
            analytics_rows,
            lambda row: float(row.get("lifetime_frequency", row["frequency"]) or 0),
            higher_is_better=True,
        )
        monetary_scores = self._rank_scores(
            active_rows,
            lambda row: float(row["monetary"] or 0),
            descending=True,
        )
        interaction_values = [
            float(row["interaction_score"] or 0) for row in analytics_rows
        ]
        interaction_min = min(interaction_values)
        interaction_max = max(interaction_values)
        entities: list[RFMEntity] = []
        for row in analytics_rows:
            customer_id = row["customer_id"]
            window_frequency = int(row["frequency"] or 0)
            frequency = int(row.get("lifetime_frequency", window_frequency) or 0)
            has_orders = window_frequency > 0
            monetary = Decimal(str(row["monetary"] or 0))
            recent_spend = Decimal(str(row["recent_spend"] or 0))
            previous_spend = Decimal(str(row["previous_spend"] or 0))
            f_score = frequency_scores.get(customer_id) if frequency > 0 else None
            r_score = recency_scores.get(customer_id) if has_orders else None
            m_score = monetary_scores.get(customer_id) if has_orders else None
            entity = RFMEntity(
                customer_id=customer_id,
                recency_days=(
                    float(row["recency_days"])
                    if row["recency_days"] is not None
                    else None
                ),
                frequency=frequency,
                monetary=monetary,
                r_score=r_score,
                f_score=f_score,
                m_score=m_score,
                rfm_score=(
                    r_score + f_score + m_score
                    if r_score is not None
                    and f_score is not None
                    and m_score is not None
                    else None
                ),
                first_purchase_date=row.get("first_purchase_date"),
                trend=self._trend_label_from_spend(recent_spend, previous_spend),
                interaction_score=float(row["interaction_score"] or 0),
                interaction_normalized_score=self._min_max_score(
                    float(row["interaction_score"] or 0),
                    interaction_min,
                    interaction_max,
                ),
                analysis_date=resolved_date,
            )
            entity.name = row["name"]
            entity.customer_code = row.get("customer_code")
            entities.append(entity)

        entities.sort(
            key=lambda item: (
                item.rfm_score is not None,
                item.rfm_score or -1,
                item.monetary,
                item.frequency,
            ),
            reverse=True,
        )
        return entities

    @staticmethod
    def _min_max_score(value: float, minimum: float, maximum: float) -> float:
        """Normalize a raw interaction value to the continuous 1..5 scale."""
        if maximum == minimum:
            return 3.0
        return 1 + ((value - minimum) / (maximum - minimum)) * 4

    @staticmethod
    def _percentile_scores(
        rows: list[dict[str, Any]],
        value: Callable[[dict[str, Any]], float],
        *,
        higher_is_better: bool,
    ) -> dict[str, int]:
        """Map values to five points using the documented PERCENTRANK formula."""
        if not rows:
            return {}
        values = [value(row) for row in rows]
        denominator = max(len(values) - 1, 1)
        scores: dict[str, int] = {}
        for row, current in zip(rows, values, strict=True):
            better_count = (
                sum(candidate < current for candidate in values)
                if higher_is_better
                else sum(candidate > current for candidate in values)
            )
            percentile = better_count / denominator
            scores[row["customer_id"]] = max(
                1,
                min(5, ceil(percentile * 4 + 1)),
            )
        return scores

    @staticmethod
    def _rank_scores(
        rows: list[dict[str, Any]],
        value: Callable[[dict[str, Any]], float],
        *,
        descending: bool,
    ) -> dict[str, int]:
        """Map ordered values to deterministic five-point rank scores."""
        if not rows:
            return {}
        ordered = sorted(
            rows,
            key=lambda row: (value(row), str(row["customer_id"])),
            reverse=descending,
        )
        size = len(ordered)
        return {
            row["customer_id"]: max(1, min(5, ceil((size - index) * 5 / size)))
            for index, row in enumerate(ordered)
        }

    def _potential_score_details(
        self, rfm: RFMEntity
    ) -> tuple[float | None, dict[str, float], list[str]]:
        """Calculate the documented weighted Potential Score."""
        weights = settings.score_weights
        missing_components = [
            name
            for name, value in (
                ("recency", rfm.r_score),
                ("frequency", rfm.f_score),
                ("monetary", rfm.m_score),
            )
            if value is None
        ]
        if missing_components:
            return None, weights, missing_components

        interaction = (
            rfm.interaction_normalized_score
            if rfm.interaction_normalized_score is not None
            else rfm.interaction_score
        )
        values = {
            "recency": rfm.r_score,
            "frequency": rfm.f_score,
            "monetary": rfm.m_score,
            "interaction": interaction,
        }
        score = round(
            sum(float(values[key]) * weights[key] for key in weights)
            * settings.SCORE_SCALE_MULTIPLIER,
            2,
        )
        return score, weights, missing_components

    def _potential_score_from_rfm(self, rfm: RFMEntity) -> float | None:
        """Calculate the Script_Duan weighted Potential Score."""
        score, _, _ = self._potential_score_details(rfm)
        return score

    @staticmethod
    def _score_components(
        rfm: RFMEntity,
        weights: dict[str, float],
        missing_components: list[str],
    ) -> dict[str, Any]:
        """Expose the exact weighted inputs used by the potential score."""
        return {
            "recency": rfm.r_score,
            "frequency": rfm.f_score,
            "monetary": rfm.m_score,
            "interaction": rfm.interaction_normalized_score,
            "interactionRaw": rfm.interaction_score,
            "weights": {key: round(value, 4) for key, value in weights.items()},
            "missingComponents": missing_components,
            "configurationVersion": settings.SCORING_CONFIGURATION_VERSION,
        }

    @staticmethod
    def _rfm_snapshot(rfm: RFMEntity) -> dict[str, Any]:
        """Expose the source RFM metrics used before score weighting."""
        return {
            **rfm.to_dict(),
            "name": getattr(rfm, "name", "Unknown Customer"),
            "interaction_normalized_score": rfm.interaction_normalized_score,
        }

    @staticmethod
    def _potential_level(score: float | None) -> ScoreLevel:
        """Map a potential score to its configured level."""
        if score is None:
            return ScoreLevel.INSUFFICIENT_DATA
        if score >= settings.POTENTIAL_HIGH_THRESHOLD:
            return ScoreLevel.HIGH
        if score >= settings.POTENTIAL_THRESHOLD:
            return ScoreLevel.POTENTIAL
        return ScoreLevel.NORMAL

    def _determine_segment(
        self,
        rfm: RFMEntity,
        potential_score: float | None = None,
    ) -> tuple[SegmentType, str]:
        """Classify customers using the documented potential-score bands."""
        if rfm.frequency == 0 or rfm.first_purchase_date is None:
            return (
                SegmentType.INSUFFICIENT_DATA,
                "Khách hàng không có đơn hàng hợp lệ trong kỳ phân tích.",
            )

        if potential_score is None:
            potential_score = self._potential_score_from_rfm(rfm)
        if potential_score is None:
            return (
                SegmentType.INSUFFICIENT_DATA,
                "Khách hàng chưa có đủ dữ liệu RFM.",
            )
        if potential_score >= settings.POTENTIAL_HIGH_THRESHOLD:
            return (
                SegmentType.HIGH_VALUE,
                f"Điểm tiềm năng đạt từ {settings.POTENTIAL_HIGH_THRESHOLD} trở lên.",
            )
        if potential_score >= settings.POTENTIAL_THRESHOLD:
            return (
                SegmentType.POTENTIAL,
                f"Điểm tiềm năng đạt từ {settings.POTENTIAL_THRESHOLD} trở lên.",
            )
        return (
            SegmentType.NORMAL,
            f"Điểm tiềm năng dưới {settings.POTENTIAL_THRESHOLD}.",
        )

    @staticmethod
    def _trend_label_from_spend(recent_spend: Decimal, previous_spend: Decimal) -> str:
        """Classify spend trend using stable relative thresholds."""
        if previous_spend <= 0:
            return "STRONG_INCREASE" if recent_spend > 0 else "STABLE"
        growth_ratio = (recent_spend - previous_spend) / previous_spend
        if growth_ratio <= Decimal("-0.5"):
            return "STRONG_DECREASE"
        if growth_ratio < Decimal("-0.1"):
            return "DECREASE"
        if growth_ratio >= Decimal("0.5"):
            return "STRONG_INCREASE"
        if growth_ratio > Decimal("0.1"):
            return "INCREASE"
        return "STABLE"

    def _calculate_trend_score(
        self, recent_spend: Decimal, previous_spend: Decimal
    ) -> float:
        """Convert approved trend labels into a normalized 0-1 score."""
        return {
            "STRONG_DECREASE": 0.0,
            "DECREASE": 0.2,
            "STABLE": 0.6,
            "INCREASE": 0.8,
            "STRONG_INCREASE": 1.0,
        }[self._trend_label_from_spend(recent_spend, previous_spend)]


def _pagination(total: int, page: int, page_size: int) -> dict[str, Any]:
    """Build stable pagination metadata for a dashboard customer list."""
    total_pages = (total + page_size - 1) // page_size if total else 0
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1 and total_pages > 0,
    }


def _paginate(
    rows: list[dict[str, Any]], page: int, page_size: int
) -> list[dict[str, Any]]:
    """Return one page without changing the stable source ordering."""
    start = (page - 1) * page_size
    return rows[start : start + page_size]


def _uuid_array(customer_ids: set[str]) -> list[uuid.UUID]:
    """Convert UUID strings to a PostgreSQL-compatible UUID array."""
    return [uuid.UUID(customer_id) for customer_id in sorted(customer_ids)]


def _date_range(from_date: date, to_date: date) -> list[date]:
    """Return an inclusive date range without relying on database state."""
    return [
        from_date + timedelta(days=offset)
        for offset in range((to_date - from_date).days + 1)
    ]


def _money_int(value: Any) -> int:
    """Convert a database numeric amount to integer VND."""
    return int(Decimal(str(value or 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _change_percent(current: int | float, previous: int | float) -> float | None:
    """Calculate a finite percentage delta."""
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 2)


def _segment_label(key: str) -> str:
    """Return a stable display label for a segment option."""
    return {
        "HIGH_VALUE": "High value",
        "LOYAL": "Loyal",
        "AT_RISK": "At risk",
        "POTENTIAL": "Potential",
        "NEW_CUSTOMER": "New customer",
        "NORMAL": "Normal",
        "INSUFFICIENT_DATA": "Insufficient data",
    }.get(key, key)


def _score_distribution(values: list[float]) -> list[dict[str, Any]]:
    """Build the five Potential Score buckets."""
    buckets = [
        ("0–19", 0, 20),
        ("20–39", 20, 40),
        ("40–59", 40, 60),
        ("60–79", 60, 80),
        ("80–100", 80, 101),
    ]
    return [
        {
            "label": label,
            "min": float(minimum),
            "max": float(100 if maximum == 101 else maximum),
            "count": sum(minimum <= value < maximum for value in values),
        }
        for label, minimum, maximum in buckets
    ]


def _opportunity_sort_key(customer: dict[str, Any]) -> tuple[float, str]:
    """Sort opportunities by combined score, then stable customer ID."""
    return (
        -float(customer["potential_score"]) * float(customer["purchase_probability"]),
        str(customer["id"]),
    )


def _probability_distribution(values: list[float]) -> list[dict[str, Any]]:
    """Build the five purchase-probability percentage buckets."""
    buckets = [
        ("0–20%", 0.0, 0.2),
        ("20–40%", 0.2, 0.4),
        ("40–60%", 0.4, 0.6),
        ("60–80%", 0.6, 0.8),
        ("80–100%", 0.8, 1.0000001),
    ]
    return [
        {
            "label": label,
            "min": minimum,
            "max": 1.0 if maximum > 1 else maximum,
            "count": sum(minimum <= value < maximum for value in values),
        }
        for label, minimum, maximum in buckets
    ]
