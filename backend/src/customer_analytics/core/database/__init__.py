"""
Database infrastructure — engine, Base, session, mixins.

Import từ đây để truy cập tất cả thành phần database:
    from customer_analytics.core.database import Base, engine, get_db
"""

from __future__ import annotations

from customer_analytics.core.database.base import Base, metadata_obj
from customer_analytics.core.database.engine import engine
from customer_analytics.core.database.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from customer_analytics.core.database.session import (
    AsyncSessionFactory,
    check_db_connection,
    get_db,
)

__all__ = [
    "AsyncSessionFactory",
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "check_db_connection",
    "engine",
    "get_db",
    "metadata_obj",
]
