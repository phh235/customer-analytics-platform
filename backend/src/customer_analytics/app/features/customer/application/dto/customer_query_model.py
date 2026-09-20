"""Customer query models — Output DTOs for customer operations."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CustomerReadModel(BaseModel):
    """DTO for reading customer data."""

    id: str = Field(..., description="Internal customer ID")
    customer_code: str = Field(..., description="Customer-facing reference code")
    name: str = Field(..., description="Customer name")
    image_url: str | None = Field(None, description="Cloudinary image URL")
    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    address: str | None = Field(None, description="Address")
    status: str = Field(..., description="Account status")
    gender: str | None = Field(None, description="Gender")
    date_of_birth: date | None = Field(None, description="Date of birth")
    region: str | None = Field(None, description="Region/City")
    assigned_user_id: str | None = Field(None, description="Assigned user ID")
    team_id: str | None = Field(None, description="Assigned team ID")
    customer_since: datetime | None = Field(None, description="Customer since")
    total_orders: int = Field(0, description="Total orders")
    total_spent: Decimal = Field(Decimal("0.00"), description="Total spent")
    avg_order_value: Decimal = Field(Decimal("0.00"), description="Average order value")
    last_purchase_date: datetime | None = Field(None, description="Last purchase date")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_entity(cls, entity) -> CustomerReadModel:
        return cls(
            id=entity.id_,
            customer_code=entity.customer_code,
            name=entity.name,
            image_url=entity.image_url,
            email=entity.email,
            phone=entity.phone,
            address=entity.address,
            status=entity.status,
            gender=entity.gender,
            date_of_birth=entity.date_of_birth,
            region=entity.region,
            assigned_user_id=entity.assigned_user_id,
            team_id=entity.team_id,
            customer_since=entity.customer_since,
            total_orders=entity.total_orders,
            total_spent=entity.total_spent,
            avg_order_value=entity.avg_order_value,
            last_purchase_date=entity.last_purchase_date,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class CustomerListResult(BaseModel):
    """Paginated customer list result."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[CustomerReadModel] = Field(..., description="Customer records")
