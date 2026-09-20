"""Pydantic schemas for analytics API responses."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class RFMResponse(BaseModel):
    """RFM analytics response."""

    customer_id: str = Field(description="Customer ID")
    name: str = Field(description="Customer name")
    recency_days: float | None = Field(
        description="Days since last valid order, or null without orders"
    )
    frequency: int = Field(description="Valid order count")
    monetary: Decimal = Field(description="Net value of valid orders")
    r_score: int | None = Field(
        description="Recency score on a five-point scale, or null without orders"
    )
    f_score: int | None = Field(
        description="Frequency score on a five-point scale, or null without orders"
    )
    m_score: int | None = Field(
        description="Monetary score on a five-point scale, or null without orders"
    )
    rfm_score: int | None = Field(
        description="Sum of five-point RFM scores, or null without orders"
    )
    interaction_score: float = Field(
        default=0, description="Raw cumulative interaction score"
    )
    interaction_normalized_score: float | None = Field(
        default=None, description="Normalized interaction input used by scoring"
    )
    trend: str = Field(default="STABLE", description="Spend trend")
    analysis_date: date | None = Field(default=None, description="Analysis date")


class SegmentResponse(BaseModel):
    """Segment analytics response with score diagnostics."""

    customer_id: str = Field(description="Customer ID")
    name: str = Field(description="Customer name")
    segment_type: str = Field(description="Assigned segment")
    reason: str = Field(description="Reason for assigned segment")
    potential_score: float | None = Field(
        description="Potential score from 0 to 100, or null for insufficient data"
    )
    potential_level: str = Field(description="Potential score level")
    rfm: RFMResponse | None = Field(
        default=None, description="RFM inputs used by the score"
    )
    score_components: dict[str, Any] = Field(
        default_factory=dict,
        description="Weighted score inputs, weights, missing fields, and version",
    )
    analysis_date: date | None = Field(
        default=None, description="Business-local date used for the calculation"
    )
    calculated_at: datetime = Field(description="Calculation timestamp")


class PaginatedSegmentsResponse(BaseModel):
    """Paginated customer segment results."""

    current: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total segment records")
    pages: int = Field(..., description="Total pages")
    records: list[SegmentResponse] = Field(..., description="Segment records")


class PotentialScoreResponse(BaseModel):
    """Potential score response."""

    customer_id: str = Field(description="Customer ID")
    name: str = Field(description="Customer name")
    score: float | None = Field(
        description="Potential score from 0 to 100, or null for insufficient data"
    )
    level: str = Field(description="Score level")
    components: dict[str, Any] = Field(description="Underlying score components")
    calculated_at: datetime = Field(description="Calculation timestamp")


class PriorityCustomerResponse(BaseModel):
    """Customer selected for the combined potential and prediction queue."""

    customer_id: str
    name: str
    potential_score: float
    potential_level: str
    purchase_probability: float
    preferred_product_category: str | None = None
    purchase_cycle_days: float | None = None
    recommendation: str
    priority_reason: str


class CustomerProfileResponse(BaseModel):
    """Customer profile block for customer 360."""

    customer_id: str = Field(description="Customer ID")
    name: str = Field(description="Customer name")
    email: str | None = Field(default=None, description="Email")
    phone: str | None = Field(default=None, description="Phone")
    address: str | None = Field(default=None, description="Address")
    status: str = Field(description="Customer status")
    gender: str | None = Field(default=None, description="Gender")
    date_of_birth: date | None = Field(default=None, description="Date of birth")
    region: str | None = Field(default=None, description="Region")
    customer_since: datetime | None = Field(default=None, description="Customer since")
    total_orders: int = Field(description="Aggregated order count")
    total_spent: Decimal = Field(description="Aggregated spend")
    avg_order_value: Decimal = Field(description="Average order value")
    last_purchase_date: datetime | None = Field(
        default=None, description="Last purchase date"
    )
    created_at: datetime = Field(description="Created at")
    updated_at: datetime = Field(description="Updated at")


class Customer360TopProductResponse(BaseModel):
    """Top purchased product in customer 360."""

    product_id: str = Field(description="Product ID")
    name: str = Field(description="Product name")
    category: str = Field(description="Product category")
    total_quantity: int = Field(description="Total purchased quantity")
    total_revenue: Decimal = Field(description="Revenue contributed by the product")


class Customer360RecentOrderResponse(BaseModel):
    """Recent order block in customer 360."""

    order_id: str = Field(description="Order ID")
    order_number: str = Field(description="Order number")
    order_date: datetime = Field(description="Order date")
    total_amount: Decimal = Field(description="Order total amount")
    refund_amount: Decimal = Field(description="Refund amount")
    net_amount: Decimal = Field(description="Net order amount")
    status: str = Field(description="Order status")
    channel: str | None = Field(default=None, description="Order channel")


class SegmentHistoryResponse(BaseModel):
    """A persisted segment snapshot for a customer."""

    customer_id: str = Field(description="Customer ID")
    segment_type: str = Field(description="Assigned segment at that time")
    reason: str = Field(description="Reason recorded with the assignment")
    calculated_at: datetime = Field(description="When the segment was computed")
    recorded_at: datetime = Field(description="When the snapshot was persisted")


class PurchasePredictionResponse(BaseModel):
    """Repeat-purchase prediction for a customer."""

    customer_id: str
    name: str
    prediction_date: datetime
    prediction_horizon_days: int
    feature_window_days: int
    purchase_probability: float
    model_version: str


class ModelRegisterRequest(BaseModel):
    """Register a trained model artifact."""

    version: str = Field(min_length=1, max_length=100)
    artifact_uri: str | None = Field(default=None, max_length=500)
    baseline_pr_auc: Decimal | None = Field(default=None, ge=0, le=1)


class ModelEvaluateRequest(BaseModel):
    """Submit validation metrics for a trained model."""

    pr_auc: Decimal = Field(ge=0, le=1)
    lift_top10: Decimal = Field(ge=0)
    precision_top10: Decimal | None = Field(default=None, ge=0, le=1)
    overall_conversion: Decimal | None = Field(default=None, ge=0, le=1)
    metrics: dict[str, Any] | None = None


class ModelTrainRequest(BaseModel):
    """Train and evaluate a purchase-repeat model from transaction history."""

    version: str = Field(min_length=1, max_length=100)
    model_type: str = Field(
        default="LOGISTIC_REGRESSION",
        pattern="^(LOGISTIC_REGRESSION|RANDOM_FOREST)$",
    )
    feature_window_days: int = Field(default=365, ge=30, le=3650)
    prediction_horizon_days: int = Field(default=90, ge=1, le=365)
    analysis_date: date | None = None


class ModelLifecycleResponse(BaseModel):
    """Current model lifecycle state and evaluation metrics."""

    version: str
    status: str
    model_type: str | None = None
    feature_window_days: int | None = None
    prediction_horizon_days: int | None = None
    precision: Decimal | None = None
    recall: Decimal | None = None
    f1_score: Decimal | None = None
    roc_auc: Decimal | None = None
    pr_auc: Decimal | None = None
    lift_top10: Decimal | None = None
    precision_top10: Decimal | None = None
    baseline_pr_auc: Decimal
    artifact_uri: str | None = None
    metrics: dict[str, Any] | None = None
    evaluated_at: datetime | None = None


class Customer360Response(BaseModel):
    """Full customer 360 analytics response."""

    profile: CustomerProfileResponse = Field(description="Customer profile")
    rfm: RFMResponse | None = Field(default=None, description="RFM analytics")
    behavior: dict[str, Any] | None = Field(
        default=None,
        description="Purchase behavior features used by scoring and prediction",
    )
    recommendation: str | None = Field(
        default=None, description="Recommended next customer action"
    )
    segment: SegmentResponse | None = Field(default=None, description="Segment data")
    potential_score: PotentialScoreResponse | None = Field(
        default=None, description="Potential score data"
    )
    prediction: PurchasePredictionResponse | None = Field(
        default=None, description="Repeat-purchase prediction result"
    )
    top_products: list[Customer360TopProductResponse] = Field(
        default_factory=list, description="Top purchased products"
    )
    recent_orders: list[Customer360RecentOrderResponse] = Field(
        default_factory=list, description="Most recent orders"
    )


class RecalculateAnalyticsResponse(BaseModel):
    """Response for analytics recalculation trigger."""

    rfm_customers: int = Field(description="Number of customers with recalculated RFM")
    segments: int = Field(description="Number of recalculated segments")
    potential_scores: int = Field(description="Number of recalculated potential scores")
    generated_at: datetime = Field(description="Execution timestamp")


class DashboardFiltersResponse(BaseModel):
    """Active dashboard filters."""

    channel: str | None = Field(default=None, description="Sales channel filter")
    category: str | None = Field(default=None, description="Product category filter")
    segment: str | None = Field(default=None, description="Segment filter")
    level: str | None = Field(default=None, description="Potential level filter")


class DashboardPotentialCustomerResponse(BaseModel):
    """Top potential customer entry on the dashboard."""

    customer_id: str = Field(description="Customer ID")
    score: float | None = Field(
        description="Potential score, or null for insufficient data"
    )
    level: str = Field(description="Score level")
    calculated_at: datetime = Field(description="Calculation timestamp")


class DashboardSegmentCustomerResponse(BaseModel):
    """Segmented customer entry on the dashboard."""

    customer_id: str = Field(description="Customer ID")
    segment_type: str = Field(description="Assigned segment")
    reason: str = Field(description="Reason for assigned segment")
    calculated_at: datetime = Field(description="Calculation timestamp")


class DashboardTopProductCategoryResponse(BaseModel):
    """Most-purchased product category on the dashboard."""

    category: str = Field(description="Product category name")
    total_quantity: int = Field(description="Total quantity purchased")
    total_revenue: Decimal = Field(description="Total revenue for the category")
    order_count: int = Field(description="Distinct orders containing the category")


class DashboardResponse(BaseModel):
    """Analytics dashboard aggregates response."""

    days: int = Field(description="Analysis time window in days")
    filters: DashboardFiltersResponse = Field(
        description="Filters applied to this snapshot"
    )
    total_customers: int = Field(description="Total customers in window")
    total_orders: int = Field(description="Completed order count in window")
    total_revenue: Decimal = Field(description="Completed revenue in window")
    aov: Decimal = Field(description="Average order value in window")
    segment_distribution: dict[str, int] = Field(
        description="Customer count per segment type"
    )
    potential_distribution: dict[str, int] = Field(
        description="Customer count per potential level"
    )
    top_potential_customers: list[DashboardPotentialCustomerResponse] = Field(
        default_factory=list, description="Highest potential score customers"
    )
    top_at_risk_customers: list[DashboardSegmentCustomerResponse] = Field(
        default_factory=list, description="Customers in the target segment"
    )
    top_product_categories: list[DashboardTopProductCategoryResponse] = Field(
        default_factory=list, description="Most-purchased product categories"
    )


class BehaviorMetricsResponse(BaseModel):
    customer_id: str
    recency_days: float | None
    frequency: int
    monetary: Decimal
    aov: Decimal
    purchase_cycle_days: float | None
    product_preference: str | None
    product_diversity: int = 0
    review_score: float | None = None
    interaction_score: float = 0
    trend: str
    channel_count: int
