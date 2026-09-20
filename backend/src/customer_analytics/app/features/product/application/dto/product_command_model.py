"""Product command models — Input DTOs for product operations."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreateModel(BaseModel):
    """DTO for creating a product."""

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


class ProductUpdateModel(BaseModel):
    """DTO for updating a product."""

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
