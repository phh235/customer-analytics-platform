"""User query models — Output models for user queries."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

UserRoleFilter = Literal["ADMIN", "ANALYST", "CLIENT"]
UserStatusFilter = Literal["ACTIVE", "DISABLED", "LOCKED"]
UserSortField = Literal["created_at", "full_name", "last_login_at"]
SortOrder = Literal["asc", "desc"]


class UserListQueryModel(BaseModel):
    """Validated filters and ordering for the paginated user list."""

    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    search: str | None = None
    role_code: UserRoleFilter | None = None
    status: UserStatusFilter | None = None
    sort_by: UserSortField = "created_at"
    sort_order: SortOrder = "desc"


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
