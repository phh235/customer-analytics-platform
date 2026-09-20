"""Validated semantic query plans and deterministic PostgreSQL compilation."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from customer_analytics.app.features.analytics.domain.semantic_layer import (
    ADMIN_RAW_TABLES,
    ANALYTICS_DIMENSIONS,
    ANALYTICS_METRIC_EXPRESSIONS,
    ANALYTICS_METRIC_SOURCES,
    ANALYTICS_TIME_BUCKETS,
    ANALYTICS_VIEWS,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException

PlanMode = Literal["aggregate", "rows", "unsupported"]


class AnalyticsQueryPlan(BaseModel):
    """Structured intent returned by the analytics planner."""

    mode: PlanMode = "aggregate"
    metric: str | None = Field(default=None, max_length=100)
    source: str | None = Field(default=None, max_length=100)
    columns: list[str] = Field(default_factory=list, max_length=30)
    date_field: str = Field(default="created_at", max_length=100)
    date_from: date | None = None
    date_to: date | None = None
    status: str | None = Field(default=None, max_length=32)
    group_by: list[str] = Field(default_factory=list, max_length=5)
    order_by: str | None = Field(default=None, max_length=100)
    order_direction: Literal["asc", "desc"] = "desc"
    time_bucket: str | None = Field(default=None, max_length=16)
    filters: dict[str, str] = Field(default_factory=dict, max_length=10)
    limit: int = Field(default=100, ge=1, le=100)
    sql: str | None = Field(default=None, max_length=10_000)

    @model_validator(mode="after")
    def validate_shape(self) -> AnalyticsQueryPlan:
        """Require either legacy SQL or enough semantic fields to compile."""
        if self.sql is None and self.mode == "aggregate" and self.metric is None:
            raise ValueError("Aggregate plans require a metric.")
        if self.sql is None and self.mode == "rows" and self.source is None:
            raise ValueError("Row plans require a source.")
        if self.date_from and self.date_to and self.date_from >= self.date_to:
            raise ValueError("date_from must be earlier than date_to.")
        return self


def compile_query(plan: AnalyticsQueryPlan, *, admin_mode: bool) -> str:
    """Compile a validated semantic plan into deterministic PostgreSQL SQL."""
    if plan.sql is not None:
        return plan.sql
    if plan.mode == "unsupported":
        _reject("I do not have a supported data source for this question.")
    if plan.mode == "aggregate":
        return _compile_aggregate(plan)
    return _compile_rows(plan, admin_mode=admin_mode)


def _compile_aggregate(plan: AnalyticsQueryPlan) -> str:
    """Compile an aggregate plan against one approved semantic view."""
    metric = plan.metric
    if metric is None or metric not in ANALYTICS_METRIC_EXPRESSIONS:
        _reject(f"Unsupported analytics metric '{metric}'.")
    assert metric is not None
    source = ANALYTICS_METRIC_SOURCES[metric]
    source_columns = ANALYTICS_VIEWS[source]
    expression = ANALYTICS_METRIC_EXPRESSIONS[metric]
    select_parts: list[str] = [f"{expression} AS {metric}"]
    group_expressions: list[str] = []

    if plan.time_bucket is not None:
        if plan.time_bucket not in ANALYTICS_TIME_BUCKETS:
            _reject(f"Unsupported time bucket '{plan.time_bucket}'.")
        _require_column(source_columns, plan.date_field)
        bucket = ANALYTICS_TIME_BUCKETS[plan.time_bucket]
        bucket_expression = f"DATE_TRUNC('{bucket}', {plan.date_field})"
        select_parts.insert(0, f"{bucket_expression} AS period")
        group_expressions.append(bucket_expression)

    for dimension in plan.group_by:
        details = ANALYTICS_DIMENSIONS.get(dimension)
        if details is None or not _dimension_matches_source(details, source):
            _reject(f"Dimension '{dimension}' is not valid for {source}.")
        assert details is not None
        _require_column(source_columns, details["expression"])
        select_parts.append(f"{details['expression']} AS {dimension}")
        group_expressions.append(details["expression"])

    status = _resolve_status(plan)
    where_parts: list[str] = []
    if "status" in source_columns:
        where_parts.append(_status_clause(status))
    elif status is not None:
        _reject(f"Filter 'status' is not valid for {source}.")
    if plan.date_from or plan.date_to:
        _require_column(source_columns, plan.date_field)
    if plan.date_from:
        where_parts.append(f"{plan.date_field} >= DATE '{plan.date_from.isoformat()}'")
    if plan.date_to:
        where_parts.append(f"{plan.date_field} < DATE '{plan.date_to.isoformat()}'")
    for name, value in plan.filters.items():
        if name == "status":
            continue
        details = ANALYTICS_DIMENSIONS.get(name)
        if details is None or not _dimension_matches_source(details, source):
            _reject(f"Filter '{name}' is not valid for {source}.")
        assert details is not None
        where_parts.append(f"{details['expression']} = {_literal(value)}")
    query = [
        "SELECT",
        "    " + ",\n    ".join(select_parts),
        f"FROM analytics.{source}",
        "WHERE " + "\n  AND ".join(where_parts),
    ]
    if group_expressions:
        query.append("GROUP BY " + ", ".join(group_expressions))
    order_by = plan.order_by
    if order_by is None and metric == "view_count" and "product_name" in plan.group_by:
        order_by = metric
    if order_by is not None:
        allowed_order_fields = {metric, *plan.group_by}
        if plan.time_bucket is not None:
            allowed_order_fields.add("period")
        if order_by not in allowed_order_fields:
            _reject(f"Order field '{order_by}' is not valid for this query.")
        query.append(f"ORDER BY {order_by} {plan.order_direction.upper()}")
    query.append(f"LIMIT {plan.limit}")
    return "\n".join(query)


def _compile_rows(plan: AnalyticsQueryPlan, *, admin_mode: bool) -> str:
    """Compile a row listing against one approved source."""
    source = plan.source or ""
    if source.startswith("public."):
        source = source.removeprefix("public.")
    if source in ADMIN_RAW_TABLES:
        if not admin_mode:
            _reject("Raw table queries require ADMIN access.")
        allowed_columns = ADMIN_RAW_TABLES[source]
        qualified_source = f"public.{source}"
    elif source in ANALYTICS_VIEWS:
        allowed_columns = frozenset(ANALYTICS_VIEWS[source])
        qualified_source = f"analytics.{source}"
    else:
        _reject(f"Unsupported analytics source '{plan.source}'.")

    columns = plan.columns or ["*"]
    if "*" in columns:
        if not admin_mode or source not in ADMIN_RAW_TABLES or len(columns) != 1:
            _reject("SELECT * is only available for ADMIN raw table listings.")
        select_sql = "*"
    else:
        for column in columns:
            _require_column(allowed_columns, column)
        select_sql = ", ".join(columns)

    where_parts: list[str] = []
    status = _resolve_status(plan)
    if status is not None:
        _require_column(allowed_columns, "status")
        where_parts.append(_status_clause(status))
    for name, value in plan.filters.items():
        if name == "status":
            continue
        _require_column(allowed_columns, name)
        where_parts.append(f"{name} = {_literal(value)}")
    if plan.date_from or plan.date_to:
        _require_column(allowed_columns, plan.date_field)
        if plan.date_from:
            where_parts.append(
                f"{plan.date_field} >= DATE '{plan.date_from.isoformat()}'"
            )
        if plan.date_to:
            where_parts.append(f"{plan.date_field} < DATE '{plan.date_to.isoformat()}'")

    query = [f"SELECT {select_sql}", f"FROM {qualified_source}"]
    if where_parts:
        query.append("WHERE " + "\n  AND ".join(where_parts))
    if plan.order_by is not None:
        _require_column(allowed_columns, plan.order_by)
        query.append(f"ORDER BY {plan.order_by} {plan.order_direction.upper()}")
    query.append(f"LIMIT {plan.limit}")
    return "\n".join(query)


def _resolve_status(plan: AnalyticsQueryPlan) -> str | None:
    """Accept status from either the dedicated field or generic filters."""
    filter_status = plan.filters.get("status")
    if (
        plan.status is not None
        and filter_status is not None
        and plan.status != filter_status
    ):
        _reject("Conflicting status filters are not allowed.")
    return plan.status if plan.status is not None else filter_status


def _dimension_matches_source(details: dict[str, str], source: str) -> bool:
    """Allow product dimensions on sales and product-view sources."""
    return details["source"] == source or (
        details["source"] == "product_sales" and source == "product_views"
    )


def _status_clause(status: str | None) -> str:
    value = status or "delivered"
    if value not in {"delivered", "processing", "canceled", "returned"}:
        _reject(f"Unsupported order status '{value}'.")
    return f"status = {_literal(value)}"


def _require_column(
    columns: set[str] | frozenset[str] | dict[str, str], name: str
) -> None:
    if name not in columns:
        _reject(f"Column '{name}' is not available for this source.")


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _reject(message: str) -> None:
    raise AppException(ErrorCode.ANALYTICS_QUERY_REJECTED, message=message)
