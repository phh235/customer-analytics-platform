"""
Middleware registration — tập trung thứ tự đăng ký tại đây.

Thứ tự quan trọng:
1. CORS (outermost) — xử lý preflight, headers trước khi request vào app
2. RequestID (innermost) — gắn request_id ngay trước khi request chạm handler
"""

from __future__ import annotations

from fastapi import FastAPI

from customer_analytics.core.middleware.cors import build_cors_middleware
from customer_analytics.core.middleware.request_id import (
    RequestIDMiddleware,
)


def register_middleware(app: FastAPI) -> None:
    """Đăng ký tất cả middleware theo đúng thứ tự. Gọi một lần khi khởi động app."""
    build_cors_middleware(app)  # CORS trước (outermost)
    app.add_middleware(RequestIDMiddleware)  # RequestID sau


__all__ = ["RequestIDMiddleware", "register_middleware"]
