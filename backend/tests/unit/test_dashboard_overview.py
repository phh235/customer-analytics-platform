"""Focused tests for the dashboard overview contract."""

from __future__ import annotations

from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient

from customer_analytics.app.features.analytics.domain.dashboard_overview import (
    DashboardOverviewQuery,
    DashboardPeriod,
)
from customer_analytics.app.features.analytics.infrastructure.repositories.analytics_repository_impl import (  # noqa: E501
    AnalyticsRepositoryImpl,
    _probability_distribution,
    _score_distribution,
)
from customer_analytics.app.features.analytics.presentation.routes.analytics_routes import (  # noqa: E501
    require_dashboard_read,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.main import app


def test_custom_dashboard_period_builds_equal_previous_window() -> None:
    query = DashboardOverviewQuery(
        period=DashboardPeriod.CUSTOM,
        from_date=date(2026, 6, 22),
        to_date=date(2026, 9, 19),
    )

    window = query.resolve_window()

    assert window.days == 90
    assert window.previous_from == date(2026, 3, 24)
    assert window.previous_to == date(2026, 6, 21)


def test_custom_dashboard_period_rejects_ranges_over_366_days() -> None:
    query = DashboardOverviewQuery(
        period=DashboardPeriod.CUSTOM,
        from_date=date(2025, 1, 1),
        to_date=date(2026, 1, 2),
    )

    with pytest.raises(AppException, match="không được vượt quá"):
        query.resolve_window()


def test_dashboard_histograms_keep_boundary_values_in_final_bucket() -> None:
    score_buckets = _score_distribution([0, 19, 20, 79, 80, 100])
    probability_buckets = _probability_distribution([0, 0.2, 0.8, 1.0])

    assert [bucket["count"] for bucket in score_buckets] == [2, 1, 0, 1, 2]
    assert [bucket["count"] for bucket in probability_buckets] == [1, 1, 0, 0, 2]


def test_rank_scores_are_deterministic_and_five_point() -> None:
    rows = [
        {"customer_id": "c", "value": 30},
        {"customer_id": "a", "value": 10},
        {"customer_id": "b", "value": 20},
    ]

    scores = AnalyticsRepositoryImpl._rank_scores(
        rows, lambda row: float(row["value"]), descending=True
    )
    assert scores == {"c": 5, "b": 4, "a": 2}


@pytest.mark.asyncio
async def test_customer_account_cannot_read_dashboard_even_with_permission() -> None:
    user = UserEntity(
        id_="customer-user",
        email="customer@example.com",
        password_hash="unused",
        full_name="Customer",
        role_code="USER",
        permissions=["analytics:read"],
    )

    with pytest.raises(AppException) as error:
        await require_dashboard_read(user)

    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_dashboard_overview_requires_authentication() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/dashboard/overview")

    assert response.status_code == 401
