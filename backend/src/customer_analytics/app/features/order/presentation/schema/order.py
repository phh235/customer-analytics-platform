"""Order schemas — Request/response models for order API."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

# ── Request schemas ────────────────────────────────────────


class OrderItemCreateRequest(BaseModel):
    """Create order item request body."""

    product_id: uuid.UUID = Field(
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


class OrderCreateRequest(BaseModel):
    """Create order request body."""

    customer_id: uuid.UUID = Field(
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
        description="Order notes",
    )
    items: list[OrderItemCreateRequest] = Field(
        ...,
        min_length=1,
        description="Order items",
    )


class OrderUpdateRequest(BaseModel):
    """Update order request body."""

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
        description="Order notes",
    )


# ── Response schemas ───────────────────────────────────────


class OrderItemResponse(BaseModel):
    """Order item info in response."""

    id: uuid.UUID = Field(..., description="Order item ID")
    order_id: uuid.UUID = Field(..., description="Order ID")
    product_id: uuid.UUID = Field(..., description="Product ID")
    quantity: int = Field(..., description="Quantity")
    unit_price: Decimal = Field(..., description="Unit price")
    subtotal: Decimal = Field(..., description="Subtotal")

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """Order info in response."""

    id: uuid.UUID = Field(..., description="Order ID")
    customer_id: uuid.UUID = Field(..., description="Customer ID")
    order_number: str = Field(..., description="Order number")
    order_date: datetime = Field(..., description="Order date")
    total_amount: Decimal = Field(..., description="Total amount")
    refund_amount: Decimal = Field(..., description="Refund amount")
    net_amount: Decimal = Field(..., description="Net amount after refund")
    status: str = Field(..., description="Order status")
    channel: str | None = Field(None, description="Order channel")
    notes: str | None = Field(None, description="Order notes")
    items: list[OrderItemResponse] = Field(
        default_factory=list, description="Order items"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class PaginatedOrdersResponse(BaseModel):
    """Paginated orders list."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[OrderResponse] = Field(..., description="Order records")


# ── Error schemas ──────────────────────────────────────────


class OrderErrorResponse(BaseModel):
    """Error response schema."""

    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Error type")
    path: str = Field(..., description="Request path")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    details: list[dict[str, str | int | None]] | None = Field(
        default=None, description="Error details"
    )
