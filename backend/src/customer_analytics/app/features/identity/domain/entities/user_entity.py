"""User entity — Domain entity for user."""

from __future__ import annotations

import copy
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException

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
        role_code: str = "USER",
        role_id: str | None = None,
        permissions: list[str] | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        last_login_at: datetime | None = None,
        failed_login_count: int = 0,
        locked_until: datetime | None = None,
        google_id: str | None = None,
        auth_provider: str = "local",
        team_id: str | None = None,
        customer_id: str | None = None,
    ):
        self.id_ = id_
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.status = status
        self.role_code = role_code
        self.role_id = role_id
        self.permissions = permissions or []
        self.is_active = is_active
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at
        self.last_login_at = last_login_at
        self.failed_login_count = failed_login_count
        self.locked_until = locked_until
        self.google_id = google_id
        self.auth_provider = auth_provider
        self.team_id = team_id
        self.customer_id = customer_id

    def update_entity(
        self,
        entity_update_model: UserUpdateModel,
        get_update_data_fn: Any,
    ) -> UserEntity:
        """Update entity with new data."""
        update_data = get_update_data_fn(entity_update_model)
        updated_entity = copy.deepcopy(self)

        for attr_name, value in update_data.items():
            setattr(updated_entity, attr_name, value)

        return updated_entity

    def _set_status(self, new_status: str) -> UserEntity:
        """Set user status (internal method for disable/enable)."""
        if self.status == new_status:
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message=f"User is already {new_status.lower()}",
            )

        entity = copy.deepcopy(self)
        entity.status = new_status
        entity.is_active = new_status == "ACTIVE"

        if new_status == "ACTIVE":
            entity.failed_login_count = 0
            entity.locked_until = None

        return entity

    def mark_entity_as_deleted(self) -> UserEntity:
        """Mark entity as deleted (soft delete)."""
        return self._set_status("DISABLED")

    def disable(self) -> UserEntity:
        """Disable user account."""
        return self._set_status("DISABLED")

    def enable(self) -> UserEntity:
        """Enable user account."""
        return self._set_status("ACTIVE")

    def record_failed_login(self) -> UserEntity:
        """Record a failed login attempt."""
        updated_entity = copy.deepcopy(self)
        updated_entity.failed_login_count += 1

        if updated_entity.failed_login_count >= 5:
            updated_entity.status = "LOCKED"
            updated_entity.locked_until = datetime.now(UTC) + timedelta(minutes=15)

        return updated_entity

    def record_successful_login(self) -> UserEntity:
        """Record a successful login."""
        updated_entity = copy.deepcopy(self)
        updated_entity.failed_login_count = 0
        updated_entity.locked_until = None
        updated_entity.last_login_at = datetime.now(UTC)

        return updated_entity

    def update(
        self,
        google_id: str | None = None,
        auth_provider: str | None = None,
    ) -> UserEntity:
        """Update user with OAuth2 data."""
        updated_entity = copy.deepcopy(self)

        if google_id is not None:
            updated_entity.google_id = google_id
        if auth_provider is not None:
            updated_entity.auth_provider = auth_provider

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
            "role_id": self.role_id,
            "permissions": self.permissions,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login_at": self.last_login_at,
            "failed_login_count": self.failed_login_count,
            "locked_until": self.locked_until,
            "google_id": self.google_id,
            "customer_id": self.customer_id,
            "auth_provider": self.auth_provider,
            "team_id": self.team_id,
        }
