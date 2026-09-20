"""Customer schemas — Request/response models for customer API."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

# ── Request schemas ────────────────────────────────────────


class CustomerCreateRequest(BaseModel):
    """Create customer request body."""

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
    gender: str | None = Field(
        default=None,
        description="Gender (M/F/Other)",
        examples=["M"],
    )
    date_of_birth: date | None = Field(
        default=None,
        description="Date of birth",
        examples=["1990-01-15"],
    )
    region: str | None = Field(
        default=None,
        max_length=50,
        description="Region/City",
        examples=["Ho Chi Minh"],
    )


class CustomerUpdateRequest(BaseModel):
    """Update customer request body."""

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
    gender: str | None = Field(
        default=None,
        description="Gender (M/F/Other)",
    )
    date_of_birth: date | None = Field(
        default=None,
        description="Date of birth",
    )
    region: str | None = Field(
        default=None,
        max_length=50,
        description="Region/City",
    )


# ── Response schemas ───────────────────────────────────────


class CustomerResponse(BaseModel):
    """Customer info in response."""

    id: uuid.UUID = Field(..., description="Internal customer ID")
    customer_code: str = Field(..., description="Customer-facing reference code")
    name: str = Field(..., description="Customer name")
    image_url: str | None = Field(None, description="Cloudinary image URL")
    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    address: str | None = Field(None, description="Address")
    gender: str | None = Field(None, description="Gender")
    date_of_birth: date | None = Field(None, description="Date of birth")
    region: str | None = Field(None, description="Region/City")
    assigned_user_id: uuid.UUID | None = Field(
        None, description="Assigned analyst or service user"
    )
    team_id: uuid.UUID | None = Field(None, description="Assigned team")
    customer_since: datetime | None = Field(None, description="Customer since")
    total_orders: int = Field(0, description="Total orders")
    total_spent: Decimal = Field(Decimal("0.00"), description="Total spent")
    avg_order_value: Decimal = Field(Decimal("0.00"), description="Average order value")
    last_purchase_date: datetime | None = Field(None, description="Last purchase date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class PaginatedCustomersResponse(BaseModel):
    """Paginated customers list."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[CustomerResponse] = Field(..., description="Customer records")


# ── Error schemas ──────────────────────────────────────────


class CustomerErrorResponse(BaseModel):
    """Error response schema."""

    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Error type")
    path: str = Field(..., description="Request path")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    details: list[dict[str, str | int | None]] | None = Field(
        default=None, description="Error details"
    )
