"""Customer command models — Input DTOs for customer operations."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class CustomerCreateModel(BaseModel):
    """DTO for creating a customer."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Customer name",
        examples=["Nguyen Van A"],
    )
    email: EmailStr | None = Field(
        default=None,
        description="Email address",
        examples=["customer@example.com"],
    )
    image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary image URL",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        description="Phone number",
        examples=["0901234567"],
    )
    address: str | None = Field(
        default=None,
        max_length=255,
        description="Address",
        examples=["123 Nguyen Hue, Q1, TP.HCM"],
    )


class CustomerUpdateModel(BaseModel):
    """DTO for updating a customer."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Customer name",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Email address",
    )
    image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary image URL",
    )
    phone: str | None = Field(
        default=None,
        max_length=20,
        description="Phone number",
    )
    address: str | None = Field(
        default=None,
        max_length=255,
        description="Address",
    )
    status: str | None = Field(
        default=None,
        description="Status (ACTIVE, INACTIVE, VIP)",
    )
