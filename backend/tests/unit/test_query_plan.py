from __future__ import annotations

import pytest

from customer_analytics.app.features.analytics.application.query_plan import (
    AnalyticsQueryPlan,
    compile_query,
)
from customer_analytics.app.features.analytics.domain.semantic_layer import (
    build_schema_context,
)
from customer_analytics.app.shared.exceptions import AppException


def test_product_sales_accepts_status_from_generic_filters() -> None:
    plan = AnalyticsQueryPlan(
        metric="quantity_sold",
        filters={"status": "delivered"},
    )

    query = compile_query(plan, admin_mode=False)

    assert "FROM analytics.product_sales" in query
    assert "status = 'delivered'" in query


def test_product_sales_row_plan_accepts_status_filter() -> None:
    plan = AnalyticsQueryPlan(
        mode="rows",
        source="product_sales",
        columns=["product_name", "quantity"],
        filters={"status": "delivered"},
    )

    query = compile_query(plan, admin_mode=False)

    assert "FROM analytics.product_sales" in query
    assert "status = 'delivered'" in query


def test_current_potential_rows_filter_and_order_by_score() -> None:
    plan = AnalyticsQueryPlan(
        mode="rows",
        source="customer_potential_current",
        columns=["customer_code", "potential_score"],
        filters={"potential_level": "HIGH"},
        order_by="potential_score",
        limit=10,
    )

    query = compile_query(plan, admin_mode=False)

    assert "FROM analytics.customer_potential_current" in query
    assert "potential_level = 'HIGH'" in query
    assert "ORDER BY potential_score DESC" in query
    assert query.endswith("LIMIT 10")


def test_product_views_plan_orders_most_viewed_product_first() -> None:
    plan = AnalyticsQueryPlan(
        metric="view_count",
        group_by=["product_name"],
        limit=1,
    )

    query = compile_query(plan, admin_mode=False)

    assert "FROM analytics.product_views" in query
    assert "GROUP BY product_name" in query
    assert "ORDER BY view_count DESC" in query
    assert query.endswith("LIMIT 1")


def test_conflicting_status_fields_are_rejected() -> None:
    plan = AnalyticsQueryPlan(
        metric="quantity_sold",
        status="returned",
        filters={"status": "delivered"},
    )

    with pytest.raises(AppException, match="Conflicting status filters"):
        compile_query(plan, admin_mode=False)


def test_unsupported_plan_is_rejected_for_graceful_chat_fallback() -> None:
    plan = AnalyticsQueryPlan(mode="unsupported")

    with pytest.raises(AppException, match="supported data source"):
        compile_query(plan, admin_mode=False)


def test_product_sales_rejects_customer_region_dimension() -> None:
    plan = AnalyticsQueryPlan(
        metric="quantity_sold",
        group_by=["customer_region"],
    )

    with pytest.raises(AppException, match="not valid for product_sales"):
        compile_query(plan, admin_mode=False)


def test_schema_context_declares_supported_and_unavailable_capabilities() -> None:
    context = build_schema_context()

    assert "analytics.product_views" in context
    assert "Product-view analysis" in context
    assert "analytics.customer_potential_current" in context
    assert "Customer potential analysis" in context
    assert "RFM scores and raw RFM component rankings" in context
    assert '"mode":"unsupported"' in context
