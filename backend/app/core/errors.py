from enum import Enum
from typing import NamedTuple


class ErrorDetails(NamedTuple):
    status_code: int
    message: str


class ErrorCode(Enum):
    # --- 2xx Success ---
    SUCCESS = ErrorDetails(200, "Operation completed successfully")
    CREATED = ErrorDetails(201, "Resource created successfully")
    ACCEPTED = ErrorDetails(202, "Request accepted for processing")

    # --- 3xx Redirection ---
    REDIRECT_PERMANENT = ErrorDetails(301, "Permanent redirect")
    REDIRECT_FOUND = ErrorDetails(302, "Resource found elsewhere")
    REDIRECT_TEMPORARY = ErrorDetails(307, "Temporary redirect")

    # --- 4xx Client Errors ---
    BAD_REQUEST = ErrorDetails(400, "Bad request")
    UNAUTHORIZED = ErrorDetails(401, "Authentication required")
    TOKEN_EXPIRED = ErrorDetails(401, "Session expired, please login again")
    TOKEN_INVALID = ErrorDetails(401, "Invalid authentication token")
    FORBIDDEN = ErrorDetails(403, "Access denied")
    PERMISSION_DENIED = ErrorDetails(
        403, "You do not have permission to perform this action"
    )
    NOT_FOUND = ErrorDetails(404, "Resource not found")
    METHOD_NOT_ALLOWED = ErrorDetails(405, "HTTP method not allowed")
    CONFLICT = ErrorDetails(409, "Resource conflict occurred")
    RESOURCE_EXISTS = ErrorDetails(409, "Resource already exists")
    UNPROCESSABLE_ENTITY = ErrorDetails(422, "Validation error occurred")
    TOO_MANY_REQUESTS = ErrorDetails(429, "Too many requests, please slow down")

    # --- 5xx Server Errors ---
    INTERNAL_SERVER_ERROR = ErrorDetails(500, "Internal server error")
    DATABASE_ERROR = ErrorDetails(500, "Database storage failure")
    SERVICE_UNAVAILABLE = ErrorDetails(503, "Service temporarily unavailable")
    NOT_IMPLEMENTED = ErrorDetails(501, "Feature not implemented")

    @property
    def status_code(self) -> int:
        return self.value.status_code

    @property
    def message(self) -> str:
        return self.value.message
