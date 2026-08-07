"""
Rate limiting middleware — using slowapi.

Endpoints quan trọng cần rate limit:
- POST /auth/login:防止 brute force attack
- POST /auth/refresh:防止 token theft
- POST /auth/register:防止 spam account

Usage:
    from customer_analytics.core.middleware.rate_limit import limiter

    @router.post("/login")
    @limiter.limit("5/minute")
    async def login(request: Request, ...):
        ...
"""

from __future__ import annotations

import structlog
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = structlog.get_logger(__name__)


def get_remote_address_with_xff(request) -> str:
    """Get client IP, support X-Forwarded-For for reverse proxy."""
    # Check X-Forwarded-For header first (for nginx/cloudflare)
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # Take first IP (original client)
        return xff.split(",")[0].strip()
    return get_remote_address(request)


# Limiter instance — import ở mọi nơi để dùng @limiter.limit()
limiter = Limiter(
    key_func=get_remote_address_with_xff,
    # Storage: in-memory (default) hoặc Redis
    # storage_uri="redis://localhost:6379",
)


def setup_rate_limiting(app) -> None:
    """Setup rate limiting for FastAPI app."""
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware

    from customer_analytics.app.shared.errors import ErrorCode
    from customer_analytics.app.shared.exceptions import AppException

    # Add limiter to app state
    app.state.limiter = limiter

    # Custom exception handler — convert to our AppException format
    async def rate_limit_exceeded_handler(request, exc):
        """Handle rate limit exceeded."""
        logger.warning(
            "rate_limit_exceeded",
            path=request.url.path,
            method=request.method,
            detail=str(exc.detail),
        )
        raise AppException(
            error_code=ErrorCode.TOO_MANY_REQUESTS,
            message=f"Quá nhiều requests. Vui lòng thử lại sau. {exc.detail}",
        )

    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Add middleware
    app.add_middleware(SlowAPIMiddleware)


__all__ = ["limiter", "setup_rate_limiting"]
