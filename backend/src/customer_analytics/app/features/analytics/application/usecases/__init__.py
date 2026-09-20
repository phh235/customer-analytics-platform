"""Analytics application use cases re-exports."""

from __future__ import annotations

from customer_analytics.app.features.analytics.application.usecases.calculate_potential_score import (  # noqa: E501
    CalculatePotentialScoreUseCase,
)
from customer_analytics.app.features.analytics.application.usecases.calculate_rfm import (  # noqa: E501
    CalculateRfmUseCase,
)
from customer_analytics.app.features.analytics.application.usecases.get_customer_360 import (  # noqa: E501
    GetCustomer360UseCase,
)
from customer_analytics.app.features.analytics.application.usecases.get_dashboard_overview import (  # noqa: E501
    GetDashboardOptionsUseCase,
    GetDashboardOverviewUseCase,
)
from customer_analytics.app.features.analytics.application.usecases.segment_customers import (  # noqa: E501
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
