"""Order query models — Output DTOs for order operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderItemReadModel(BaseModel):
    """DTO for reading order item data."""

    id: str = Field(..., description="Order item ID")
    order_id: str = Field(..., description="Order ID")
    product_id: str = Field(..., description="Product ID")
    quantity: int = Field(..., description="Quantity")
    unit_price: Decimal = Field(..., description="Unit price")
    subtotal: Decimal = Field(..., description="Subtotal")

    @classmethod
    def from_entity(cls, entity) -> OrderItemReadModel:
        """Create read model from entity."""
        return cls(
            id=entity.id_,
            order_id=entity.order_id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            unit_price=entity.unit_price,
            subtotal=entity.subtotal,
        )


class OrderReadModel(BaseModel):
    """DTO for reading order data."""

    id: str = Field(..., description="Order ID")
    customer_id: str = Field(..., description="Customer ID")
    order_number: str = Field(..., description="Order number")
    order_date: datetime = Field(..., description="Order date")
    total_amount: Decimal = Field(..., description="Total amount")
    refund_amount: Decimal = Field(..., description="Refund amount")
    net_amount: Decimal = Field(..., description="Net amount after refund")
    status: str = Field(..., description="Order status")
    channel: str | None = Field(None, description="Order channel")
    notes: str | None = Field(None, description="Order notes")
    items: list[OrderItemReadModel] = Field(
        default_factory=list, description="Order items"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_entity(cls, entity) -> OrderReadModel:
        """Create read model from entity."""
        return cls(
            id=entity.id_,
            customer_id=entity.customer_id,
            order_number=entity.order_number,
            order_date=entity.order_date,
            total_amount=entity.total_amount,
            refund_amount=entity.refund_amount,
            net_amount=entity.net_amount,
            status=entity.status,
            channel=entity.channel,
            notes=entity.notes,
            items=[OrderItemReadModel.from_entity(item) for item in entity.items],
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class OrderListResult(BaseModel):
    """Paginated order list result."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[OrderReadModel] = Field(..., description="Order records")
