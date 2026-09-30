"""Analytics API routes."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.application.services.export_service import (
    build_csv,
    build_xlsx,
)
from customer_analytics.app.features.analytics.application.services.model_lifecycle_service import (
    ModelLifecycleService,
)
from customer_analytics.app.features.analytics.application.services.purchase_model import (
    train_purchase_model,
)
from customer_analytics.app.features.analytics.application.usecases import (
    CalculatePotentialScoreUseCase,
    CalculateRfmUseCase,
    GetCustomer360UseCase,
    GetDashboardOptionsUseCase,
    GetDashboardOverviewUseCase,
    SegmentCustomersUseCase,
)
from customer_analytics.app.features.analytics.domain.dashboard_overview import (
    MAX_DASHBOARD_PAGE_SIZE,
    DashboardOverviewQuery,
    DashboardPeriod,
)
from customer_analytics.app.features.analytics.domain.entities import (
    PotentialScoreEntity,
    RFMEntity,
    SegmentEntity,
)
from customer_analytics.app.features.analytics.domain.enums import (
    ScoreLevel,
    SegmentType,
)
from customer_analytics.app.features.analytics.infrastructure.repositories.analytics_repository_impl import (
    AnalyticsRepositoryImpl,
)
from customer_analytics.app.features.analytics.presentation.schema.analytics_schemas import (
    BehaviorMetricsResponse,
    Customer360RecentOrderResponse,
    Customer360Response,
    Customer360TopProductResponse,
    CustomerProfileResponse,
    DashboardResponse,
    ModelEvaluateRequest,
    ModelLifecycleResponse,
    ModelRegisterRequest,
    ModelTrainRequest,
    PaginatedSegmentsResponse,
    PotentialScoreResponse,
    PriorityCustomerResponse,
    PurchasePredictionResponse,
    RecalculateAnalyticsResponse,
    RFMResponse,
    SegmentHistoryResponse,
    SegmentResponse,
)
from customer_analytics.app.features.analytics.presentation.schema.dashboard_overview_schemas import (
    DashboardOptionsResponse,
    DashboardOverviewResponse,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    AdminDep,
    CurrentUserDep,
    require_permission,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.app.shared.schemas import ErrorResponse
from customer_analytics.core.database import AsyncSessionFactory

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


async def _get_analytics_repository(
    current_user: CurrentUserDep,
) -> AsyncGenerator[AnalyticsRepositoryImpl]:
    """Create analytics repository with a managed async session and scope."""
    async with AsyncSessionFactory() as session:
        try:
            yield AnalyticsRepositoryImpl(session, current_user)
        except Exception:
            await session.rollback()
            raise


async def _get_model_lifecycle_service() -> AsyncGenerator[ModelLifecycleService]:
    """Create a model lifecycle service with a managed transaction."""
    async with AsyncSessionFactory() as session:
        try:
            yield ModelLifecycleService(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise


ModelLifecycleDep = Annotated[
    ModelLifecycleService, Depends(_get_model_lifecycle_service)
]


AnalyticsRepositoryDep = Annotated[
    AnalyticsRepositoryImpl, Depends(_get_analytics_repository)
]

AnalysisDateQuery = Annotated[
    date | None,
    Query(description="Business-local analysis date in Asia/Ho_Chi_Minh"),
]

AnalyticsReadDep = Annotated[
    UserEntity,
    Depends(require_permission("analytics:read")),
]


async def require_dashboard_read(current_user: CurrentUserDep) -> UserEntity:
    """Require analytics access and exclude customer-facing accounts."""
    if current_user.role_code == "USER":
        raise AppException(
            ErrorCode.PERMISSION_DENIED,
            "Customer accounts cannot access analytics dashboards.",
        )
    if "analytics:read" not in current_user.permissions:
        raise AppException(
            ErrorCode.PERMISSION_DENIED,
            "Không có quyền 'analytics:read'.",
        )
    return current_user


DashboardReadDep = Annotated[UserEntity, Depends(require_dashboard_read)]
DashboardExportDep = Annotated[
    UserEntity, Depends(require_permission("customers:export"))
]


def _matches_search(search: str | None, *values: object) -> bool:
    """Match a normalized query against any searchable response field."""
    if not search or not search.strip():
        return True
    query = search.strip().casefold()
    return any(query in str(value).casefold() for value in values if value is not None)


def _to_rfm_response(entity: RFMEntity) -> RFMResponse:
    """Map RFM entity to response schema."""
    return RFMResponse(
        customer_id=entity.customer_id,
        customer_code=getattr(entity, "customer_code", None),
        name=getattr(entity, "name", "Unknown Customer"),
        recency_days=entity.recency_days,
        frequency=entity.frequency,
        monetary=entity.monetary,
        r_score=entity.r_score,
        f_score=entity.f_score,
        m_score=entity.m_score,
        rfm_score=entity.rfm_score,
        interaction_score=entity.interaction_score,
        interaction_normalized_score=entity.interaction_normalized_score,
        trend=entity.trend,
        analysis_date=entity.analysis_date,
    )


def _to_segment_response(entity: SegmentEntity) -> SegmentResponse:
    """Map segment entity to response schema."""
    return SegmentResponse(
        customer_id=entity.customer_id,
        customer_code=getattr(entity, "customer_code", None),
        name=getattr(entity, "name", "Unknown Customer"),
        segment_type=entity.segment_type.value,
        reason=entity.reason,
        potential_score=entity.potential_score,
        potential_level=entity.potential_level.value,
        rfm=RFMResponse.model_validate(entity.rfm) if entity.rfm else None,
        score_components=entity.score_components or {},
        analysis_date=getattr(entity, "analysis_date", None),
        calculated_at=entity.calculated_at,
    )


async def _resolve_segment_analysis_date(
    repository: AnalyticsRepositoryImpl,
    analysis_date: date | None,
) -> date | None:
    """Use the newest imported run when no snapshot date is requested."""
    if analysis_date is not None:
        return analysis_date
    return await repository.get_latest_analysis_date()


def _to_potential_score_response(
    entity: PotentialScoreEntity,
) -> PotentialScoreResponse:
    """Map potential score entity to response schema."""
    return PotentialScoreResponse(
        customer_id=entity.customer_id,
        customer_code=getattr(entity, "customer_code", None),
        name=getattr(entity, "name", "Unknown Customer"),
        score=entity.score,
        level=entity.level.value,
        components=entity.components,
        calculated_at=entity.calculated_at,
    )


def _recommend_customer_action(payload: dict[str, Any]) -> str | None:
    """Derive a next action from available customer signals."""
    potential = payload.get("potential_score")
    prediction = payload.get("prediction")
    if (
        prediction
        and float(prediction["purchase_probability"])
        >= settings.ML_PRIORITY_PROBABILITY_THRESHOLD
    ):
        return "Ưu tiên ưu đãi cá nhân hóa và nhắc mua lại."
    if (
        potential
        and potential.get("score") is not None
        and float(potential["score"]) >= 80
    ):
        return "Nuôi dưỡng theo danh mục ưa thích và chu kỳ mua."
    if (payload.get("behavior") or {}).get("recency_days") is not None and (
        payload["behavior"]["recency_days"] > 90
    ):
        return "Kích hoạt chiến dịch tái tương tác."
    return "Duy trì chăm sóc định kỳ."


def _to_customer_360_response(payload: dict[str, Any]) -> Customer360Response:
    """Map customer 360 payload to response schema."""
    return Customer360Response(
        profile=CustomerProfileResponse(
            customer_id=payload["customer_id"],
            customer_code=payload.get("customer_code"),
            name=payload["name"],
            email=payload["email"],
            phone=payload["phone"],
            address=payload["address"],
            status=payload["status"],
            gender=payload["gender"],
            date_of_birth=payload["date_of_birth"],
            region=payload["region"],
            customer_since=payload["customer_since"],
            total_orders=payload["total_orders"],
            total_spent=payload["total_spent"],
            avg_order_value=payload["avg_order_value"],
            last_purchase_date=payload["last_purchase_date"],
            created_at=payload["created_at"],
            updated_at=payload["updated_at"],
        ),
        rfm=RFMResponse(
            customer_id=payload["rfm"]["customer_id"],
            customer_code=payload["rfm"].get("customer_code"),
            name=payload["name"],
            recency_days=payload["rfm"]["recency_days"],
            frequency=payload["rfm"]["frequency"],
            monetary=payload["rfm"]["monetary"],
            r_score=payload["rfm"]["r_score"],
            f_score=payload["rfm"]["f_score"],
            m_score=payload["rfm"]["m_score"],
            rfm_score=payload["rfm"]["rfm_score"],
            interaction_score=payload["rfm"].get("interaction_score", 0),
            interaction_normalized_score=payload["rfm"].get(
                "interaction_normalized_score"
            ),
            trend=payload["rfm"].get("trend", "STABLE"),
            analysis_date=payload["rfm"].get("analysis_date"),
        )
        if payload["rfm"]
        else None,
        recommendation=_recommend_customer_action(payload),
        behavior=payload.get("behavior"),
        segment=SegmentResponse(
            customer_id=payload["customer_id"],
            customer_code=payload.get("customer_code"),
            name=payload["name"],
            segment_type=payload["segment"]["segment_type"],
            reason=payload["segment"]["reason"],
            potential_score=payload["segment"]["potential_score"],
            potential_level=payload["segment"]["potential_level"],
            rfm=RFMResponse.model_validate(payload["segment"]["rfm"])
            if payload["segment"].get("rfm")
            else None,
            score_components=payload["segment"].get("score_components", {}),
            analysis_date=payload["segment"].get("analysis_date"),
            calculated_at=payload["segment"]["calculated_at"],
        )
        if payload["segment"]
        else None,
        potential_score=PotentialScoreResponse(
            customer_id=payload["customer_id"],
            customer_code=payload.get("customer_code"),
            name=payload["name"],
            score=payload["potential_score"]["score"],
            level=payload["potential_score"]["level"],
            components=payload["potential_score"]["components"],
            calculated_at=payload["potential_score"]["calculated_at"],
        )
        if payload["potential_score"]
        else None,
        prediction=PurchasePredictionResponse(**payload["prediction"])
        if payload.get("prediction")
        else None,
        top_products=[
            Customer360TopProductResponse(**product)
            for product in payload["top_products"]
        ],
        recent_orders=[
            Customer360RecentOrderResponse(**order)
            for order in payload["recent_orders"]
        ],
    )


def _to_model_lifecycle_response(model: Any) -> ModelLifecycleResponse:
    """Map a model registry row to its public lifecycle response."""
    return ModelLifecycleResponse(
        version=model.version,
        status=(
            model.status.value if hasattr(model.status, "value") else str(model.status)
        ),
        model_type=model.model_type,
        feature_window_days=model.feature_window_days,
        prediction_horizon_days=model.prediction_horizon_days,
        precision=model.precision,
        recall=model.recall,
        f1_score=model.f1_score,
        roc_auc=model.roc_auc,
        pr_auc=model.pr_auc,
        lift_top10=model.lift_top10,
        precision_top10=model.precision_top10,
        baseline_pr_auc=model.baseline_pr_auc,
        artifact_uri=model.artifact_uri,
        metrics=model.metrics,
        evaluated_at=model.evaluated_at,
    )


@router.post(
    "/models",
    response_model=ModelLifecycleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a trained prediction model",
)
async def register_model(
    _: AdminDep,
    body: ModelRegisterRequest,
    service: ModelLifecycleDep,
) -> ModelLifecycleResponse:
    model = await service.register_trained(
        body.version,
        body.artifact_uri,
        body.baseline_pr_auc,
    )
    return _to_model_lifecycle_response(model)


@router.get(
    "/models",
    response_model=list[ModelLifecycleResponse],
    status_code=status.HTTP_200_OK,
    summary="List registered prediction models",
)
async def list_models(
    _: AdminDep,
    service: ModelLifecycleDep,
) -> list[ModelLifecycleResponse]:
    """Return model versions and their lifecycle metrics."""
    return [
        _to_model_lifecycle_response(model) for model in await service.list_models()
    ]


@router.post(
    "/models/train",
    response_model=ModelLifecycleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Train and evaluate a purchase prediction model",
)
async def train_purchase_model_route(
    _: AdminDep,
    body: ModelTrainRequest,
    repository: AnalyticsRepositoryDep,
    service: ModelLifecycleDep,
) -> ModelLifecycleResponse:
    """Train, evaluate, and register a purchase-repeat model artifact."""
    rows = await repository.get_training_feature_rows(
        days=body.feature_window_days,
        horizon_days=body.prediction_horizon_days,
        analysis_date=body.analysis_date,
    )
    try:
        artifact, metrics = train_purchase_model(rows, body.model_type)
    except ValueError as exc:
        raise AppException(ErrorCode.VALIDATION_ERROR, str(exc)) from exc

    safe_version = "".join(
        character if character.isalnum() or character in "-_." else "_"
        for character in body.version
    )
    artifact_path = Path(settings.MODEL_STORAGE_DIR) / f"{safe_version}.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
    baseline_pr_auc = Decimal(str(metrics["overall_conversion"]))
    model = await service.register_trained(
        version=body.version,
        artifact_uri=str(artifact_path),
        baseline_pr_auc=baseline_pr_auc,
        model_type=body.model_type,
        feature_window_days=body.feature_window_days,
        prediction_horizon_days=body.prediction_horizon_days,
    )
    model = await service.evaluate(
        version=model.version,
        pr_auc=Decimal(str(metrics["pr_auc"])),
        lift_top10=Decimal(str(metrics["lift_top10"])),
        precision_top10=Decimal(str(metrics["precision_top10"])),
        overall_conversion=Decimal(str(metrics["overall_conversion"])),
        metrics=metrics,
    )
    return _to_model_lifecycle_response(model)


@router.post(
    "/models/{version}/evaluate",
    response_model=ModelLifecycleResponse,
    summary="Evaluate a trained prediction model",
)
async def evaluate_model(
    _: AdminDep,
    version: str,
    body: ModelEvaluateRequest,
    service: ModelLifecycleDep,
) -> ModelLifecycleResponse:
    model = await service.evaluate(
        version=version,
        pr_auc=body.pr_auc,
        lift_top10=body.lift_top10,
        precision_top10=body.precision_top10,
        overall_conversion=body.overall_conversion,
        metrics=body.metrics,
    )
    return _to_model_lifecycle_response(model)


@router.post(
    "/models/{version}/deploy",
    response_model=ModelLifecycleResponse,
    summary="Deploy an approved prediction model",
)
async def deploy_model(
    _: AdminDep,
    version: str,
    service: ModelLifecycleDep,
) -> ModelLifecycleResponse:
    model = await service.deploy(version)
    return _to_model_lifecycle_response(model)


@router.get(
    "/rfm",
    response_model=list[RFMResponse],
    status_code=status.HTTP_200_OK,
    summary="Get RFM analytics for all customers",
)
async def get_all_rfm(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> list[RFMResponse]:
    """Return RFM analytics for all customers."""
    use_case = CalculateRfmUseCase(repository)
    result = await use_case.execute(days=days, analysis_date=analysis_date)
    return [_to_rfm_response(entity) for entity in result]


@router.get(
    "/rfm/{customer_id}",
    response_model=RFMResponse,
    status_code=status.HTTP_200_OK,
    summary="Get RFM analytics for one customer",
)
async def get_customer_rfm(
    customer_id: uuid.UUID,
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> RFMResponse:
    """Return RFM analytics for a single customer."""
    use_case = CalculateRfmUseCase(repository)
    result = await use_case.execute(
        customer_id=str(customer_id),
        days=days,
        analysis_date=analysis_date,
    )
    return _to_rfm_response(result)


@router.get(
    "/segments",
    response_model=PaginatedSegmentsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated segments for all customers",
    description=(
        "Get searchable paginated customer segments. "
        "Requires analytics:read permission."
    ),
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Insufficient analytics:read permission",
            "model": ErrorResponse,
        }
    },
)
async def get_all_segments(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
    search: Annotated[
        str | None, Query(max_length=100, description="Search customer or segment")
    ] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 10,
) -> PaginatedSegmentsResponse:
    """Return a paginated, searchable list of customer segments."""
    use_case = SegmentCustomersUseCase(repository)
    resolved_analysis_date = await _resolve_segment_analysis_date(
        repository, analysis_date
    )
    result = await use_case.execute(days=days, analysis_date=resolved_analysis_date)
    assert isinstance(result, list)
    matching_result = [
        entity
        for entity in result
        if _matches_search(
            search,
            entity.customer_id,
            getattr(entity, "name", None),
            entity.segment_type.value,
            entity.reason,
        )
    ]
    total = len(matching_result)
    start = (page - 1) * size
    pages = (total + size - 1) // size if total else 0
    records = matching_result[start : start + size]
    return PaginatedSegmentsResponse(
        current=page,
        size=size,
        total=total,
        pages=pages,
        records=[_to_segment_response(entity) for entity in records],
    )


@router.get(
    "/segments/history",
    response_model=list[SegmentHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get segment change history",
)
async def get_segment_history(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    customer_id: Annotated[
        uuid.UUID | None, Query(description="Filter by customer")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[SegmentHistoryResponse]:
    """Return persisted segment snapshots, newest first."""
    history = await repository.get_segment_history(
        customer_id=str(customer_id) if customer_id else None, limit=limit
    )
    return [SegmentHistoryResponse(**row) for row in history]


@router.get(
    "/segments/{customer_id}",
    response_model=SegmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get segment for one customer",
)
async def get_customer_segment(
    customer_id: uuid.UUID,
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> SegmentResponse:
    """Return segment analytics for a single customer."""
    use_case = SegmentCustomersUseCase(repository)
    resolved_analysis_date = await _resolve_segment_analysis_date(
        repository, analysis_date
    )
    result = await use_case.execute(
        customer_id=str(customer_id),
        days=days,
        analysis_date=resolved_analysis_date,
    )
    return _to_segment_response(result)


@router.get(
    "/potential-scores",
    response_model=list[PotentialScoreResponse],
    status_code=status.HTTP_200_OK,
    summary="Get potential scores for all customers",
)
async def get_all_potential_scores(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> list[PotentialScoreResponse]:
    """Return potential scores for all customers."""
    use_case = CalculatePotentialScoreUseCase(repository)
    result = await use_case.execute(days=days, analysis_date=analysis_date)
    return [_to_potential_score_response(entity) for entity in result]


@router.get(
    "/potential-scores/{customer_id}",
    response_model=PotentialScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Get potential score for one customer",
)
async def get_customer_potential_score(
    customer_id: uuid.UUID,
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> PotentialScoreResponse:
    """Return a potential score for a single customer."""
    use_case = CalculatePotentialScoreUseCase(repository)
    result = await use_case.execute(
        customer_id=str(customer_id),
        days=days,
        analysis_date=analysis_date,
    )
    return _to_potential_score_response(result)


@router.get(
    "/priority-list",
    response_model=list[PriorityCustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Get customers prioritized for the next campaign",
)
async def get_priority_list(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    horizon_days: Annotated[int, Query(ge=1, le=365)] = 90,
    analysis_date: AnalysisDateQuery = None,
    search: Annotated[
        str | None, Query(max_length=100, description="Search priority customers")
    ] = None,
) -> list[PriorityCustomerResponse]:
    """Combine high potential scores and repeat-purchase probabilities."""
    potential_result = await CalculatePotentialScoreUseCase(repository).execute(
        days=days, analysis_date=analysis_date
    )
    predictions = await repository.get_purchase_predictions(
        days, horizon_days, analysis_date
    )
    prediction_by_customer = {row["customer_id"]: row for row in predictions}
    priority: list[PriorityCustomerResponse] = []
    for score in potential_result:
        prediction = prediction_by_customer.get(score.customer_id)
        if prediction is None:
            continue
        probability = float(prediction["purchase_probability"])
        high_potential = score.score >= 80
        high_probability = probability >= settings.ML_PRIORITY_PROBABILITY_THRESHOLD
        if not high_potential and not high_probability:
            continue
        behavior = await repository.get_behavior_metrics(
            score.customer_id, days, analysis_date
        )
        if high_potential and high_probability:
            reason = "POTENTIAL_SCORE_AND_PURCHASE_PROBABILITY"
        elif high_potential:
            reason = "POTENTIAL_SCORE"
        else:
            reason = "PURCHASE_PROBABILITY"
        recommendation = (
            "Ưu tiên ưu đãi cá nhân hóa và nhắc mua lại."
            if high_probability
            else "Nuôi dưỡng theo danh mục ưa thích và chu kỳ mua."
        )
        priority.append(
            PriorityCustomerResponse(
                customer_code=prediction.get("customer_code"),
                customer_id=score.customer_id,
                name=prediction["name"],
                potential_score=score.score,
                potential_level=score.level.value,
                purchase_probability=probability,
                preferred_product_category=(
                    behavior["product_preference"] if behavior else None
                ),
                purchase_cycle_days=(
                    behavior["purchase_cycle_days"] if behavior else None
                ),
                recommendation=recommendation,
                priority_reason=reason,
            )
        )
    ordered_priority = sorted(
        priority,
        key=lambda item: (item.potential_score, item.purchase_probability),
        reverse=True,
    )
    return [
        item
        for item in ordered_priority
        if _matches_search(
            search,
            item.customer_id,
            item.name,
            item.potential_level,
            item.preferred_product_category,
            item.recommendation,
            item.priority_reason,
        )
    ]


@router.get(
    "/customer-360/{customer_id}",
    response_model=Customer360Response,
    status_code=status.HTTP_200_OK,
    summary="Get customer 360 view",
)
async def get_customer_360(
    customer_id: uuid.UUID,
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> Customer360Response:
    """Return full customer 360 analytics for a single customer."""
    use_case = GetCustomer360UseCase(repository)
    result = await use_case.execute(
        customer_id=str(customer_id),
        days=days,
        analysis_date=analysis_date,
    )
    return _to_customer_360_response(result)


@router.post(
    "/recalculate",
    response_model=RecalculateAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger recalculation of analytics",
)
async def recalculate_analytics(
    current_user: AdminDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> RecalculateAnalyticsResponse:
    """Trigger recalculation of all analytics data on demand."""
    rfm_use_case = CalculateRfmUseCase(repository)
    segment_use_case = SegmentCustomersUseCase(repository)
    score_use_case = CalculatePotentialScoreUseCase(repository)

    rfm_result = await rfm_use_case.execute(days=days, analysis_date=analysis_date)
    segment_result = await segment_use_case.execute(
        days=days, analysis_date=analysis_date
    )
    score_result = await score_use_case.execute(days=days, analysis_date=analysis_date)

    assert isinstance(rfm_result, list)
    assert isinstance(segment_result, list)
    assert isinstance(score_result, list)

    await repository.save_segment_history(segment_result)
    await repository.save_current_potential_scores(score_result, days)
    await repository.commit()

    return RecalculateAnalyticsResponse(
        rfm_customers=len(rfm_result),
        segments=len(segment_result),
        potential_scores=len(score_result),
        generated_at=datetime.now(UTC),
    )


@router.get(
    "/behavior/{customer_id}",
    response_model=BehaviorMetricsResponse,
    summary="Get transaction behavior metrics",
)
async def get_behavior_metrics(
    customer_id: uuid.UUID,
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
) -> BehaviorMetricsResponse:
    result = await repository.get_behavior_metrics(
        str(customer_id), days, analysis_date
    )
    if result is None:
        raise AppException(ErrorCode.NOT_FOUND, "Customer not found")
    return BehaviorMetricsResponse(**result)


def _build_dashboard_query(
    period: DashboardPeriod,
    from_date: date | None,
    to_date: date | None,
    segment: str,
    potential: str,
    category: str,
    employee: str,
    opportunity_page: int,
    opportunity_page_size: int,
    priority_page: int,
    priority_page_size: int,
) -> DashboardOverviewQuery:
    """Validate enum filters before handing them to the application layer."""
    valid_segments = {"all", *(segment_type.value for segment_type in SegmentType)}
    valid_potential = {"all", *(level.value for level in ScoreLevel)}
    if segment not in valid_segments:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            f"Unknown segment '{segment}'.",
        )
    if potential not in valid_potential:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            f"Unknown potential level '{potential}'.",
        )
    return DashboardOverviewQuery(
        period=period,
        from_date=from_date,
        to_date=to_date,
        segment=segment,
        potential=potential,
        category=category,
        employee=employee,
        opportunity_page=opportunity_page,
        opportunity_page_size=opportunity_page_size,
        priority_page=priority_page,
        priority_page_size=priority_page_size,
    )


@router.get(
    "/dashboard/overview",
    response_model=DashboardOverviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get live dashboard overview",
)
async def get_dashboard_overview(
    _: DashboardReadDep,
    repository: AnalyticsRepositoryDep,
    period: Annotated[DashboardPeriod, Query()] = DashboardPeriod.DAYS_90,
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
    segment: Annotated[str, Query(max_length=50)] = "all",
    potential: Annotated[str, Query(max_length=30)] = "all",
    category: Annotated[str, Query(max_length=200)] = "all",
    employee: Annotated[str, Query(max_length=100)] = "all",
    opportunity_page: Annotated[int, Query(ge=1)] = 1,
    opportunity_page_size: Annotated[int, Query(ge=1, le=MAX_DASHBOARD_PAGE_SIZE)] = 80,
    priority_page: Annotated[int, Query(ge=1)] = 1,
    priority_page_size: Annotated[int, Query(ge=1, le=MAX_DASHBOARD_PAGE_SIZE)] = 10,
) -> DashboardOverviewResponse:
    """Return KPI, trend, scoring and paginated customer lists."""
    query = _build_dashboard_query(
        period,
        from_date,
        to_date,
        segment,
        potential,
        category,
        employee,
        opportunity_page,
        opportunity_page_size,
        priority_page,
        priority_page_size,
    )
    payload = await GetDashboardOverviewUseCase(repository).execute(query)
    return DashboardOverviewResponse.model_validate(payload)


@router.get(
    "/dashboard/options",
    response_model=DashboardOptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get scoped dashboard options",
)
async def get_dashboard_options(
    _: DashboardReadDep,
    repository: AnalyticsRepositoryDep,
) -> DashboardOptionsResponse:
    """Return filter values visible to the authenticated user."""
    payload = await GetDashboardOptionsUseCase(repository).execute()
    return DashboardOptionsResponse.model_validate(payload)


@router.get(
    "/dashboard/export.csv",
    status_code=status.HTTP_200_OK,
    summary="Export dashboard trend as CSV",
)
async def export_dashboard_csv(
    _: DashboardReadDep,
    __: DashboardExportDep,
    repository: AnalyticsRepositoryDep,
    period: Annotated[DashboardPeriod, Query()] = DashboardPeriod.DAYS_90,
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
    segment: Annotated[str, Query(max_length=50)] = "all",
    potential: Annotated[str, Query(max_length=30)] = "all",
    category: Annotated[str, Query(max_length=200)] = "all",
    employee: Annotated[str, Query(max_length=100)] = "all",
) -> StreamingResponse:
    """Export the server-filtered current/previous trend."""
    query = _build_dashboard_query(
        period,
        from_date,
        to_date,
        segment,
        potential,
        category,
        employee,
        1,
        80,
        1,
        10,
    )
    payload = await GetDashboardOverviewUseCase(repository).execute(query)
    rows = [
        (
            point["date"],
            point["previous_date"],
            point["revenue"],
            point["previous_revenue"],
            point["orders"],
            point["previous_orders"],
        )
        for point in payload["trend"]
    ]
    content = build_csv(
        [
            "date",
            "previous_date",
            "revenue",
            "previous_revenue",
            "orders",
            "previous_orders",
        ],
        rows,
    )
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=dashboard-trend.csv"},
    )


@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    summary="Get analytics dashboard aggregates",
)
async def get_dashboard(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    channel: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    segment: Annotated[str | None, Query()] = None,
    level: Annotated[str | None, Query()] = None,
    analysis_date: AnalysisDateQuery = None,
) -> DashboardResponse:
    if segment is not None and segment not in {s.value for s in SegmentType}:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            f"Unknown segment '{segment}'.",
        )
    payload = await repository.get_dashboard(
        days,
        channel=channel,
        category=category,
        segment=segment,
        level=level,
        analysis_date=analysis_date,
    )
    return DashboardResponse(**payload)


@router.get(
    "/predictions/purchase-repeat",
    response_model=list[PurchasePredictionResponse],
    summary="Get 90-day purchase repeat predictions",
)
async def get_purchase_predictions(
    current_user: AnalyticsReadDep,
    repository: AnalyticsRepositoryDep,
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    analysis_date: AnalysisDateQuery = None,
    horizon_days: Annotated[int, Query(ge=1, le=365)] = 90,
    search: Annotated[
        str | None, Query(max_length=100, description="Search prediction customers")
    ] = None,
) -> list[PurchasePredictionResponse]:
    result = await repository.get_purchase_predictions(
        days, horizon_days, analysis_date
    )
    return [
        PurchasePredictionResponse(**row)
        for row in result
        if _matches_search(
            search,
            row.get("customer_id"),
            row.get("name"),
            row.get("model_version"),
        )
    ]


@router.get("/export/rfm.csv", summary="Export RFM results as CSV")
async def export_rfm_csv(
    current_user: UserEntity = Depends(require_permission("customers:export")),
    repository: AnalyticsRepositoryImpl = Depends(_get_analytics_repository),
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
) -> StreamingResponse:
    rows = await repository.calculate_all_rfm(days)
    content = build_csv(
        [
            "customer_id",
            "customer_code",
            "recency_days",
            "frequency",
            "monetary",
            "rfm_score",
        ],
        [
            [
                r.customer_id,
                r.customer_code,
                r.recency_days,
                r.frequency,
                r.monetary,
                r.rfm_score,
            ]
            for r in rows
        ],
    )
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rfm.csv"},
    )


@router.get("/export/rfm.xlsx", summary="Export RFM results as XLSX")
async def export_rfm_xlsx(
    current_user: UserEntity = Depends(require_permission("customers:export")),
    repository: AnalyticsRepositoryImpl = Depends(_get_analytics_repository),
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
) -> StreamingResponse:
    """Export RFM results to an Excel workbook."""
    rows = await repository.calculate_all_rfm(days)
    content = build_xlsx(
        "RFM",
        [
            "customer_id",
            "customer_code",
            "recency_days",
            "frequency",
            "monetary",
            "rfm_score",
        ],
        [
            [
                r.customer_id,
                r.customer_code,
                r.recency_days,
                r.frequency,
                float(r.monetary),
                r.rfm_score,
            ]
            for r in rows
        ],
    )
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=rfm.xlsx"},
    )


@router.get("/export/segments.csv", summary="Export segmentation results as CSV")
async def export_segments_csv(
    current_user: UserEntity = Depends(require_permission("customers:export")),
    repository: AnalyticsRepositoryImpl = Depends(_get_analytics_repository),
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
) -> StreamingResponse:
    segments = await repository.get_all_segments(days)
    content = build_csv(
        [
            "customer_id",
            "customer_code",
            "name",
            "segment_type",
            "reason",
            "calculated_at",
        ],
        [
            [
                s.customer_id,
                getattr(s, "customer_code", None),
                getattr(s, "name", ""),
                s.segment_type.value,
                s.reason,
                s.calculated_at,
            ]
            for s in segments
        ],
    )
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=segments.csv"},
    )


@router.get("/export/segments.xlsx", summary="Export segmentation results as XLSX")
async def export_segments_xlsx(
    current_user: UserEntity = Depends(require_permission("customers:export")),
    repository: AnalyticsRepositoryImpl = Depends(_get_analytics_repository),
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
) -> StreamingResponse:
    segments = await repository.get_all_segments(days)
    content = build_xlsx(
        "Segments",
        [
            "customer_id",
            "customer_code",
            "name",
            "segment_type",
            "reason",
            "calculated_at",
        ],
        [
            [
                s.customer_id,
                getattr(s, "customer_code", None),
                getattr(s, "name", ""),
                s.segment_type.value,
                s.reason,
                s.calculated_at,
            ]
            for s in segments
        ],
    )
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=segments.xlsx"},
    )


@router.get("/export/target-list.csv", summary="Export target customers as CSV")
async def export_target_list_csv(
    current_user: UserEntity = Depends(require_permission("customers:export")),
    repository: AnalyticsRepositoryImpl = Depends(_get_analytics_repository),
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    horizon_days: Annotated[int, Query(ge=1, le=365)] = 90,
) -> StreamingResponse:
    predictions = await repository.get_purchase_predictions(days, horizon_days)
    headers = [
        "customer_id",
        "customer_code",
        "name",
        "purchase_probability",
        "prediction_date",
        "prediction_horizon_days",
        "feature_window_days",
        "model_version",
    ]
    rows = [
        [
            row["customer_id"],
            row["customer_code"],
            row["name"],
            row["purchase_probability"],
            row["prediction_date"],
            row["prediction_horizon_days"],
            row["feature_window_days"],
            row["model_version"],
        ]
        for row in predictions
        if row["purchase_probability"] >= 0.5
    ]
    content = build_csv(headers, rows)
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=target-list.csv"},
    )


@router.get("/export/predictions.xlsx", summary="Export prediction results as XLSX")
async def export_predictions_xlsx(
    current_user: UserEntity = Depends(require_permission("customers:export")),
    repository: AnalyticsRepositoryImpl = Depends(_get_analytics_repository),
    days: Annotated[int, Query(ge=30, le=3650)] = 365,
    horizon_days: Annotated[int, Query(ge=1, le=365)] = 90,
) -> StreamingResponse:
    predictions = await repository.get_purchase_predictions(days, horizon_days)
    headers = [
        "customer_id",
        "customer_code",
        "name",
        "purchase_probability",
        "prediction_date",
        "prediction_horizon_days",
        "feature_window_days",
        "model_version",
    ]
    rows = [
        [
            row["customer_id"],
            row["customer_code"],
            row["name"],
            row["purchase_probability"],
            row["prediction_date"],
            row["prediction_horizon_days"],
            row["feature_window_days"],
            row["model_version"],
        ]
        for row in predictions
    ]
    content = build_xlsx("Predictions", headers, rows)
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=predictions.xlsx"},
    )
