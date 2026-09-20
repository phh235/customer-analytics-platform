"""Analytics application use cases re-exports."""

from __future__ import annotations

from customer_analytics.app.features.analytics.application.usecases.calculate_potential_score import (
    CalculatePotentialScoreUseCase,
)
from customer_analytics.app.features.analytics.application.usecases.calculate_rfm import (
    CalculateRfmUseCase,
)
from customer_analytics.app.features.analytics.application.usecases.get_customer_360 import (
    GetCustomer360UseCase,
)
from customer_analytics.app.features.analytics.application.usecases.get_dashboard_overview import (
    GetDashboardOptionsUseCase,
    GetDashboardOverviewUseCase,
)
from customer_analytics.app.features.analytics.application.usecases.segment_customers import (
    SegmentCustomersUseCase,
)

__all__ = [
    "CalculatePotentialScoreUseCase",
    "CalculateRfmUseCase",
    "GetCustomer360UseCase",
    "GetDashboardOptionsUseCase",
    "GetDashboardOverviewUseCase",
    "SegmentCustomersUseCase",
]
