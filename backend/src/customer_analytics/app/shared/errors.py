"""
Standardized error codes for the API.

Mỗi ErrorCode ánh xạ tới một HTTP status và message mặc định.
Client dùng code name (ổn định) để xử lý, không parse message text.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(Enum):
    """Central error catalog.

    Mỗi member = (http_status_code, default_message).
    Dùng `.status_code` và `.message` để truy cập.
    """

    # ── 2xx Success ────────────────────────────────────
    SUCCESS = (200, "Operation completed successfully")
    CREATED = (201, "Resource created successfully")
    ACCEPTED = (202, "Request accepted for processing")

    # ── 4xx Client Errors ──────────────────────────────
    BAD_REQUEST = (400, "Bad request")
    VALIDATION_ERROR = (422, "Validation failed")

    # Auth
    UNAUTHORIZED = (401, "Authentication required")
    TOKEN_EXPIRED = (401, "Session expired, please login again")
    TOKEN_INVALID = (401, "Invalid authentication token")
    INVALID_CREDENTIALS = (401, "Email or password is incorrect")
    INVALID_OTP = (400, "Invalid or expired OTP")
    INVALID_PASSWORD_RESET_TOKEN = (400, "Invalid or expired password reset token")
    # Authorization
    FORBIDDEN = (403, "Access denied")
    PERMISSION_DENIED = (403, "You do not have permission to perform this action")

    # Not found
    NOT_FOUND = (404, "Resource not found")
    USER_NOT_FOUND = (404, "User not found")
    ROLE_NOT_FOUND = (404, "Role not found")

    # Conflict
    CONFLICT = (409, "Resource conflict occurred")
    RESOURCE_EXISTS = (409, "Resource already exists")
    EMAIL_EXISTS = (409, "Email already registered")

    # Rate limit
    TOO_MANY_REQUESTS = (429, "Too many requests, please slow down")
    ANALYTICS_QUERY_REJECTED = (
        422,
        "Analytics query rejected by safety policy",
    )

    # ── 5xx Server Errors ──────────────────────────────
    INTERNAL_SERVER_ERROR = (500, "Internal server error")
    DATABASE_ERROR = (500, "Database storage failure")
    SERVICE_UNAVAILABLE = (503, "Service temporarily unavailable")
    MODEL_NOT_AVAILABLE = (503, "No deployed prediction model is available")
    NOT_IMPLEMENTED = (501, "Feature not implemented")

    # ── Identity domain ────────────────────────────────
    USER_DISABLED = (401, "Account has been disabled")
    USER_LOCKED = (401, "Account has been locked")
    INVALID_REFRESH_TOKEN = (401, "Invalid or expired refresh token")
    REFRESH_TOKEN_REUSED = (401, "Refresh token has been reused — all sessions revoked")
    CANNOT_DISABLE_SELF = (400, "Cannot disable your own account")
    INVALID_OPERATION = (400, "Invalid operation")

    @property
    def status_code(self) -> int:
        return self.value[0]

    @property
    def message(self) -> str:
        return self.value[1]
