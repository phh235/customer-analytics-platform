"""Upload file use case — Handle file upload and create import job."""

from __future__ import annotations

import hashlib
import re
from abc import abstractmethod
from pathlib import Path

from customer_analytics.app.features.import_data.application.dto.import_models import (
    ImportJobReadModel,
    ImportPreviewResponse,
)
from customer_analytics.app.features.import_data.application.services.dataset_contract import (
    parse_dataset_workbook,
)
from customer_analytics.app.features.import_data.application.services.file_parser import (
    parse_file,
    suggest_mapping,
)
from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportJob,
)
from customer_analytics.app.features.import_data.domain.enums import (
    ImportStatus,
    ImportType,
)
from customer_analytics.app.features.import_data.domain.repositories.import_job_repository import (
    ImportJobRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class UploadFileUseCase(BaseUseCase[tuple[bytes, str, str, str], ImportJobReadModel]):
    """Upload file use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[bytes, str, str, str]) -> ImportJobReadModel:
        raise NotImplementedError()


class UploadFileUseCaseImpl(UploadFileUseCase):
    """Upload file use case implementation."""

    def __init__(self, repository: ImportJobRepository, storage_dir: str):
        self.repository = repository
        self.storage_dir = Path(storage_dir)

    async def __call__(self, args: tuple[bytes, str, str, str]) -> ImportJobReadModel:
        file_content, filename, import_type_str, created_by = args

        # Validate import type.
        try:
            import_type = ImportType(import_type_str.upper())
        except ValueError:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=(
                    f"Loại import '{import_type_str}' không hợp lệ. "
                    "Chỉ chấp nhận: CUSTOMER, ORDER, ORDER_DETAIL, PRODUCT, "
                    "INTERACTION, DATASET."
                ),
            ) from None

        # Parse and validate the canonical workbook contract before storage.
        if import_type is ImportType.DATASET:
            dataset = parse_dataset_workbook(file_content)
            rows_count = dataset.importable_rows
        else:
            _, rows = parse_file(file_content, filename)
            rows_count = len(rows)

        if rows_count == 0:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="File không có dữ liệu.",
            )

        safe_filename = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
        file_sha256 = hashlib.sha256(file_content).hexdigest()
        storage_key = f"{file_sha256}_{safe_filename}"
        target = self.storage_dir / storage_key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(file_content)

        # Create import job
        job = ImportJob(
            id_=None,
            filename=filename,
            import_type=import_type,
            status=ImportStatus.PENDING,
            total_rows=rows_count,
            created_by=created_by,
            storage_key=storage_key,
            file_sha256=file_sha256,
            file_size=len(file_content),
        )

        # Save job
        created_job = await self.repository.create(job)

        return ImportJobReadModel.from_entity(created_job)


class PreviewFileUseCase(BaseUseCase[tuple[bytes, str, str], ImportPreviewResponse]):
    """Preview file use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[bytes, str, str]) -> ImportPreviewResponse:
        raise NotImplementedError()


class PreviewFileUseCaseImpl(PreviewFileUseCase):
    """Preview file use case implementation."""

    async def __call__(self, args: tuple[bytes, str, str]) -> ImportPreviewResponse:
        file_content, filename, import_type_str = args

        # Validate import type.
        try:
            import_type = ImportType(import_type_str.upper())
        except ValueError:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=f"Loại import '{import_type_str}' không hợp lệ.",
            ) from None

        if import_type is ImportType.DATASET:
            dataset = parse_dataset_workbook(file_content)
            first_sheet = dataset.sheets["Employees"]
            sheets = [
                {
                    "name": sheet.name,
                    "columns": list(sheet.headers),
                    "total_rows": len(sheet.rows),
                }
                for sheet in dataset.sheets.values()
            ]
            return ImportPreviewResponse(
                filename=filename,
                import_type=import_type.value,
                columns=list(first_sheet.headers),
                sample_data=list(first_sheet.rows[:5]),
                total_rows=dataset.importable_rows,
                suggested_mapping={"__workbook__": import_type.value},
                sheets=sheets,
            )

        # Parse file.
        headers, rows = parse_file(file_content, filename)
        if not rows:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="File không có dữ liệu.",
            )

        suggested_mapping = suggest_mapping(headers, import_type.value)
        return ImportPreviewResponse(
            filename=filename,
            import_type=import_type.value,
            columns=headers,
            sample_data=rows[:5],
            total_rows=len(rows),
            suggested_mapping=suggested_mapping,
        )
