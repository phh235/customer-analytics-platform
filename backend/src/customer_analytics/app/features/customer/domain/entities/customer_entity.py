"""Customer entity — Domain entity for customer."""

from __future__ import annotations

import copy
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class CustomerEntity:
    """Customer entity — Represents a customer in the system."""

    def __init__(
        self,
        id_: str | None,
        name: str,
        customer_code: str | None = None,
        image_url: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        status: str = "ACTIVE",
        gender: str | None = None,
        date_of_birth: date | None = None,
        region: str | None = None,
        customer_since: datetime | None = None,
        assigned_user_id: str | None = None,
        team_id: str | None = None,
        total_orders: int = 0,
        total_spent: Decimal = Decimal("0.00"),
        avg_order_value: Decimal = Decimal("0.00"),
        last_purchase_date: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self.id_ = id_
        self.customer_code = customer_code
        self.image_url = image_url
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.status = status
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.region = region
        self.customer_since = customer_since
        self.assigned_user_id = assigned_user_id
        self.team_id = team_id
        self.total_orders = total_orders
        self.total_spent = total_spent
        self.avg_order_value = avg_order_value
        self.last_purchase_date = last_purchase_date
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at

    def update(self, **kwargs: Any) -> CustomerEntity:
        """Update entity with new data."""
        updated = copy.deepcopy(self)
        for key, value in kwargs.items():
            if hasattr(updated, key) and value is not None:
                setattr(updated, key, value)
        return updated

    def disable(self) -> CustomerEntity:
        """Disable customer."""
        if self.status == "INACTIVE":
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message="Customer is already inactive",
            )
        entity = copy.deepcopy(self)
        entity.status = "INACTIVE"
        return entity

    def enable(self) -> CustomerEntity:
        """Enable customer."""
        if self.status == "ACTIVE":
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message="Customer is already active",
            )
        entity = copy.deepcopy(self)
        entity.status = "ACTIVE"
        return entity

    def update_stats(
        self,
        total_orders: int,
        total_spent: Decimal,
        avg_order_value: Decimal,
        last_purchase_date: datetime | None = None,
    ) -> CustomerEntity:
        """Update aggregated statistics."""
        entity = copy.deepcopy(self)
        entity.total_orders = total_orders
        entity.total_spent = total_spent
        entity.avg_order_value = avg_order_value
        entity.last_purchase_date = last_purchase_date
        return entity

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CustomerEntity):
            return self.id_ == other.id_
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "image_url": self.image_url,
            "id_": self.id_,
            "customer_code": self.customer_code,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "status": self.status,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "region": self.region,
            "customer_since": self.customer_since,
            "assigned_user_id": self.assigned_user_id,
            "team_id": self.team_id,
            "total_orders": self.total_orders,
            "total_spent": self.total_spent,
            "avg_order_value": self.avg_order_value,
            "last_purchase_date": self.last_purchase_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
