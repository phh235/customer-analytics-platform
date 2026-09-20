"""Schemas for the live dashboard overview API."""

from __future__ import annotations

from datetime import date as Date
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DashboardMetaResponse(BaseModel):
    """Traceability and display metadata for a dashboard snapshot."""

    source: Literal["live"] = "live"
    generated_at: datetime
    analysis_date: Date
    run_id: str | None = None
    config_version: str
    currency: str = "VND"
    timezone: str = "Asia/Ho_Chi_Minh"


class DashboardPeriodResponse(BaseModel):
    """Current and previous inclusive date ranges."""

    from_date: Date = Field(alias="from")
    to_date: Date = Field(alias="to")
    previous_from: Date
    previous_to: Date

    model_config = {"populate_by_name": True}


class DashboardFiltersResponse(BaseModel):
    """Filters actually applied by the server."""

    period: str
    from_date: Date = Field(alias="from")
    to_date: Date = Field(alias="to")
    segment: str
    potential: str
    category: str
    employee: str

    model_config = {"populate_by_name": True}


class DashboardMetricResponse(BaseModel):
    """A current/previous aggregate and its percentage delta."""

    current: int | float
    previous: int | float
    change_percent: float | None


class DashboardMetricsResponse(BaseModel):
    """Dashboard KPI aggregates."""

    customers: DashboardMetricResponse
    orders: DashboardMetricResponse
    revenue: DashboardMetricResponse
    aov: DashboardMetricResponse


class DashboardTrendPointResponse(BaseModel):
    """One local calendar day in the current and previous trend."""

    date: Date
    previous_date: Date
    revenue: int
    previous_revenue: int
    orders: int
    previous_orders: int


class DashboardSegmentResponse(BaseModel):
    """Customer count for one mutually-exclusive segment."""

    key: str
    label: str
    count: int


class DashboardDistributionResponse(BaseModel):
    """A bounded histogram bucket."""

    label: str
    min: float
    max: float
    count: int


class DashboardPaginationResponse(BaseModel):
    """Pagination metadata for dashboard customer lists."""

    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class DashboardPotentialResponse(BaseModel):
    """Potential score distribution and configuration."""

    distribution: list[DashboardDistributionResponse]
    high_count: int
    eligible_count: int
    insufficient_count: int
    average_score: float | None
    thresholds: dict[str, float]
    weights: dict[str, float]


class DashboardCategoryResponse(BaseModel):
    """Revenue contribution of one product category."""

    id: str
    name: str
    revenue: int
    orders: int
    units: int
    customers: int


class DashboardPredictionsResponse(BaseModel):
    """Prediction availability and probability distribution."""

    status: Literal["available", "not_deployed", "insufficient_data"]
    model_version: str | None
    prediction_date: datetime | None
    horizon_days: int | None
    feature_window: int | None
    evaluated_customers: int
    insufficient_count: int
    distribution: list[DashboardDistributionResponse]


class DashboardOpportunityCustomerResponse(BaseModel):
    """Customer with both a score and a model probability."""

    id: str
    name: str
    segment: str
    potential_score: float
    purchase_probability: float
    revenue: int


class DashboardPriorityCustomerResponse(BaseModel):
    """High-potential customer in the bounded priority list."""

    id: str
    name: str
    segment: str
    potential_score: float
    purchase_probability: float | None
    revenue: int
    employee_id: str | None = None


class DashboardDataQualityResponse(BaseModel):
    """Data quality and interaction provenance counters."""

    valid_orders: int
    excluded_orders: int
    unscored_customers: int
    interaction_source: Literal["real", "simulated"]


class DashboardOverviewResponse(BaseModel):
    """Full live dashboard overview contract."""

    meta: DashboardMetaResponse
    period: DashboardPeriodResponse
    filters: DashboardFiltersResponse
    metrics: DashboardMetricsResponse
    trend: list[DashboardTrendPointResponse]
    segments: list[DashboardSegmentResponse]
    potential: DashboardPotentialResponse
    categories: list[DashboardCategoryResponse]
    predictions: DashboardPredictionsResponse
    opportunity_customers: list[DashboardOpportunityCustomerResponse]
    priority_customers: list[DashboardPriorityCustomerResponse]
    opportunity_pagination: DashboardPaginationResponse
    priority_pagination: DashboardPaginationResponse
    priority_total: int
    data_quality: DashboardDataQualityResponse


class DashboardOptionResponse(BaseModel):
    """One selectable dashboard option."""

    id: str
    name: str


class DashboardOptionsResponse(BaseModel):
    """Scoped options and scoring configuration for the dashboard."""

    segments: list[DashboardOptionResponse]
    potential_levels: list[DashboardOptionResponse]
    categories: list[DashboardOptionResponse]
    employees: list[DashboardOptionResponse]
    thresholds: dict[str, float]
    weights: dict[str, float]
    analysis_date: Date
    max_custom_range_days: int
    currency: str = "VND"
    timezone: str = "Asia/Ho_Chi_Minh"
