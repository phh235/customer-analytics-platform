"""Product-interest analytics API routes."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime, timedelta
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query

from customer_analytics.app.features.analytics.infrastructure.repositories.product_interest_repository_impl import (
    ProductInterestRepositoryImpl,
)
from customer_analytics.app.features.analytics.presentation.schema.product_interest_schemas import (
    ProductInterestSummaryResponse,
    ProductUniqueViewersResponse,
    ProductViewerResponse,
    ProductViewersResponse,
    ProductViewsResponse,
    ProductViewTrendPointResponse,
    ProductViewTrendResponse,
    TrendingProductResponse,
    TrendingProductsResponse,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    require_permission,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.database import AsyncSessionFactory

router = APIRouter(prefix="/api/v1/analytics", tags=["Product Interest Analytics"])

AnalyticsReadDep = Annotated[
    UserEntity,
    Depends(require_permission("analytics:read")),
]


async def _get_repository(
    current_user: AnalyticsReadDep,
) -> AsyncGenerator[ProductInterestRepositoryImpl]:
    """Create a read-only product-interest repository."""
    async with AsyncSessionFactory() as session:
        yield ProductInterestRepositoryImpl(session, current_user)


ProductInterestRepositoryDep = Annotated[
    ProductInterestRepositoryImpl,
    Depends(_get_repository),
]


def _resolve_window(
    from_date: date | None,
    to_date: date | None,
    *,
    default_days: int = 30,
) -> tuple[date, date]:
    """Resolve an inclusive date window from optional API filters."""
    end = to_date or datetime.now(UTC).date()
    start = from_date or end - timedelta(days=default_days - 1)
    if start > end:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            "from_date must be earlier than or equal to to_date",
        )
    return start, end


def _product_summary_response(
    summary: dict[str, Any], from_date: date, to_date: date
) -> ProductInterestSummaryResponse:
    """Map a repository summary to its public response."""
    return ProductInterestSummaryResponse(
        product_id=str(summary["product_id"]),
        product_code=summary["product_code"],
        product_name=str(summary["name"]),
        total_views=int(summary["total_views"]),
        unique_viewers=int(summary["unique_viewers"]),
        from_date=from_date,
        to_date=to_date,
    )


@router.get(
    "/products/trending",
    response_model=TrendingProductsResponse,
    summary="List trending products by product-view growth",
)
async def get_trending_products(
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    to_date: Annotated[
        date | None, Query(description="Inclusive current-period end")
    ] = None,
    period_days: Annotated[int, Query(ge=1, le=365)] = 7,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> TrendingProductsResponse:
    """Compare current and previous equal-length product-view periods."""
    end = to_date or datetime.now(UTC).date()
    start = end - timedelta(days=period_days - 1)
    records = await repository.get_trending_products(end, period_days, limit)
    return TrendingProductsResponse(
        from_date=start,
        to_date=end,
        period_days=period_days,
        records=[TrendingProductResponse.model_validate(record) for record in records],
    )


@router.get(
    "/products/{product_id}/interest",
    response_model=ProductInterestSummaryResponse,
    summary="Get product-interest summary",
)
async def get_product_interest(
    product_id: str,
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
) -> ProductInterestSummaryResponse:
    """Return total views and unique viewers for one product."""
    start, end = _resolve_window(from_date, to_date)
    summary = await repository.get_product_summary(product_id, start, end)
    return _product_summary_response(summary, start, end)


@router.get(
    "/products/{product_id}/views",
    response_model=ProductViewsResponse,
    summary="Count product views",
)
async def get_product_views(
    product_id: str,
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
) -> ProductViewsResponse:
    """Count product_view events in an inclusive date window."""
    start, end = _resolve_window(from_date, to_date)
    summary = await repository.get_product_summary(product_id, start, end)
    return ProductViewsResponse(
        product_id=str(summary["product_id"]),
        product_code=summary["product_code"],
        product_name=str(summary["name"]),
        total_views=int(summary["total_views"]),
        from_date=start,
        to_date=end,
    )


@router.get(
    "/products/{product_id}/unique-viewers",
    response_model=ProductUniqueViewersResponse,
    summary="Count unique product viewers",
)
async def get_unique_product_viewers(
    product_id: str,
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
) -> ProductUniqueViewersResponse:
    """Count distinct customers who viewed a product."""
    start, end = _resolve_window(from_date, to_date)
    summary = await repository.get_product_summary(product_id, start, end)
    return ProductUniqueViewersResponse(
        product_id=str(summary["product_id"]),
        product_code=summary["product_code"],
        product_name=str(summary["name"]),
        unique_viewers=int(summary["unique_viewers"]),
        from_date=start,
        to_date=end,
    )


@router.get(
    "/products/{product_id}/viewers",
    response_model=ProductViewersResponse,
    summary="Rank customers by product-view frequency",
)
async def get_product_viewers(
    product_id: str,
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> ProductViewersResponse:
    """Return customer-product view counts, newest viewers first on ties."""
    start, end = _resolve_window(from_date, to_date)
    summary = await repository.get_product_summary(product_id, start, end)
    records = [
        ProductViewerResponse.model_validate(record)
        for record in await repository.get_product_viewers(
            product_id, start, end, limit
        )
    ]
    return ProductViewersResponse(
        product_id=str(summary["product_id"]),
        product_code=summary["product_code"],
        product_name=str(summary["name"]),
        from_date=start,
        to_date=end,
        records=records,
    )


@router.get(
    "/products/{product_id}/top-interested-customers",
    response_model=ProductViewersResponse,
    summary="List top interested customers",
)
async def get_top_interested_customers(
    product_id: str,
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ProductViewersResponse:
    """Return the highest-frequency customers for one product."""
    return await get_product_viewers(
        product_id,
        repository,
        _,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )


@router.get(
    "/products/{product_id}/trend",
    response_model=ProductViewTrendResponse,
    summary="Get product-view time trend",
)
async def get_product_view_trend(
    product_id: str,
    repository: ProductInterestRepositoryDep,
    _: AnalyticsReadDep,
    group_by: Annotated[Literal["day", "week", "month"], Query()] = "day",
    from_date: Annotated[date | None, Query()] = None,
    to_date: Annotated[date | None, Query()] = None,
) -> ProductViewTrendResponse:
    """Aggregate product views by day, week, or month."""
    start, end = _resolve_window(from_date, to_date)
    summary = await repository.get_product_summary(product_id, start, end)
    points = await repository.get_product_trend(product_id, start, end, group_by)
    return ProductViewTrendResponse(
        product_id=str(summary["product_id"]),
        product_code=summary["product_code"],
        product_name=str(summary["name"]),
        group_by=group_by,
        from_date=start,
        to_date=end,
        points=[
            ProductViewTrendPointResponse.model_validate(point) for point in points
        ],
    )
