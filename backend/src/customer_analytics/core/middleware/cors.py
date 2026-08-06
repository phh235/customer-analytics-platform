"""
CORS middleware — cấu hình Cross-Origin Resource Sharing.

Chỉ thêm middleware nếu BACKEND_CORS_ORIGINS không rỗng.

IMPORTANT: allow_credentials=True is required for HTTP-only cookies.
When using cookies for auth, CORS must be properly configured:
- allow_credentials=True (allows cookies)
- allow_origins must NOT be ["*"] in production (browsers reject it)
- In production, list specific frontend origins
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from customer_analytics.app.config import settings


def build_cors_middleware(app: FastAPI) -> None:
    """Đăng ký CORS middleware nếu có origins cấu hình."""
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,  # Required for HTTP-only cookies
            allow_methods=["*"],
            allow_headers=["*"],
        )
