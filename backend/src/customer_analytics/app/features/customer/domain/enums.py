"""Customer domain enums."""

from __future__ import annotations

import enum


class CustomerStatus(enum.StrEnum):
    """Trạng thái khách hàng."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    VIP = "VIP"
