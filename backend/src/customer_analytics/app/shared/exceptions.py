"""
Application exception hierarchy and FastAPI exception handlers.

Mọi business error đều dùng AppException, không dùng raw HTTP exceptions.
Exception handlers tự động format response đồng nhất.
"""

from __future__ import annotations

import time
from http import HTTPStatus
from typing import Any

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.schemas import (
    ErrorDetail,
    ErrorResponse,
)

logger = structlog.get_logger(__name__)


class AppException(Exception):
    """Base business exception — xuyên suốt toàn bộ ứng dụng.

    Usage:
        raise AppException(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message="Email hoặc mật khẩu không chính xác.",
        )
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str | None = None,
        details: Any = None,
        status_code: int | None = None,
    ):
        super().__init__(message or error_code.message)
        self.error_code = error_code
        self.message = message or error_code.message
        self.details = details
        self.status_code = status_code or error_code.status_code


def _build_error_response(
    request: Request,
    status_code: int,
    message: str,
    error: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    """Build ErrorResponse và trả về JSONResponse."""
    response = ErrorResponse(
        code=status_code,
        message=message,
        error=error,
        path=request.url.path,
        timestamp=int(time.time() * 1000),
        details=details or [],
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True),
    )


# ── Exception Handlers ──────────────────────────────


def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Xử lý AppException — format JSON đồng nhất."""
    assert isinstance(exc, AppException)
    logger.warning(
        "app_exception",
        error_code=exc.error_code.name,
        message=exc.message,
        path=request.url.path,
    )
    error_phrase = HTTPStatus(exc.status_code).phrase
    return _build_error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.message,
        error=error_phrase,
    )


def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Xử lý lỗi validation từ Pydantic — field-level errors."""
    assert isinstance(exc, RequestValidationError)
    errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = " -> ".join(str(v) for v in loc if v != "body")
        errors.append(
            ErrorDetail(
                field=field or "body",
                issue=error.get("msg", ""),
                type=error.get("type", ""),
            )
        )

    logger.warning(
        "validation_error",
        errors=[e.model_dump() for e in errors],
        path=request.url.path,
    )
    return _build_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        message=ErrorCode.VALIDATION_ERROR.message,
        error=HTTPStatus(status.HTTP_422_UNPROCESSABLE_CONTENT).phrase,
        details=errors,
    )


def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback — bắt mọi exception không được xử lý."""
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        exc_info=exc,
    )
    return _build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=ErrorCode.INTERNAL_SERVER_ERROR.message,
        error=HTTPStatus(status.HTTP_500_INTERNAL_SERVER_ERROR).phrase,
    )
