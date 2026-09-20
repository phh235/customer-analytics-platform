"""Product entity — Domain entity for product."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any


class ProductEntity:
    """Product entity — Represents a product in the system."""

    def __init__(
        self,
        id_: str | None,
        name: str,
        category: str,
        price: Decimal,
        product_code: str | None = None,
        status: str = "ACTIVE",
        sku: str | None = None,
        description: str | None = None,
        image_url: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.product_code = product_code
        self.id_ = id_
        self.name = name
        self.category = category
        self.price = price
        self.status = status
        self.sku = sku
        self.description = description
        self.image_url = image_url
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProductEntity):
            return self.id_ == other.id_
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_code": self.product_code,
            "id_": self.id_,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "status": self.status,
            "sku": self.sku,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
