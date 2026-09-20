"""Use case for customer segmentation analytics."""

from __future__ import annotations

from datetime import date

from customer_analytics.app.features.analytics.domain.entities import SegmentEntity
from customer_analytics.app.features.analytics.domain.repositories import (
    AnalyticsRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class SegmentCustomersUseCase:
    """Get segments for one customer or all customers."""

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    async def execute(
        self,
        customer_id: str | None = None,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> SegmentEntity | list[SegmentEntity]:
        """Execute the segmentation flow."""
        if customer_id is None:
            return await self.repository.get_all_segments(
                days=days, analysis_date=analysis_date
            )

        segment = await self.repository.get_customer_segment(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        if segment is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )
        return segment
