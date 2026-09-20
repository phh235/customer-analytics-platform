"""Order database model — SQLAlchemy model."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from customer_analytics.app.features.product.infrastructure.models.product import (
        ProductModel,
    )


class OrderModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Order database model."""

    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "refund_amount >= 0 AND refund_amount <= total_amount",
            name="ck_orders_refund_amount_valid",
        ),
        CheckConstraint(
            "net_amount >= 0",
            name="ck_orders_net_amount_non_negative",
        ),
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id"), nullable=False, index=True
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    source_order_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    order_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    order_code: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_carrier_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_customer_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estimated_delivery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    freight_total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount_total: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sales_channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    province_city: Mapped[str | None] = mapped_column(String(150), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="VND")
    is_valid_for_rfm: Mapped[bool] = mapped_column(nullable=False, default=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0")
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="COMPLETED"
    )  # Includes PROCESSING for imported in-flight orders.
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    items: Mapped[list[OrderItemModel]] = relationship(
        "OrderItemModel", back_populates="order", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<OrderModel(id={self.id}, number='{self.order_number}')>"


class OrderItemModel(UUIDPrimaryKeyMixin, Base):
    """Order item database model."""

    __tablename__ = "order_items"
    __table_args__ = {"extend_existing": True}

    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False, index=True
    )
    seller_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("sellers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    item_sequence: Mapped[int | None] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    freight_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    discount_value: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    line_subtotal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    line_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    line_total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    shipping_limit_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped[OrderModel] = relationship("OrderModel", back_populates="items")
    product: Mapped[ProductModel] = relationship("ProductModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<OrderItemModel(id={self.id}, order_id={self.order_id})>"
