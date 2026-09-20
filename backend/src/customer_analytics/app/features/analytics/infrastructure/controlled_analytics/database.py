"""Dedicated read-only database connection for AI analytics queries."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from customer_analytics.app.config import settings
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


@lru_cache(maxsize=1)
def get_analytics_engine() -> AsyncEngine | None:
    """Create the AI database engine only when a separate URL is configured."""
    if not settings.AI_ANALYTICS_DATABASE_URL:
        return None
    analytics_url = make_url(settings.AI_ANALYTICS_DATABASE_URL)
    if analytics_url.host and "@" in analytics_url.host:
        password_suffix, host = analytics_url.host.rsplit("@", 1)
        analytics_url = analytics_url.set(
            password=f"{analytics_url.password or ''}@{password_suffix}",
            host=host,
        )
    if analytics_url.host == "localhost":
        analytics_url = analytics_url.set(host="127.0.0.1")
    return create_async_engine(
        analytics_url,
        pool_size=2,
        max_overflow=0,
        pool_pre_ping=True,
        pool_timeout=5,
        pool_recycle=300,
        connect_args={"statement_cache_size": 0},
    )


@asynccontextmanager
async def analytics_session_context() -> AsyncGenerator[AsyncSession]:
    """Open a session backed by the dedicated analytics database."""
    engine = get_analytics_engine()
    if engine is None:
        raise AppException(
            ErrorCode.SERVICE_UNAVAILABLE,
            message="Controlled analytics database is not configured.",
        )

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_analytics_session() -> AsyncGenerator[AsyncSession]:
    """Yield a session backed by the dedicated analytics database."""
    async with analytics_session_context() as session:
        yield session


AnalyticsSessionDep = Annotated[
    AsyncSession,
    Depends(get_analytics_session),
]
