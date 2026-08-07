"""
Alembic environment configuration.

Kết nối với SQLAlchemy metadata của project và lấy database URL từ settings.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context

# Import project modules
from customer_analytics.configuration.database import Base
from customer_analytics.configuration.settings import settings

# Import all ORM models so Alembic can detect them
from customer_analytics.identity.domain.entities import (  # noqa: F401
    Permission,
    Role,
    RolePermission,
    User,
)
from sqlalchemy.ext.asyncio import create_async_engine

# Alembic Config object
config = context.config

# Cấu hình logging từ alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Gắn metadata — để Alembic tự động phát hiện thay đổi model
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Chạy migration ở offline mode (không cần database).

    Dùng khi muốn generate SQL script mà không chạy thật.
    """
    url = settings.database_url_sync
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Chạy migration trên một connection có sẵn."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Chạy migration ở online mode — kết nối database thật."""
    # Dùng async engine với URL async (có +asyncpg)
    connectable = create_async_engine(settings.database_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
