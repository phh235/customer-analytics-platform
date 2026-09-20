"""Use case for calculating RFM analytics."""

from __future__ import annotations

from datetime import date

from customer_analytics.app.features.analytics.domain.entities import RFMEntity
from customer_analytics.app.features.analytics.domain.repositories import (
    AnalyticsRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class CalculateRfmUseCase:
    """Calculate RFM for one customer or all customers."""

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    async def execute(
        self,
        customer_id: str | None = None,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> RFMEntity | list[RFMEntity]:
        """Execute the RFM analytics flow."""
        if customer_id is None:
            return await self.repository.calculate_all_rfm(
                days=days, analysis_date=analysis_date
            )

        rfm = await self.repository.calculate_rfm(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        if rfm is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )
        return rfm
