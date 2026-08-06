"""Base exception classes for the application."""

from __future__ import annotations


class InvalidOperationError(Exception):
    """Raised when an invalid operation is attempted."""

    def __init__(self, message: str = "Invalid operation") -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(Exception):
    """Raised when a resource is not found."""

    def __init__(self, resource: str = "Resource", identifier: str = "") -> None:
        self.resource = resource
        self.identifier = identifier
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message)


class AlreadyExistsError(Exception):
    """Raised when a resource already exists."""

    def __init__(self, resource: str = "Resource", identifier: str = "") -> None:
        self.resource = resource
        self.identifier = identifier
        message = f"{resource} already exists"
        if identifier:
            message = f"{resource} with identifier '{identifier}' already exists"
        super().__init__(message)
