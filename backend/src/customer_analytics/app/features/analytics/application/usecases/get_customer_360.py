"""Use case for retrieving customer 360 analytics."""

from __future__ import annotations

from datetime import date
from typing import Any

from customer_analytics.app.features.analytics.domain.repositories import (
    AnalyticsRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class GetCustomer360UseCase:
    """Aggregate customer profile and analytics in one payload."""

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    async def execute(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> dict[str, Any]:
        """Execute the customer 360 flow."""
        customer_360 = await self.repository.get_customer_360(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        if customer_360 is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )
        return customer_360
