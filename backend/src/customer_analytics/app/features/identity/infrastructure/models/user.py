"""User database model — SQLAlchemy model."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from customer_analytics.app.features.identity.domain.enums import UserStatus
from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class TeamModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Team used by manager-level data scoping."""

    __tablename__ = "teams"
    __table_args__ = {"extend_existing": True}

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class UserModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """User database model."""

    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    failed_login_count: Mapped[int] = mapped_column(default=0, nullable=False)
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    team_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── OAuth2 fields ──────────────────────────────────────
    google_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True, index=True
    )
    auth_provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="local",  # "local" | "google"
    )

    # Relationships
    role: Mapped[RoleModel] = relationship("RoleModel", lazy="selectin")

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email}')>"


class RoleModel(UUIDPrimaryKeyMixin, Base):
    """Role database model."""

    __tablename__ = "roles"
    __table_args__ = {"extend_existing": True}

    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    permissions: Mapped[list[PermissionModel]] = relationship(
        "PermissionModel",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<RoleModel(id={self.id}, code='{self.code}')>"


class PermissionModel(UUIDPrimaryKeyMixin, Base):
    """Permission database model."""

    __tablename__ = "permissions"
    __table_args__ = {"extend_existing": True}

    code: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    roles: Mapped[list[RoleModel]] = relationship(
        "RoleModel",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<PermissionModel(id={self.id}, code='{self.code}')>"


class RolePermissionModel(Base):
    """Role-Permission association table."""

    __tablename__ = "role_permissions"
    __table_args__ = {"extend_existing": True}

    role_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
