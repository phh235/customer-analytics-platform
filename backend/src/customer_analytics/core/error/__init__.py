"""Core error module — Base exceptions."""

from customer_analytics.core.error.exception import (
    AlreadyExistsError,
    InvalidOperationError,
    NotFoundError,
)

__all__ = [
    "InvalidOperationError",
    "NotFoundError",
    "AlreadyExistsError",
]
