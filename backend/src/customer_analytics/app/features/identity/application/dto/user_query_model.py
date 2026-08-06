"""User query models — Output models for user queries."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UserReadModel(BaseModel):
    """Model for reading user data."""

    id: uuid.UUID = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    full_name: str = Field(..., description="Full name")
    status: str = Field(..., description="Account status")
    role_code: str = Field(..., description="Role code")
    permissions: list[str] = Field(default_factory=list, description="User permissions")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_login_at: datetime | None = Field(None, description="Last login timestamp")

    @classmethod
    def from_entity(
        cls, entity: Any, permissions: list[str] | None = None
    ) -> UserReadModel:
        """Create read model from entity."""
        return cls(
            id=entity.id_,
            email=entity.email,
            full_name=entity.full_name,
            status=entity.status,
            role_code=entity.role_code,
            permissions=permissions or [],
            created_at=entity.created_at,
            last_login_at=entity.last_login_at,
        )


class UserListReadModel(BaseModel):
    """Model for listing users with pagination."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[UserReadModel] = Field(..., description="User records")
