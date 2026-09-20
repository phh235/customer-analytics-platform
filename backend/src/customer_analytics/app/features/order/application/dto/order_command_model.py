"""Order command models — Input DTOs for order operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItemCreateModel(BaseModel):
    """DTO for creating an order item."""

    product_id: str = Field(
        ...,
        description="Product ID",
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity",
        examples=[1],
    )
    unit_price: Decimal = Field(
        ...,
        gt=0,
        description="Unit price",
        examples=[29990000],
    )


class OrderCreateModel(BaseModel):
    """DTO for creating an order."""

    customer_id: str = Field(
        ...,
        description="Customer ID",
    )
    order_date: datetime = Field(
        ...,
        description="Order date",
    )
    refund_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Refund amount",
    )
    channel: str | None = Field(
        default=None,
        max_length=50,
        description="Order channel (online/pos/phone)",
        examples=["online"],
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Order notes",
    )
    items: list[OrderItemCreateModel] = Field(
        ...,
        min_length=1,
        description="Order items",
    )


class OrderUpdateModel(BaseModel):
    """DTO for updating an order."""

    status: str | None = Field(
        default=None,
        description="Order status",
    )
    refund_amount: Decimal | None = Field(
        default=None,
        ge=0,
        description="Refund amount",
    )
    notes: str | None = Field(
        default=None,
        max_length=2000,
        description="Order notes",
    )
