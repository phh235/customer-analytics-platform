"""Use case for customer potential score analytics."""

from __future__ import annotations

from datetime import date

from customer_analytics.app.features.analytics.domain.entities import (
    PotentialScoreEntity,
)
from customer_analytics.app.features.analytics.domain.repositories import (
    AnalyticsRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class CalculatePotentialScoreUseCase:
    """Get potential scores for one customer or all customers."""

    def __init__(self, repository: AnalyticsRepository):
        self.repository = repository

    async def execute(
        self,
        customer_id: str | None = None,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> PotentialScoreEntity | list[PotentialScoreEntity]:
        """Execute the potential scoring flow."""
        if customer_id is None:
            return await self.repository.get_all_potential_scores(
                days=days, analysis_date=analysis_date
            )

        score = await self.repository.get_potential_score(
            customer_id=customer_id,
            days=days,
            analysis_date=analysis_date,
        )
        if score is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )
        return score
