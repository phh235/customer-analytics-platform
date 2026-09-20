"""Application use cases for dashboard overview reads."""

from __future__ import annotations

from typing import Any

from customer_analytics.app.features.analytics.domain.dashboard_overview import (
    DashboardOverviewQuery,
)
from customer_analytics.app.features.analytics.domain.repositories import (
    AnalyticsRepository,
)


class GetDashboardOverviewUseCase:
    """Load one server-scoped dashboard overview."""

    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    async def execute(self, query: DashboardOverviewQuery) -> dict[str, Any]:
        """Return the repository aggregate for the validated query."""
        query.resolve_window()
        return await self.repository.get_dashboard_overview(query)


class GetDashboardOptionsUseCase:
    """Load server-scoped dashboard filter options."""

    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    async def execute(self) -> dict[str, Any]:
        """Return options and active scoring configuration."""
        return await self.repository.get_dashboard_options()
