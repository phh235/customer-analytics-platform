"""
SQLAlchemy 2 async engine — singleton.

Tạo engine duy nhất cho toàn bộ ứng dụng.
Pool settings từ config, dễ tùy chỉnh per environment.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine

from customer_analytics.app.config import settings

# Singleton: tạo một engine duy nhất cho toàn bộ ứng dụng
engine = create_async_engine(
    settings.database_url,
    echo=settings.APP_DEBUG,
    # Pool settings từ config
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    # Disable statement caching to avoid InvalidCachedStatementError
    # after schema changes (e.g., running migrations)
    connect_args={"statement_cache_size": 0},
)
