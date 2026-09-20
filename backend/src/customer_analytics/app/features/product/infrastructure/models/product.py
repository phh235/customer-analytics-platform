"""Product database model — SQLAlchemy model."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ProductModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Product database model."""

    __tablename__ = "products"
    __table_args__ = (
        Index("uq_products_sku", "sku", unique=True),
        {"extend_existing": True},
    )

    source_product_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    product_code: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    sku: Mapped[str | None] = mapped_column(String(64), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_category_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    list_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="VND")
    weight_g: Mapped[Decimal | None] = mapped_column(Numeric(12, 3), nullable=True)
    length_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    width_cm: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    photo_count: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ACTIVE"
    )  # ACTIVE/INACTIVE
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)

    def __repr__(self) -> str:
        return f"<ProductModel(id={self.id}, name='{self.name}')>"
