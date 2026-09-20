"""Product query models — Output DTOs for product operations."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductReadModel(BaseModel):
    """DTO for reading product data."""

    id: str = Field(..., description="Internal product ID")
    product_code: str = Field(..., description="Product-facing reference code")
    name: str = Field(..., description="Product name")
    sku: str | None = Field(None, description="Stock keeping unit")
    category: str = Field(..., description="Product category")
    description: str | None = Field(None, description="Product description")
    image_url: str | None = Field(None, description="Cloudinary image URL")
    price: Decimal = Field(..., description="Product price")
    status: str = Field(..., description="Product status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_entity(cls, entity) -> ProductReadModel:
        """Create read model from entity."""
        return cls(
            product_code=entity.product_code,
            id=entity.id_,
            name=entity.name,
            sku=entity.sku,
            category=entity.category,
            description=entity.description,
            image_url=entity.image_url,
            price=entity.price,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class ProductListResult(BaseModel):
    """Paginated product list result."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[ProductReadModel] = Field(..., description="Product records")
