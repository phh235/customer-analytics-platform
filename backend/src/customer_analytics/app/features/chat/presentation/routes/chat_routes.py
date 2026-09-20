"""Authenticated chat completion and SSE streaming routes."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.application.controlled_analytics_agent import (
    ControlledAnalyticsAgent,
    ControlledAnalyticsResult,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.audit_repository import (
    AnalyticsAuditRepository,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.database import (
    analytics_session_context,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.query_executor import (
    AnalyticsQueryExecutor,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.sql_safety import (
    SQLSafetyGateway,
)
from customer_analytics.app.features.chat.application.services.ai_service import (
    AIService,
)
from customer_analytics.app.features.chat.infrastructure.providers import (
    GroqProvider,
)
from customer_analytics.app.features.chat.presentation.schema.chat_schemas import (
    ChatRequest,
    ChatResponse,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    CurrentUserDep,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.dependencies import DatabaseSessionDep
from customer_analytics.core.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@lru_cache(maxsize=1)
def get_chat_provider() -> GroqProvider:
    """Build one reusable Groq client for all chat services."""
    return GroqProvider(settings)


@lru_cache(maxsize=1)
def get_chat_service() -> AIService:
    """Build one provider-backed service and reuse its async client."""
    return AIService(get_chat_provider())


ChatServiceDep = Annotated[AIService, Depends(get_chat_service)]


ANALYTICS_TERMS = (
    "doanh thu",
    "doanh số",
    "bán hàng",
    "đơn hàng",
    "khách hàng",
    "sản phẩm",
    "phân tích",
    "revenue",
    "sales",
    "orders",
    "customers",
    "products",
    "analytics",
)


def _is_analytics_question(message: str) -> bool:
    """Route business-data questions through the controlled gateway."""
    normalized = message.casefold()
    return any(term in normalized for term in ANALYTICS_TERMS)


def _require_analytics_access(current_user: UserEntity) -> None:
    if "analytics:read" not in current_user.permissions:
        raise AppException(
            ErrorCode.PERMISSION_DENIED,
            message="Không có quyền 'analytics:read'.",
        )


async def _answer(
    question: str,
    current_user: UserEntity,
    analytics_session: AsyncSession,
    audit_session: AsyncSession,
    *,
    admin_mode: bool,
) -> ControlledAnalyticsResult:
    """Run legacy analytics requests through the controlled gateway."""
    user_id: uuid.UUID | None
    try:
        user_id = uuid.UUID(current_user.id_) if current_user.id_ else None
    except ValueError:
        user_id = None

    return await ControlledAnalyticsAgent(
        provider=get_chat_provider(),
        safety_gateway=SQLSafetyGateway(settings, admin_mode=admin_mode),
        executor=AnalyticsQueryExecutor(settings),
        audit_repository=AnalyticsAuditRepository(audit_session, settings),
    ).answer(
        question,
        user_id=user_id,
        analytics_session=analytics_session,
        admin_mode=admin_mode,
    )


def _sse_event(event: str, data: dict[str, Any]) -> str:
    """Encode one JSON payload using the SSE wire format."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("", response_model=ChatResponse, summary="Generate an AI response")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user: CurrentUserDep,
    service: ChatServiceDep,
    audit_session: DatabaseSessionDep,
) -> ChatResponse:
    """Answer general chat and route analytics questions safely."""
    if not _is_analytics_question(body.message):
        return ChatResponse(message=await service.chat(body.message))

    _require_analytics_access(current_user)
    async with analytics_session_context() as analytics_session:
        result = await _answer(
            body.message,
            current_user,
            analytics_session,
            audit_session,
            admin_mode=current_user.role_code == "ADMIN",
        )
    return ChatResponse(message=result.answer)


@router.post(
    "/stream",
    response_class=StreamingResponse,
    summary="Stream an AI response",
)
@limiter.limit("10/minute")
async def stream_chat(
    request: Request,
    body: ChatRequest,
    current_user: CurrentUserDep,
    service: ChatServiceDep,
    audit_session: DatabaseSessionDep,
) -> StreamingResponse:
    """Stream generic answers or one controlled analytics answer."""

    async def generate() -> AsyncIterator[str]:
        try:
            if not _is_analytics_question(body.message):
                async for delta in service.stream_chat(body.message):
                    yield _sse_event("delta", {"content": delta})
            else:
                _require_analytics_access(current_user)
                async with analytics_session_context() as analytics_session:
                    result = await _answer(
                        body.message,
                        current_user,
                        analytics_session,
                        audit_session,
                        admin_mode=current_user.role_code == "ADMIN",
                    )
                yield _sse_event("delta", {"content": result.answer})
            yield _sse_event("done", {"status": "completed"})
        except AppException as exc:
            yield _sse_event(
                "error",
                {"code": exc.error_code.name, "message": exc.message},
            )
            yield _sse_event("done", {"status": "failed"})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
