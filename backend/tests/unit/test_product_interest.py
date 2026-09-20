"""Focused tests for product-interest analytics boundaries."""

from __future__ import annotations

from datetime import date

import pytest

from customer_analytics.app.features.analytics.infrastructure.repositories.product_interest_repository_impl import (  # noqa: E501
    _trend_metrics,
)
from customer_analytics.app.features.analytics.presentation.routes.product_interest_routes import (  # noqa: E501
    _resolve_window,
)
from customer_analytics.app.shared.exceptions import AppException


@pytest.mark.parametrize(
    ("current", "previous", "growth", "status"),
    [
        (120, 60, 100.0, "STRONG_TRENDING"),
        (60, 50, 20.0, "TRENDING"),
        (50, 50, 0.0, "STABLE"),
        (40, 50, -20.0, "DECLINING"),
        (12, 0, None, "NEW_TREND"),
        (0, 0, None, "STABLE"),
    ],
)
def test_trend_metrics_apply_growth_thresholds_and_zero_baseline(
    current: int,
    previous: int,
    growth: float | None,
    status: str,
) -> None:
    assert _trend_metrics(current, previous) == (growth, status)


def test_resolve_window_defaults_to_thirty_inclusive_days() -> None:
    assert _resolve_window(None, date(2026, 9, 20)) == (
        date(2026, 8, 22),
        date(2026, 9, 20),
    )


def test_resolve_window_rejects_reversed_dates() -> None:
    with pytest.raises(AppException, match="from_date"):
        _resolve_window(date(2026, 9, 21), date(2026, 9, 20))
