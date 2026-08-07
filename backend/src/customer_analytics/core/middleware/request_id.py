"""
Request ID middleware — gắn request_id vào mọi request.

Logic:
1. Nếu Client gửi header `X-Request-ID` → dùng cái đó (để client report lỗi)
2. Nếu Client không gửi → tự sinh UUID7 mới
3. Response luôn trả về `X-Request-ID` trong header
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

import structlog
import uuid_utils
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware gán request_id cho mỗi HTTP request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # 1. Lấy request_id từ client hoặc tự sinh
        request_id = request.headers.get("x-request-id") or str(uuid_utils.uuid7())

        # 2. Gán vào structlog context — mọi log trong request sẽ có request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # 3. Xử lý request và đo thời gian
        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception:
            # Nếu exception không được handler bắt, vẫn log và re-raise
            logger.exception("unhandled_middleware_error")
            raise

        # 4. Gắn request_id vào response header
        response.headers["X-Request-ID"] = request_id

        # 5. Log request info
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=f"{duration_ms:.0f}",
        )

        # 6. Dọn context — tránh rò rỉ request_id sang request khác
        structlog.contextvars.clear_contextvars()

        return response
