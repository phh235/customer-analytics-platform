"""Authenticated controlled analytics chat endpoint."""

from __future__ import annotations

import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.application.controlled_analytics_agent import (
    ControlledAnalyticsAgent,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.audit_repository import (
    AnalyticsAuditRepository,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.database import (
    AnalyticsSessionDep,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.query_executor import (
    AnalyticsQueryExecutor,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.sql_safety import (
    SQLSafetyGateway,
)
from customer_analytics.app.features.analytics.presentation.schema.analytics_chat_schemas import (
    AnalyticsChatMetadata,
    AnalyticsChatRequest,
    AnalyticsChatResponse,
)
from customer_analytics.app.features.chat.presentation.routes.chat_routes import (
    get_chat_provider,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    require_permission,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.dependencies import DatabaseSessionDep
from customer_analytics.core.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/analytics", tags=["Controlled Analytics"])

AnalyticsReadDep = Annotated[
    UserEntity,
    Depends(require_permission("analytics:read")),
]


UNKNOWN_ANALYTICS_ANSWER = (
    "Xin lỗi, tôi chưa rõ câu trả lời cho yêu cầu này trong phạm vi dữ liệu "
    "hiện có. Bạn có thể thử hỏi về doanh thu, đơn hàng, sản phẩm được xem "
    "nhiều nhất hoặc xu hướng theo thời gian."
)


def _unknown_analytics_response() -> AnalyticsChatResponse:
    """Return a useful answer when no safe analytics plan is available."""
    return AnalyticsChatResponse(
        answer=UNKNOWN_ANALYTICS_ANSWER,
        data=[],
        metadata=AnalyticsChatMetadata(
            rows=0,
            execution_time_ms=0,
            estimated_cost=0,
            query_id=uuid.uuid4(),
        ),
    )


@lru_cache(maxsize=1)
def get_query_executor() -> AnalyticsQueryExecutor:
    """Reuse query policy configuration for all requests."""
    return AnalyticsQueryExecutor(settings)


@router.post("/chat", response_model=AnalyticsChatResponse)
@limiter.limit("10/minute")
async def controlled_analytics_chat(
    request: Request,
    body: AnalyticsChatRequest,
    current_user: AnalyticsReadDep,
    analytics_session: AnalyticsSessionDep,
    audit_session: DatabaseSessionDep,
) -> AnalyticsChatResponse:
    """Answer one question through planning, AST validation, and read-only SQL."""
    user_id: uuid.UUID | None
    try:
        user_id = uuid.UUID(current_user.id_) if current_user.id_ else None
    except ValueError:
        user_id = None

    agent = ControlledAnalyticsAgent(
        provider=get_chat_provider(),
        safety_gateway=SQLSafetyGateway(
            settings,
            admin_mode=current_user.role_code == "ADMIN",
        ),
        executor=get_query_executor(),
        audit_repository=AnalyticsAuditRepository(audit_session, settings),
    )
    try:
        result = await agent.answer(
            body.message,
            user_id=user_id,
            analytics_session=analytics_session,
            admin_mode=current_user.role_code == "ADMIN",
        )
    except AppException as exc:
        if exc.error_code is not ErrorCode.ANALYTICS_QUERY_REJECTED:
            raise
        return _unknown_analytics_response()
    return AnalyticsChatResponse(
        answer=result.answer,
        data=result.rows,
        metadata=AnalyticsChatMetadata(
            rows=len(result.rows),
            execution_time_ms=result.execution.execution_time_ms,
            estimated_cost=result.execution.estimated_cost,
            query_id=result.query_id,
        ),
    )
