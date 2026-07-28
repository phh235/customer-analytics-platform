from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import ErrorCode


class AppException(Exception):
    """
    Custom Application Exception that bridges application-specific business errors
    with standard HTTP status codes.
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


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handles custom AppException, returning a structured JSON error response.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code.name,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles validation errors (e.g., failed Pydantic schema validation),
    formatting them into a clean, human-readable format.
    """
    errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = " -> ".join(str(loc_val) for loc_val in loc if loc_val != "body")
        errors.append(
            {
                "field": field or "body",
                "issue": error.get("msg"),
                "type": error.get("type"),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.UNPROCESSABLE_ENTITY.name,
                "message": ErrorCode.UNPROCESSABLE_ENTITY.message,
                "details": errors,
            },
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches all other unhandled Python exceptions, returning a standard 500
    Internal Server Error response.
    """
    # In a real environment, you should log this exception using logger.exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_SERVER_ERROR.name,
                "message": ErrorCode.INTERNAL_SERVER_ERROR.message,
                "details": str(exc),  # Exposing for easy debugging during development
            },
        },
    )
