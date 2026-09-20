"""Import schemas — Request/response models for import API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ── Request schemas ────────────────────────────────────────


class ImportUploadRequest(BaseModel):
    """Import upload request — column mapping configuration."""

    import_type: str = Field(
        ...,
        description="Import type (CUSTOMER, ORDER, ORDER_DETAIL, PRODUCT)",
        examples=["CUSTOMER"],
    )
    column_mapping: dict[str, str] = Field(
        ...,
        description="Mapping from file columns to system fields",
        examples=[{"Ho ten": "name", "Email": "email", "So dien thoai": "phone"}],
    )


# ── Response schemas ───────────────────────────────────────


class ImportErrorDetailResponse(BaseModel):
    """Import error detail."""

    sheet: str | None = Field(None, description="Workbook sheet")
    row_number: int = Field(..., description="Row number with error")
    field: str = Field(..., description="Field name")
    error_code: str | None = Field(None, description="Stable error code")
    message: str = Field(..., description="Error message")
    severity: str = Field(..., description="Severity (ERROR/WARNING)")
    raw_value: Any = Field(None, description="Raw source value")
    original_value: Any = Field(None, description="Backward-compatible source value")


class ImportJobResponse(BaseModel):
    """Import job info in response."""

    id: uuid.UUID = Field(..., description="Import job ID")
    filename: str = Field(..., description="Original filename")
    import_type: str = Field(..., description="Import type")
    status: str = Field(..., description="Import status")
    total_rows: int = Field(..., description="Total rows in file")
    processed_rows: int = Field(..., description="Rows processed")
    success_rows: int = Field(..., description="Rows imported successfully")
    error_rows: int = Field(..., description="Rows with errors")
    errors: list[ImportErrorDetailResponse] = Field(
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

    model_config = {"from_attributes": True}


class PaginatedImportJobsResponse(BaseModel):
    """Paginated import jobs list."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total records")
    pages: int = Field(..., description="Total pages")
    records: list[ImportJobResponse] = Field(..., description="Import job records")


class WorkbookSheetPreview(BaseModel):
    """Preview metadata for one dataset workbook sheet."""

    name: str = Field(..., description="Exact workbook sheet name")
    columns: list[str] = Field(..., description="Validated sheet headers")
    total_rows: int = Field(..., description="Data row count")


class ImportPreviewResponse(BaseModel):
    """Import preview response."""

    filename: str = Field(..., description="Original filename")
    import_type: str = Field(..., description="Detected import type")
    columns: list[str] = Field(..., description="Columns detected in file")
    sample_data: list[dict[str, Any]] = Field(..., description="Sample rows (first 5)")
    total_rows: int = Field(..., description="Total rows in file")
    suggested_mapping: dict[str, str] = Field(
        ..., description="Column mapping or workbook marker"
    )
    sheets: list[WorkbookSheetPreview] = Field(
        default_factory=list,
        description="Validated workbook sheets for DATASET imports",
    )


class ImportProcessRequest(BaseModel):
    """Process import request."""

    job_id: uuid.UUID = Field(..., description="Import job ID")
    column_mapping: dict[str, str] = Field(
        ...,
        description="Column mapping configuration",
    )


class ConsolidateRequest(BaseModel):
    """Consolidate customers request."""

    customers: list[dict[str, Any]] = Field(
        ...,
        description="List of customer records to consolidate",
    )
    orders: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional list of order records to link",
    )


class ConsolidatedCustomerResponse(BaseModel):
    """Consolidated customer info."""

    customer_id: str = Field(..., description="Customer ID")
    name: str = Field(..., description="Customer name")
    email: str | None = Field(None, description="Email")
    phone: str | None = Field(None, description="Phone")
    address: str | None = Field(None, description="Address")
    gender: str | None = Field(None, description="Gender")
    date_of_birth: Any = Field(None, description="Date of birth")
    region: str | None = Field(None, description="Region")
    customer_since: datetime | None = Field(None, description="Customer since")
    total_orders: int = Field(0, description="Total orders")
    total_spent: float = Field(0.0, description="Total spent")
    avg_order_value: float = Field(0.0, description="Average order value")
    last_purchase_date: datetime | None = Field(None, description="Last purchase date")
    order_ids: list[str] = Field(default_factory=list, description="Linked order IDs")
    sources: list[str] = Field(default_factory=list, description="Data sources")


class ConsolidateResponse(BaseModel):
    """Consolidation result response."""

    total_customers: int = Field(..., description="Total input customers")
    consolidated_customers: int = Field(..., description="Consolidated customers")
    duplicates_found: int = Field(..., description="Duplicates found and merged")
    orders_linked: int = Field(..., description="Orders linked to customers")
    customers: list[ConsolidatedCustomerResponse] = Field(
        ..., description="Consolidated customer records"
    )


class ConsolidationRunRequest(BaseModel):
    """DB-backed consolidation run request."""

    apply: bool = Field(
        default=False,
        description=(
            "False = dry-run report only. True = persist normalization, "
            "order statistics, and duplicate merges to the database."
        ),
    )


class DuplicateGroupResponse(BaseModel):
    """A detected duplicate-customer group."""

    dedup_key: str = Field(..., description="Match key (email/phone/name)")
    primary_customer_id: str | None = Field(None, description="Kept record ID")
    duplicate_customer_ids: list[str] = Field(
        default_factory=list, description="Merged/deactivated record IDs"
    )
    fields_filled: list[str] = Field(
        default_factory=list, description="Fields filled from duplicates"
    )


class ConsolidationRunResponse(BaseModel):
    """DB-backed consolidation run result."""

    applied: bool = Field(..., description="Whether changes were persisted")
    customers_scanned: int = Field(..., description="Total customers scanned")
    duplicates_found: int = Field(..., description="Duplicate groups detected")
    customers_normalized: int = Field(
        ..., description="Customers whose contact fields changed"
    )
    stats_updated: int = Field(
        ..., description="Customers whose order statistics were refreshed"
    )
    duplicate_groups: list[DuplicateGroupResponse] = Field(
        default_factory=list, description="Duplicate group details"
    )


# ── Error schemas ──────────────────────────────────────────


class ImportErrorResponse(BaseModel):
    """Error response schema."""

    code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Error type")
    path: str = Field(..., description="Request path")
    timestamp: int = Field(..., description="Timestamp in milliseconds")
    details: list[dict[str, str | int | None]] | None = Field(
        default=None, description="Error details"
    )
