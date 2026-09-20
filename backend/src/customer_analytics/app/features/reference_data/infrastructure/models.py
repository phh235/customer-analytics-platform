"""Source and reference data models from the aligned dataset contract."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class EmployeeModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Employee owner and data-scope reference."""

    __tablename__ = "employees"

    employee_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    region_scope: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ACTIVE", index=True
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)


class SellerModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Seller reference from order detail data."""

    __tablename__ = "sellers"

    seller_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    seller_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)


class GeolocationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Postal-code geolocation reference."""

    __tablename__ = "geolocations"

    zip_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)


class CampaignModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Campaign reference used by customer interactions."""

    __tablename__ = "campaigns"

    campaign_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    campaign_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_segment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    budget_vnd: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)


class PaymentModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Payment transaction belonging to an order."""

    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "payment_sequence",
            name="uq_payments_order_sequence",
        ),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_installments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payment_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="VND")


class ReviewModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Customer review attached to an order."""

    __tablename__ = "reviews"

    review_code: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    review_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class CustomerInteractionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Mock or production customer interaction event."""

    __tablename__ = "customer_interactions"
    __table_args__ = (
        Index("ix_customer_interactions_timestamp", "interaction_timestamp"),
    )

    interaction_code: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    interaction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    interaction_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), nullable=False, default=Decimal("0")
    )
    interaction_result: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_mock_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
