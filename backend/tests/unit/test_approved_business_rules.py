"""Regression coverage for approved order and analysis-window rules."""

from datetime import date
from decimal import Decimal

import pytest

from customer_analytics.app.features.analytics.application.services.model_lifecycle_service import (  # noqa: E501
    ModelLifecycleService,
)
from customer_analytics.app.features.analytics.domain.analysis_window import (
    resolve_analysis_window,
)
from customer_analytics.app.features.order.domain.rules import (
    calculate_net_amount,
    validate_order_status,
)


def test_valid_order_statuses_and_partial_refunds() -> None:
    assert validate_order_status("paid") == "PAID"
    assert validate_order_status("partial_refunded") == "PARTIAL_REFUNDED"
    assert validate_order_status("processing") == "PROCESSING"

    with pytest.raises(ValueError):
        validate_order_status("not-a-real-status")


def test_net_amount_rejects_refund_above_total() -> None:
    assert calculate_net_amount(Decimal("100.00"), Decimal("25.00")) == Decimal("75.00")

    with pytest.raises(ValueError):
        calculate_net_amount(Decimal("100.00"), Decimal("100.01"))


def test_analysis_window_is_local_date_half_open_and_utc() -> None:
    window = resolve_analysis_window(days=1, analysis_date=date(2024, 9, 17))

    assert window.from_utc.isoformat() == "2024-09-15T17:00:00+00:00"
    assert window.to_utc.isoformat() == "2024-09-16T17:00:00+00:00"


def test_model_acceptance_requires_baseline_and_lift() -> None:
    accepted = ModelLifecycleService.acceptance_passes(
        pr_auc=Decimal("0.31"),
        lift_top10=Decimal("2.0"),
        precision_top10=None,
        overall_conversion=None,
        baseline_pr_auc=Decimal("0.30"),
    )
    rejected = ModelLifecycleService.acceptance_passes(
        pr_auc=Decimal("0.30"),
        lift_top10=Decimal("2.0"),
        precision_top10=None,
        overall_conversion=None,
        baseline_pr_auc=Decimal("0.30"),
    )

    assert accepted is True
    assert rejected is False


def test_model_acceptance_applies_optional_precision_gate() -> None:
    assert (
        ModelLifecycleService.acceptance_passes(
            pr_auc=Decimal("0.31"),
            lift_top10=Decimal("2.0"),
            precision_top10=Decimal("0.21"),
            overall_conversion=Decimal("0.10"),
            baseline_pr_auc=Decimal("0.30"),
        )
        is True
    )
    assert (
        ModelLifecycleService.acceptance_passes(
            pr_auc=Decimal("0.31"),
            lift_top10=Decimal("2.0"),
            precision_top10=Decimal("0.19"),
            overall_conversion=Decimal("0.10"),
            baseline_pr_auc=Decimal("0.30"),
        )
        is False
    )
