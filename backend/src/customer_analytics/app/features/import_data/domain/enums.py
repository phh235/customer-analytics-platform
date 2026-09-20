"""Import enums — Status and type enumerations for import operations."""

from __future__ import annotations

from enum import StrEnum


class ImportStatus(StrEnum):
    """Import job status."""

    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    FAILED = "FAILED"


class ImportType(StrEnum):
    """Import type."""

    CUSTOMER = "CUSTOMER"
    ORDER = "ORDER"
    ORDER_DETAIL = "ORDER_DETAIL"
    PRODUCT = "PRODUCT"
    INTERACTION = "INTERACTION"
    DATASET = "DATASET"

class ErrorSeverity(StrEnum):
    """Error severity level."""

    ERROR = "ERROR"
    WARNING = "WARNING"
