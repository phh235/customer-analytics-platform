"""Import job entity — Domain entity for import operations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from customer_analytics.app.features.import_data.domain.enums import (
    ImportStatus,
    ImportType,
)


class ImportError:
    """Import error detail."""

    def __init__(
        self,
        row_number: int,
        field: str,
        message: str,
        severity: str = "ERROR",
        original_value: Any = None,
        sheet: str | None = None,
        error_code: str | None = None,
        raw_value: Any = None,
    ):
        self.row_number = row_number
        self.field = field
        self.message = message
        self.severity = severity
        self.original_value = original_value if raw_value is None else raw_value
        self.sheet = sheet
        self.error_code = error_code
        self.raw_value = self.original_value

    def to_dict(self) -> dict[str, Any]:
        return {
            "sheet": self.sheet,
            "row_number": self.row_number,
            "field": self.field,
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity,
            "raw_value": self.raw_value,
            "original_value": self.original_value,
        }


class ImportJob:
    """Import job entity — Represents an import operation."""

    def __init__(
        self,
        id_: str | None,
        filename: str,
        import_type: ImportType,
        status: ImportStatus = ImportStatus.PENDING,
        total_rows: int = 0,
        processed_rows: int = 0,
        success_rows: int = 0,
        error_rows: int = 0,
        errors: list[ImportError] | None = None,
        mapping: dict[str, str] | None = None,
        created_by: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        completed_at: datetime | None = None,
        storage_key: str | None = None,
        file_sha256: str | None = None,
        file_size: int | None = None,
    ):
        self.id_ = id_
        self.filename = filename
        self.import_type = import_type
        self.status = status
        self.total_rows = total_rows
        self.processed_rows = processed_rows
        self.success_rows = success_rows
        self.error_rows = error_rows
        self.errors = errors or []
        self.mapping = mapping or {}
        self.created_by = created_by
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at
        self.completed_at = completed_at
        self.storage_key = storage_key
        self.file_sha256 = file_sha256
        self.file_size = file_size

    def start_validation(self) -> ImportJob:
        """Start validation phase."""
        from copy import deepcopy

        job = deepcopy(self)
        job.status = ImportStatus.VALIDATING
        job.updated_at = datetime.now(UTC)
        return job

    def start_processing(self) -> ImportJob:
        """Start processing phase."""
        from copy import deepcopy

        job = deepcopy(self)
        job.status = ImportStatus.PROCESSING
        job.updated_at = datetime.now(UTC)
        return job

    def add_error(self, error: ImportError) -> ImportJob:
        """Add an error and update counts."""
        from copy import deepcopy

        job = deepcopy(self)
        job.errors.append(error)
        if error.row_number > 0 and not any(
            existing.row_number == error.row_number
            and existing.sheet == error.sheet
            for existing in self.errors
        ):
            job.error_rows += 1
        job.updated_at = datetime.now(UTC)
        return job

    def increment_processed(self, success: bool = True) -> ImportJob:
        """Increment processed row count."""
        from copy import deepcopy

        job = deepcopy(self)
        job.processed_rows += 1
        if success:
            job.success_rows += 1
        job.updated_at = datetime.now(UTC)
        return job

    def complete(self) -> ImportJob:
        """Mark job as completed."""
        from copy import deepcopy

        job = deepcopy(self)
        if job.error_rows > 0 and job.success_rows > 0:
            job.status = ImportStatus.PARTIALLY_COMPLETED
        elif job.error_rows > 0:
            job.status = ImportStatus.FAILED
        else:
            job.status = ImportStatus.COMPLETED
        job.completed_at = datetime.now(UTC)
        job.updated_at = datetime.now(UTC)
        return job

    def fail(self, reason: str | None = None) -> ImportJob:
        """Mark job as failed."""
        from copy import deepcopy

        job = deepcopy(self)
        job.status = ImportStatus.FAILED
        if reason:
            job.errors.append(
                ImportError(
                    row_number=0,
                    field="system",
                    message=reason,
                    severity="ERROR",
                )
            )
        job.completed_at = datetime.now(UTC)
        job.updated_at = datetime.now(UTC)
        return job

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_": self.id_,
            "filename": self.filename,
            "import_type": self.import_type.value,
            "status": self.status.value,
            "total_rows": self.total_rows,
            "processed_rows": self.processed_rows,
            "success_rows": self.success_rows,
            "error_rows": self.error_rows,
            "errors": [e.to_dict() for e in self.errors],
            "mapping": self.mapping,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "storage_key": self.storage_key,
            "file_sha256": self.file_sha256,
            "file_size": self.file_size,
        }
