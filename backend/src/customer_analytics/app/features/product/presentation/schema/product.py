"""Product schemas — Request/response models for product API."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

# ── Request schemas ────────────────────────────────────────


class ProductCreateRequest(BaseModel):
    """Create product request body."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Product name",
        examples=["iPhone 15 Pro"],
    )
    sku: str | None = Field(
        default=None,
        max_length=64,
        description="Stock keeping unit",
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Product category",
        examples=["Electronics"],
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Product description",
    )
    image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary image URL",
    )
    price: Decimal = Field(
        ...,
        gt=0,
        description="Product price",
        examples=[29990000],
    )
    status: str = Field(
        default="ACTIVE",
        description="Product status (ACTIVE, INACTIVE)",
    )


class ProductUpdateRequest(BaseModel):
    """Update product request body."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Product name",
    )
    sku: str | None = Field(
        default=None,
        max_length=64,
        description="Stock keeping unit",
    )
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Product category",
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Product description",
    )
    image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary image URL",
    )
    price: Decimal | None = Field(
        default=None,
        gt=0,
        description="Product price",
    )
    status: str | None = Field(
        default=None,
        description="Product status (ACTIVE, INACTIVE)",
    )


# ── Response schemas ───────────────────────────────────────


class ProductResponse(BaseModel):
    """Product info in response."""

    id: uuid.UUID = Field(..., description="Internal product ID")
    product_code: str = Field(..., description="Product-facing reference code")
    name: str = Field(..., description="Product name")
    sku: str | None = Field(None, description="Stock keeping unit")
    category: str = Field(..., description="Product category")
    description: str | None = Field(None, description="Product description")
    image_url: str | None = Field(None, description="Cloudinary image URL")
    price: Decimal = Field(..., description="Product price")
    status: str = Field(..., description="Product status (ACTIVE, INACTIVE)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ProductDetailResponse(ProductResponse):
    """Product response with related products for the detail page."""

    related_products: list[ProductResponse] = Field(default_factory=list)


class PaginatedProductsResponse(BaseModel):
    """Paginated products list."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[ProductResponse] = Field(..., description="Product records")


class ProductViewRecordedResponse(BaseModel):
    """Confirmation returned after recording a product view."""

    event_id: uuid.UUID
    interaction_type: str = "product_view"


# ── Error schemas ──────────────────────────────────────────


class ProductErrorResponse(BaseModel):
    """Error response schema."""

    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Error type")
    path: str = Field(..., description="Request path")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    details: list[dict[str, str | int | None]] | None = Field(
        default=None, description="Error details"
    )
