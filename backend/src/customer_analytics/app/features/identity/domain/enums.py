"""Identity domain enums — Status codes and permission actions."""

from __future__ import annotations

import enum


class UserStatus(enum.StrEnum):
    """Trạng thái tài khoản người dùng."""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    LOCKED = "LOCKED"


class PermissionAction(enum.StrEnum):
    """Các hành động quyền hạn cơ bản."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    PREDICT = "predict"
