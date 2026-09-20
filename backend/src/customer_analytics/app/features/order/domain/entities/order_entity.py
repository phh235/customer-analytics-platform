"""Order entity — Domain entity for order."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from customer_analytics.app.features.order.domain.rules import (
    calculate_net_amount,
    validate_order_status,
)


class OrderItemEntity:
    """Order item entity."""

    def __init__(
        self,
        id_: str | None,
        order_id: str,
        product_id: str,
        quantity: int,
        unit_price: Decimal,
        subtotal: Decimal,
    ):
        self.id_ = id_
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = subtotal

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_": self.id_,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.subtotal,
        }


class OrderEntity:
    """Order entity — Represents an order in the system."""

    def __init__(
        self,
        id_: str | None,
        customer_id: str,
        order_number: str,
        order_date: datetime,
        total_amount: Decimal,
        status: str = "COMPLETED",
        channel: str | None = None,
        notes: str | None = None,
        items: list[OrderItemEntity] | None = None,
        refund_amount: Decimal = Decimal("0"),
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id_ = id_
        self.customer_id = customer_id
        self.order_number = order_number
        self.order_date = order_date
        self.total_amount = total_amount
        self.refund_amount = refund_amount
        self.net_amount = calculate_net_amount(total_amount, refund_amount)
        self.status = validate_order_status(status)
        self.channel = channel
        self.notes = notes
        self.items = items or []
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OrderEntity):
            return self.id_ == other.id_
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_": self.id_,
            "customer_id": self.customer_id,
            "order_number": self.order_number,
            "order_date": self.order_date,
            "total_amount": self.total_amount,
            "refund_amount": self.refund_amount,
            "net_amount": self.net_amount,
            "status": self.status,
            "channel": self.channel,
            "notes": self.notes,
            "items": [item.to_dict() for item in self.items],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
