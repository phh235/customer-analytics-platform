"""Import routes — API endpoints for data import."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from customer_analytics.app.config import settings
from customer_analytics.app.features.customer.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    require_permission,
)
from customer_analytics.app.features.import_data.application.usecases.consolidate_customers import (
    ConsolidateCustomersUseCaseImpl,
)
from customer_analytics.app.features.import_data.application.usecases.consolidate_customers_db import (
    ConsolidateCustomersDbUseCaseImpl,
)
from customer_analytics.app.features.import_data.application.usecases.get_import_status import (
    GetImportJobsUseCaseImpl,
    GetImportStatusUseCaseImpl,
)
from customer_analytics.app.features.import_data.application.usecases.process_import import (
    ProcessImportUseCaseImpl,
)
from customer_analytics.app.features.import_data.application.usecases.upload_file import (
    PreviewFileUseCaseImpl,
    UploadFileUseCaseImpl,
)
from customer_analytics.app.features.import_data.infrastructure.repositories.import_job_repository_impl import (
    ImportJobRepositoryImpl,
)
from customer_analytics.app.features.import_data.presentation.schema.import_schema import (
    ConsolidateRequest,
    ConsolidateResponse,
    ConsolidationRunRequest,
    ConsolidationRunResponse,
    DuplicateGroupResponse,
    ImportErrorDetailResponse,
    ImportErrorResponse,
    ImportJobResponse,
    ImportPreviewResponse,
    ImportProcessRequest,
    PaginatedImportJobsResponse,
)
from customer_analytics.app.features.order.infrastructure.repositories.order_repository_impl import (
    OrderRepositoryImpl,
)
from customer_analytics.app.features.product.infrastructure.repositories.product_repository_impl import (
    ProductRepositoryImpl,
)
from customer_analytics.app.features.reference_data.infrastructure.repositories.interaction_repository_impl import (
    CustomerInteractionRepositoryImpl,
)
from customer_analytics.core.database import AsyncSessionFactory
from customer_analytics.core.dependencies import DatabaseSessionDep

router = APIRouter(prefix="/api/v1/import", tags=["Data Import"])


def _to_import_job_response(job: object) -> ImportJobResponse:
    """Map a domain import job, including nested error dataclasses."""
    fields = (
        "id",
        "filename",
        "import_type",
        "status",
        "total_rows",
        "processed_rows",
        "success_rows",
        "error_rows",
        "mapping",
        "created_by",
        "created_at",
        "updated_at",
        "completed_at",
        "storage_key",
        "file_sha256",
        "file_size",
    )
    errors = getattr(job, "errors", []) or []
    return ImportJobResponse(
        **{field: getattr(job, field, None) for field in fields},
        errors=[
            error
            if isinstance(error, ImportErrorDetailResponse)
            else ImportErrorDetailResponse.model_validate(error, from_attributes=True)
            for error in errors
        ],
    )


async def _get_import_repository():
    """Create import repository with a managed async session."""
    async with AsyncSessionFactory() as session:
        try:
            yield ImportJobRepositoryImpl(session)
        except Exception:
            await session.rollback()
            raise


# ── Upload File ────────────────────────────────────────────


@router.post(
    "/upload",
    response_model=ImportJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file for import",
    description="Upload CSV/XLSX file and create import job. Requires import:create permission.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Import job created",
            "model": ImportJobResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ImportErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ImportErrorResponse},
        status.HTTP_403_FORBIDDEN: {"model": ImportErrorResponse},
    },
)
async def upload_file(
    db: DatabaseSessionDep,
    file: UploadFile = File(..., description="CSV or XLSX file"),
    import_type: str = Query(
        ...,
        description=(
            "Import type (CUSTOMER, ORDER, ORDER_DETAIL, PRODUCT, INTERACTION, "
            "DATASET)"
        ),
    ),
    current_user: UserEntity = Depends(require_permission("import:create")),
) -> ImportJobResponse:
    """Upload file CSV/XLSX để import dữ liệu."""
    # Read file content
    content = await file.read()

    if not file.filename:
        from customer_analytics.app.shared.errors import ErrorCode
        from customer_analytics.app.shared.exceptions import AppException

        raise AppException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="File không có tên.",
        )
    use_case = UploadFileUseCaseImpl(
        ImportJobRepositoryImpl(db), settings.IMPORT_STORAGE_DIR
    )
    if current_user.id_ is None:
        from customer_analytics.app.shared.errors import ErrorCode
        from customer_analytics.app.shared.exceptions import AppException

        raise AppException(
            error_code=ErrorCode.UNAUTHORIZED,
            message="Authentication required.",
        )
    result = await use_case((content, file.filename, import_type, current_user.id_))
    await db.commit()

    return _to_import_job_response(result)


# ── Preview File ───────────────────────────────────────────


@router.post(
    "/preview",
    response_model=ImportPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview file before import",
    description="Preview file structure and get suggested column mapping.",
    responses={
        status.HTTP_200_OK: {
            "description": "File preview",
            "model": ImportPreviewResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ImportErrorResponse},
    },
)
async def preview_file(
    file: UploadFile = File(..., description="CSV or XLSX file"),
    import_type: str = Query(..., description="Import type"),
    current_user: UserEntity = Depends(require_permission("import:create")),
) -> ImportPreviewResponse:
    """Xem trước cấu trúc file và gợi ý mapping cột."""
    content = await file.read()

    if not file.filename:
        from customer_analytics.app.shared.errors import ErrorCode
        from customer_analytics.app.shared.exceptions import AppException

        raise AppException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="File không có tên.",
        )

    use_case = PreviewFileUseCaseImpl()
    result = await use_case((content, file.filename, import_type))

    return ImportPreviewResponse.model_validate(result.model_dump())


# ── Process Import ─────────────────────────────────────────


@router.post(
    "/process",
    response_model=ImportJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Process import job",
    description="Process uploaded file with column mapping and save to database.",
    responses={
        status.HTTP_200_OK: {
            "description": "Import processed",
            "model": ImportJobResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ImportErrorResponse},
        status.HTTP_404_NOT_FOUND: {"model": ImportErrorResponse},
    },
)
async def process_import(
    body: ImportProcessRequest,
    db: DatabaseSessionDep,
    current_user: UserEntity = Depends(require_permission("import:create")),
) -> ImportJobResponse:
    """Xử lý import dữ liệu với mapping cột đã chọn."""
    repository = ImportJobRepositoryImpl(db)
    use_case = ProcessImportUseCaseImpl(
        repository,
        customer_repository=CustomerRepositoryImpl(db),
        order_repository=OrderRepositoryImpl(db),
        product_repository=ProductRepositoryImpl(db),
        interaction_repository=CustomerInteractionRepositoryImpl(db),
        session=db,
    )
    result = await use_case((str(body.job_id), body.column_mapping))
    await db.commit()

    return _to_import_job_response(result)


# ── Get Import Status ──────────────────────────────────────


@router.get(
    "/jobs/{job_id}",
    response_model=ImportJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get import job status",
    description="Get detailed status of an import job.",
    responses={
        status.HTTP_200_OK: {
            "description": "Import job status",
            "model": ImportJobResponse,
        },
        status.HTTP_404_NOT_FOUND: {"model": ImportErrorResponse},
    },
)
async def get_import_status(
    job_id: uuid.UUID,
    current_user: UserEntity = Depends(require_permission("import:read")),
    repository: ImportJobRepositoryImpl = Depends(_get_import_repository),
) -> ImportJobResponse:
    """Lấy trạng thái chi tiết của import job."""
    use_case = GetImportStatusUseCaseImpl(repository)
    result = await use_case((str(job_id),))

    return _to_import_job_response(result)


# ── List Import Jobs ───────────────────────────────────────


@router.get(
    "/jobs",
    response_model=PaginatedImportJobsResponse,
    status_code=status.HTTP_200_OK,
    summary="List import jobs",
    description="Get paginated list of import jobs.",
    responses={
        status.HTTP_200_OK: {
            "description": "Import jobs list",
            "model": PaginatedImportJobsResponse,
        },
    },
)
async def list_import_jobs(
    current_user: UserEntity = Depends(require_permission("import:read")),
    repository: ImportJobRepositoryImpl = Depends(_get_import_repository),
    page: int = Query(ge=1, description="Page number", default=1),
    size: int = Query(ge=1, le=100, description="Page size", default=10),
    status_filter: str | None = Query(
        None, alias="status", description="Filter by status"
    ),
    import_type: str | None = Query(None, description="Filter by import type"),
) -> PaginatedImportJobsResponse:
    """Lấy danh sách import jobs."""
    skip = (page - 1) * size
    use_case = GetImportJobsUseCaseImpl(repository)
    result = await use_case((skip, size, status_filter, import_type))

    return PaginatedImportJobsResponse(
        current=result.current,
        size=result.size,
        total=result.total,
        pages=result.pages,
        records=[_to_import_job_response(r) for r in result.records],
    )


# ── Consolidate Customers ──────────────────────────────────


@router.post(
    "/consolidate",
    response_model=ConsolidateResponse,
    status_code=status.HTTP_200_OK,
    summary="Consolidate customer data",
    description="Merge and deduplicate customer data from imported records.",
    responses={
        status.HTTP_200_OK: {
            "description": "Consolidation result",
            "model": ConsolidateResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ImportErrorResponse},
    },
)
async def consolidate_customers(
    body: ConsolidateRequest,
    current_user: UserEntity = Depends(require_permission("import:create")),
) -> ConsolidateResponse:
    """Hợp nhất và khử trùng lặp dữ liệu khách hàng."""
    from customer_analytics.app.features.customer.infrastructure.repositories.customer_repository_impl import (
        CustomerRepositoryImpl,
    )

    async with AsyncSessionFactory() as session:
        customer_repo = CustomerRepositoryImpl(session)
        use_case = ConsolidateCustomersUseCaseImpl(
            customer_repository=customer_repo,
            order_repository=None,
        )
        result = await use_case((body.customers, body.orders))

    return ConsolidateResponse(
        total_customers=result.total_customers,
        consolidated_customers=result.consolidated_customers,
        duplicates_found=result.duplicates_found,
        orders_linked=result.orders_linked,
        customers=[c.to_dict() for c in result.customers],
    )


# ── Run DB-backed Consolidation ────────────────────────────


@router.post(
    "/consolidate/run",
    response_model=ConsolidationRunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run consolidation on imported database data",
    description=(
        "Normalize contact fields, detect duplicate customers, link order "
        "statistics. Set apply=true to persist changes; default is a dry run."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Consolidation report",
            "model": ConsolidationRunResponse,
        },
        status.HTTP_400_BAD_REQUEST: {"model": ImportErrorResponse},
    },
)
async def run_consolidation(
    body: ConsolidationRunRequest,
    db: DatabaseSessionDep,
    current_user: UserEntity = Depends(require_permission("consolidation:create")),
) -> ConsolidationRunResponse:
    """Hợp nhất dữ liệu khách hàng đã import trong database."""
    from customer_analytics.app.features.customer.infrastructure.repositories.customer_unit_of_work_impl import (
        CustomerUnitOfWorkImpl,
    )

    use_case = ConsolidateCustomersDbUseCaseImpl(
        customer_unit_of_work=CustomerUnitOfWorkImpl(db),
        order_repository=OrderRepositoryImpl(db),
    )
    result = await use_case(body.apply)

    return ConsolidationRunResponse(
        applied=result.applied,
        customers_scanned=result.customers_scanned,
        duplicates_found=result.duplicates_found,
        customers_normalized=result.customers_normalized,
        stats_updated=result.stats_updated,
        duplicate_groups=[
            DuplicateGroupResponse(
                dedup_key=g.dedup_key,
                primary_customer_id=g.primary_id,
                duplicate_customer_ids=g.duplicate_ids,
                fields_filled=g.fields_filled,
            )
            for g in result.groups
        ],
    )
