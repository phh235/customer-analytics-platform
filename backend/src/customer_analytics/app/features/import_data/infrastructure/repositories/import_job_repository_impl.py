"""Import job repository implementation — SQLAlchemy implementation."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportError,
    ImportJob,
)
from customer_analytics.app.features.import_data.domain.enums import (
    ImportStatus,
    ImportType,
)
from customer_analytics.app.features.import_data.domain.repositories.import_job_repository import (
    ImportJobRepository,
)
from customer_analytics.app.features.import_data.infrastructure.models.import_job import (
    ImportJobModel,
)


class ImportJobRepositoryImpl(ImportJobRepository):
    """Import job repository using SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: ImportJobModel) -> ImportJob:
        """Convert database model to domain entity."""
        errors = []
        if model.errors:
            for err_data in model.errors.get("errors", []):
                errors.append(
                    ImportError(
                        sheet=err_data.get("sheet"),
                        row_number=err_data.get("row_number", 0),
                        field=err_data.get("field", ""),
                        error_code=err_data.get("error_code"),
                        message=err_data.get("message", ""),
                        severity=err_data.get("severity", "ERROR"),
                        raw_value=err_data.get(
                            "raw_value", err_data.get("original_value")
                        ),
                        original_value=err_data.get("original_value"),
                    )
                )

        return ImportJob(
            id_=str(model.id),
            filename=model.filename,
            import_type=ImportType(model.import_type),
            status=ImportStatus(model.status),
            total_rows=model.total_rows,
            processed_rows=model.processed_rows,
            success_rows=model.success_rows,
            error_rows=model.error_rows,
            errors=errors,
            created_by=str(model.created_by) if model.created_by else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            storage_key=model.storage_key,
            file_sha256=model.file_sha256,
            file_size=model.file_size,
        )

    def _to_model(self, entity: ImportJob) -> ImportJobModel:
        """Convert domain entity to database model."""
        errors_dict = None
        if entity.errors:
            errors_dict = {"errors": [e.to_dict() for e in entity.errors]}

        return ImportJobModel(
            id=entity.id_,
            filename=entity.filename,
            import_type=entity.import_type.value,
            status=entity.status.value,
            total_rows=entity.total_rows,
            processed_rows=entity.processed_rows,
            success_rows=entity.success_rows,
            error_rows=entity.error_rows,
            errors=errors_dict,
            created_by=uuid.UUID(entity.created_by) if entity.created_by else None,
            completed_at=entity.completed_at,
            storage_key=entity.storage_key,
            file_sha256=entity.file_sha256,
            file_size=entity.file_size,
        )

    async def create(self, job: ImportJob) -> ImportJob:
        """Create a new import job."""
        model = self._to_model(job)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, id_: str) -> ImportJob | None:
        """Find an import job by ID."""
        result = await self._session.execute(
            select(ImportJobModel).where(ImportJobModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, job: ImportJob) -> ImportJob:
        """Update an import job."""
        if job.id_ is None:
            raise ValueError("Cannot update import job without ID")

        result = await self._session.execute(
            select(ImportJobModel).where(ImportJobModel.id == job.id_)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Import job with ID {job.id_} not found")

        model.status = job.status.value
        model.total_rows = job.total_rows
        model.processed_rows = job.processed_rows
        model.success_rows = job.success_rows
        model.error_rows = job.error_rows
        model.mapping = job.mapping
        model.completed_at = job.completed_at
        model.storage_key = job.storage_key
        model.file_sha256 = job.file_sha256
        model.file_size = job.file_size

        if job.errors:
            model.errors = {"errors": [e.to_dict() for e in job.errors]}

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        import_type: str | None = None,
    ) -> list[ImportJob]:
        """Find all import jobs with filters."""
        stmt = select(ImportJobModel).order_by(ImportJobModel.created_at.desc())

        if status:
            stmt = stmt.where(ImportJobModel.status == status)
        if import_type:
            stmt = stmt.where(ImportJobModel.import_type == import_type)

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count(
        self,
        status: str | None = None,
        import_type: str | None = None,
    ) -> int:
        """Count import jobs with filters."""
        stmt = select(func.count()).select_from(ImportJobModel)

        if status:
            stmt = stmt.where(ImportJobModel.status == status)
        if import_type:
            stmt = stmt.where(ImportJobModel.import_type == import_type)

        result = await self._session.execute(stmt)
        return result.scalar_one()
