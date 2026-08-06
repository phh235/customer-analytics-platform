"""
Shared FastAPI dependencies.

Dùng typing.Annotated kết hợp Depends để tạo type alias tái sử dụng.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.core.database import get_db

# Type alias cho DB session dependency
# Dùng: async def handler(db: DatabaseSessionDep):
DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db)]
