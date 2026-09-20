"""Authenticated controlled analytics chat endpoint."""

from __future__ import annotations

import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.application.controlled_analytics_agent import (  # noqa: E501
    ControlledAnalyticsAgent,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.audit_repository import (  # noqa: E501
    AnalyticsAuditRepository,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.database import (  # noqa: E501
    AnalyticsSessionDep,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.query_executor import (  # noqa: E501
    AnalyticsQueryExecutor,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.sql_safety import (  # noqa: E501
    SQLSafetyGateway,
)
from customer_analytics.app.features.analytics.presentation.schema.analytics_chat_schemas import (  # noqa: E501
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
from customer_analytics.core.dependencies import DatabaseSessionDep
from customer_analytics.core.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/analytics", tags=["Controlled Analytics"])

AnalyticsReadDep = Annotated[
    UserEntity,
    Depends(require_permission("analytics:read")),
]



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
    result = await agent.answer(
        body.message,
        user_id=user_id,
        analytics_session=analytics_session,
        admin_mode=current_user.role_code == "ADMIN",
    )
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
