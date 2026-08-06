"""
Shared API response models.

- ApiResponse[T]: generic wrapper {code, message, data}
- ErrorResponse: error response {code, message, error, path, timestamp, details}
- PageResponse[T]: paginated data {current, size, total, pages, records}
"""

from __future__ import annotations

from pydantic import BaseModel


class ApiResponse[T](BaseModel):
    """Generic API response.

    Usage:
        return ApiResponse(code=200, message="Success", data=user)
        return ApiResponse(code=201, message="Created", data=item)
        return ApiResponse(code=200, message="No data", data=None)
    """

    code: int
    message: str
    data: T | None = None


class ErrorDetail(BaseModel):
    """Single validation error detail — field-level error từ Pydantic."""

    field: str
    issue: str
    type: str


class ErrorResponse(BaseModel):
    """Error API response.

    Usage:
        return ErrorResponse(
            code=422,
            message="Validation failed",
            error="VALIDATION_ERROR",
            path="/api/v1/users",
            timestamp=1785300000000,
            details=[ErrorDetail(field="email", issue="Invalid", type="value_error")],
        )
    """

    code: int
    message: str
    error: str
    path: str
    timestamp: int
    details: list[ErrorDetail] = []

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": 401,
                    "message": "Email hoac mat khau khong chinh xac.",
                    "error": "Unauthorized",
                    "path": "/api/v1/auth/login",
                    "timestamp": 1705312200000,
                }
            ]
        },
    }


class PageResponse[T](BaseModel):
    """Paginated API response.

    Usage:
        return PageResponse(
            current=1,
            size=20,
            total=100,
            pages=5,
            records=users,
        )
    """

    current: int
    size: int
    total: int
    pages: int
    records: list[T]
