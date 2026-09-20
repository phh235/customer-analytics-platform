"""Import job repository interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportJob,
)


class ImportJobRepository(ABC):
    """Import job repository interface."""

    @abstractmethod
    async def create(self, job: ImportJob) -> ImportJob:
        """Create a new import job."""
        raise NotImplementedError()

    @abstractmethod
    async def find_by_id(self, id_: str) -> ImportJob | None:
        """Find an import job by ID."""
        raise NotImplementedError()

    @abstractmethod
    async def update(self, job: ImportJob) -> ImportJob:
        """Update an import job."""
        raise NotImplementedError()

    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        import_type: str | None = None,
    ) -> list[ImportJob]:
        """Find all import jobs with filters."""
        raise NotImplementedError()

    @abstractmethod
    async def count(
        self,
        status: str | None = None,
        import_type: str | None = None,
    ) -> int:
        """Count import jobs with filters."""
        raise NotImplementedError()
