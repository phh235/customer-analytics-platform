"""User entity — Domain entity for user."""

from __future__ import annotations

import copy
from datetime import datetime
from typing import TYPE_CHECKING, Any

from customer_analytics.core.error.exception import InvalidOperationError

if TYPE_CHECKING:
    from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
        UserUpdateModel,
    )


class UserEntity:
    """User entity — Represents a user in the system."""

    def __init__(
        self,
        id_: str | None,
        email: str,
        password_hash: str,
        full_name: str,
        status: str = "ACTIVE",
        role_code: str = "ANALYST",
        permissions: list[str] | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_login_at: datetime | None = None,
        failed_login_count: int = 0,
        locked_until: datetime | None = None,
    ):
        self.id_ = id_
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.status = status
        self.role_code = role_code
        self.permissions = permissions or []
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
        self.last_login_at = last_login_at
        self.failed_login_count = failed_login_count
        self.locked_until = locked_until

    def update_entity(
        self,
        entity_update_model: UserUpdateModel,
        get_update_data_fn: Any,
    ) -> UserEntity:
        """Update entity with new data."""
        update_data = get_update_data_fn(entity_update_model)
        update_entity = copy.deepcopy(self)

        for attr_name, value in update_data.items():
            update_entity.__setattr__(attr_name, value)

        return update_entity

    def mark_entity_as_deleted(self) -> UserEntity:
        """Mark entity as deleted (soft delete)."""
        if self.status == "DISABLED":
            raise InvalidOperationError("User is already disabled")

        marked_entity = copy.deepcopy(self)
        marked_entity.status = "DISABLED"
        marked_entity.is_active = False

        return marked_entity

    def disable(self) -> UserEntity:
        """Disable user account."""
        if self.status == "DISABLED":
            raise InvalidOperationError("User is already disabled")

        disabled_entity = copy.deepcopy(self)
        disabled_entity.status = "DISABLED"
        disabled_entity.is_active = False

        return disabled_entity

    def enable(self) -> UserEntity:
        """Enable user account."""
        if self.status == "ACTIVE":
            raise InvalidOperationError("User is already active")

        enabled_entity = copy.deepcopy(self)
        enabled_entity.status = "ACTIVE"
        enabled_entity.is_active = True
        enabled_entity.failed_login_count = 0
        enabled_entity.locked_until = None

        return enabled_entity

    def record_failed_login(self) -> UserEntity:
        """Record a failed login attempt."""
        updated_entity = copy.deepcopy(self)
        updated_entity.failed_login_count += 1

        if updated_entity.failed_login_count >= 5:
            from datetime import timedelta

            updated_entity.status = "LOCKED"
            updated_entity.locked_until = datetime.utcnow() + timedelta(minutes=15)

        return updated_entity

    def record_successful_login(self) -> UserEntity:
        """Record a successful login."""
        updated_entity = copy.deepcopy(self)
        updated_entity.failed_login_count = 0
        updated_entity.locked_until = None
        updated_entity.last_login_at = datetime.utcnow()

        return updated_entity

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UserEntity):
            return self.id_ == other.id_
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id_": self.id_,
            "email": self.email,
            "password_hash": self.password_hash,
            "full_name": self.full_name,
            "status": self.status,
            "role_code": self.role_code,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login_at": self.last_login_at,
            "failed_login_count": self.failed_login_count,
            "locked_until": self.locked_until,
        }
