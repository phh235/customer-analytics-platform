"""
Reusable ORM mixins cho các common columns.

Dùng kết hợp với Base để tạo model:
    class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
        __tablename__ = "users"
        ...
"""

from __future__ import annotations

import uuid
from datetime import datetime

import uuid_utils
from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKeyMixin:
    """Mixin tạo cột `id` UUIDv7 làm primary key tự động."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid_utils.uuid7,
    )


class TimestampMixin:
    """Mixin tạo 2 cột `created_at` và `updated_at` tự động quản lý."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
