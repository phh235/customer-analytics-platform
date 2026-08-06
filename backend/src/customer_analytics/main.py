"""
FastAPI application entry point.

Khởi tạo app, đăng ký middleware, exception handlers, và router.
This file delegates to the new DDD structure in app/.
"""

from __future__ import annotations

# Re-export the app from the new DDD structure
from customer_analytics.app.main import app  # noqa: F401
