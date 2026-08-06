"""
Health check endpoint — dùng để monitoring và Docker healthcheck.

GET  /health       → Basic health (không cần DB)
GET  /api/v1/health → Full health (có kiểm tra DB)
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from customer_analytics.app.config import settings
from customer_analytics.core.database import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", response_model=dict[str, str | int])
def health_basic() -> dict[str, str | int]:
    """Basic health check — không phụ thuộc database."""
    return {
        "status": "UP",
        "version": settings.APP_VERSION,
    }


@router.get("/api/v1/health", response_model=dict[str, Any])
async def health_full() -> dict[str, Any]:
    """Full health check — kiểm tra kết nối database."""
    db_ok = await check_db_connection()
    return {
        "status": "UP" if db_ok else "DEGRADED",
        "version": settings.APP_VERSION,
        "checks": {
            "database": "UP" if db_ok else "DOWN",
        },
    }
