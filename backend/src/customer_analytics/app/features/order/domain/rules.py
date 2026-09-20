"""Canonical order validity and monetary rules."""

from __future__ import annotations

from decimal import Decimal

from customer_analytics.app.config import settings

VALID_ORDER_STATUSES = frozenset(settings.VALID_ORDER_STATUSES)
INVALID_ORDER_STATUSES = frozenset(
    {"CANCELED", "CANCELLED", "FAILED", "REFUNDED", "RETURNED"}
)
NON_ANALYTIC_ORDER_STATUSES = frozenset({"PROCESSING"})
ALL_ORDER_STATUSES = (
    VALID_ORDER_STATUSES | INVALID_ORDER_STATUSES | NON_ANALYTIC_ORDER_STATUSES
)


def validate_order_status(status: str) -> str:
    """Normalize and validate an order status."""
    normalized = status.strip().upper()
    if normalized not in ALL_ORDER_STATUSES:
        raise ValueError(f"Unsupported order status: {status}")
    return normalized


def calculate_net_amount(total_amount: Decimal, refund_amount: Decimal) -> Decimal:
    """Calculate net amount and reject impossible refunds."""
    if refund_amount < 0 or refund_amount > total_amount:
        raise ValueError("refund_amount must be between 0 and total_amount")
    return total_amount - refund_amount
