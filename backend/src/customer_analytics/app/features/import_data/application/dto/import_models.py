"""Import DTOs — Data Transfer Objects for import operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ImportErrorDetail(BaseModel):
    """Import error detail."""

    sheet: str | None = Field(None, description="Workbook sheet")
    row_number: int = Field(..., description="Row number with error")
    field: str = Field(..., description="Field name")
    error_code: str | None = Field(None, description="Stable error code")
    message: str = Field(..., description="Error message")
    severity: str = Field(..., description="Severity (ERROR/WARNING)")
    raw_value: Any = Field(None, description="Raw source value")
    original_value: Any = Field(None, description="Backward-compatible source value")


class ImportJobReadModel(BaseModel):
    """DTO for reading import job data."""

    id: str = Field(..., description="Import job ID")
    filename: str = Field(..., description="Original filename")
    import_type: str = Field(..., description="Import type")
    status: str = Field(..., description="Import status")
    total_rows: int = Field(..., description="Total rows in file")
    processed_rows: int = Field(..., description="Rows processed")
    success_rows: int = Field(..., description="Rows imported successfully")
    error_rows: int = Field(..., description="Rows with errors")
    errors: list[ImportErrorDetail] = Field(
        default_factory=list, description="Error details"
    )
    mapping: dict[str, str] | None = Field(None, description="Column mapping")
    created_by: str | None = Field(None, description="Created by user")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    storage_key: str | None = Field(None, description="Stored source file key")
    file_sha256: str | None = Field(None, description="Source file SHA-256")
    file_size: int | None = Field(None, description="Source file size in bytes")

    @classmethod
    def from_entity(cls, entity) -> ImportJobReadModel:
        """Create read model from entity."""
        return cls(
            id=entity.id_,
            filename=entity.filename,
            import_type=entity.import_type.value,
            status=entity.status.value,
            total_rows=entity.total_rows,
            processed_rows=entity.processed_rows,
            success_rows=entity.success_rows,
            error_rows=entity.error_rows,
            errors=[
                ImportErrorDetail(
                    sheet=e.sheet,
                    row_number=e.row_number,
                    field=e.field,
                    error_code=e.error_code,
                    message=e.message,
                    severity=e.severity,
                    raw_value=e.raw_value,
                    original_value=e.original_value,
                )
                for e in entity.errors
            ],
            mapping=entity.mapping,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            completed_at=entity.completed_at,
            storage_key=entity.storage_key,
            file_sha256=entity.file_sha256,
            file_size=entity.file_size,
        )


class ImportJobListResult(BaseModel):
    """Paginated import job list result."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[ImportJobReadModel] = Field(..., description="Import job records")


class ColumnMappingRequest(BaseModel):
    """Column mapping configuration."""

    mapping: dict[str, str] = Field(
        ...,
        description="Mapping from file columns to system fields",
        examples=[{"Ho ten": "name", "Email": "email", "So dien thoai": "phone"}],
    )


class ImportPreviewResponse(BaseModel):
    """Import preview response with detected columns and sample data."""

    filename: str = Field(..., description="Detected filename")
    import_type: str = Field(..., description="Detected import type")
    columns: list[str] = Field(..., description="Columns detected in file")
    sample_data: list[dict[str, Any]] = Field(..., description="Sample rows (first 5)")
    total_rows: int = Field(..., description="Total rows in file")
    suggested_mapping: dict[str, str] = Field(
        ..., description="Suggested column mapping"
    )
    sheets: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Validated workbook sheet metadata",
    )
