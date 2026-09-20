"""Schemas for product-interest analytics."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class ProductInterestSummaryResponse(BaseModel):
    """Combined product-interest summary for one date window."""

    product_id: str
    product_code: str | None = None
    product_name: str
    total_views: int = Field(ge=0)
    unique_viewers: int = Field(ge=0)
    from_date: date
    to_date: date


class ProductViewsResponse(BaseModel):
    """Total product-view count for one date window."""

    product_id: str
    product_code: str | None = None
    product_name: str
    total_views: int = Field(ge=0)
    from_date: date
    to_date: date


class ProductUniqueViewersResponse(BaseModel):
    """Distinct customer count for one date window."""

    product_id: str
    product_code: str | None = None
    product_name: str
    unique_viewers: int = Field(ge=0)
    from_date: date
    to_date: date


class ProductViewerResponse(BaseModel):
    """Customer view-frequency row for one product."""

    customer_id: str
    customer_code: str | None = None
    customer_name: str
    views: int = Field(ge=0)
    last_view_at: datetime


class ProductViewersResponse(BaseModel):
    """Ranked customers who viewed a product."""

    product_id: str
    product_code: str | None = None
    product_name: str
    from_date: date
    to_date: date
    records: list[ProductViewerResponse]


class ProductViewTrendPointResponse(BaseModel):
    """One time bucket in a product-view trend."""

    period_start: date
    views: int = Field(ge=0)


class ProductViewTrendResponse(BaseModel):
    """Time-bucketed product-view trend."""

    product_id: str
    product_code: str | None = None
    product_name: str
    group_by: Literal["day", "week", "month"]
    from_date: date
    to_date: date
    points: list[ProductViewTrendPointResponse]


class TrendingProductResponse(BaseModel):
    """Product growth comparison between two equal periods."""

    product_id: str
    product_code: str | None = None
    product_name: str
    current_period_views: int = Field(ge=0)
    previous_period_views: int = Field(ge=0)
    growth_percent: float | None = None
    trend_status: Literal[
        "NEW_TREND", "STRONG_TRENDING", "TRENDING", "STABLE", "DECLINING"
    ]


class TrendingProductsResponse(BaseModel):
    """Products ranked by view growth."""

    from_date: date
    to_date: date
    period_days: int = Field(ge=1)
    records: list[TrendingProductResponse]
