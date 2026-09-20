"""Get import status use case — Get import job status and details."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.import_data.application.dto.import_models import (
    ImportJobListResult,
    ImportJobReadModel,
)
from customer_analytics.app.features.import_data.domain.repositories.import_job_repository import (
    ImportJobRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetImportStatusUseCase(BaseUseCase[tuple[str], ImportJobReadModel]):
    """Get import status use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> ImportJobReadModel:
        raise NotImplementedError()


class GetImportStatusUseCaseImpl(GetImportStatusUseCase):
    """Get import status use case implementation."""

    def __init__(self, repository: ImportJobRepository):
        self.repository = repository

    async def __call__(self, args: tuple[str]) -> ImportJobReadModel:
        (job_id,) = args

        job = await self.repository.find_by_id(job_id)
        if job is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Import job '{job_id}' không tồn tại.",
            )

        return ImportJobReadModel.from_entity(job)


class GetImportJobsUseCase(
    BaseUseCase[tuple[int, int, str | None, str | None], ImportJobListResult]
):
    """Get import jobs list use case interface."""

    @abstractmethod
    async def __call__(
        self, args: tuple[int, int, str | None, str | None]
    ) -> ImportJobListResult:
        raise NotImplementedError()


class GetImportJobsUseCaseImpl(GetImportJobsUseCase):
    """Get import jobs list use case implementation."""

    def __init__(self, repository: ImportJobRepository):
        self.repository = repository

    async def __call__(
        self, args: tuple[int, int, str | None, str | None]
    ) -> ImportJobListResult:
        skip, limit, status, import_type = args

        jobs = await self.repository.find_all(
            skip=skip,
            limit=limit,
            status=status,
            import_type=import_type,
        )

        total = await self.repository.count(
            status=status,
            import_type=import_type,
        )

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current = (skip // limit) + 1 if limit > 0 else 1

        return ImportJobListResult(
            current=current,
            size=limit,
            total=total,
            pages=pages,
            records=[ImportJobReadModel.from_entity(j) for j in jobs],
        )
