"""
AsyncSession management — session factory, dependency, health check.

Session per request: dependency tạo session, service layer controls commit/rollback.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from customer_analytics.core.database.engine import engine

# ── Session factory ─────────────────────────────────
# async_sessionmaker() tạo session mới mỗi lần gọi
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Không expire object sau commit
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency — tạo session cho mỗi request.

    Session tự động close khi request kết thúc.
    Service layer sẽ quyết định khi nào commit/rollback.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            # Không auto-commit — để service layer quyết định
        except Exception:
            await session.rollback()
            raise


async def check_db_connection() -> bool:
    """Kiểm tra kết nối database — dùng cho health check."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
