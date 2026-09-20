"""Natural-language analytics orchestration with a mandatory safety gateway."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.analytics.application.query_plan import (
    AnalyticsQueryPlan,
    compile_query,
)
from customer_analytics.app.features.analytics.domain.semantic_layer import (
    build_schema_context,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.audit_repository import (
    AnalyticsAuditRepository,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.query_executor import (
    AnalyticsQueryExecutor,
    QueryExecution,
)
from customer_analytics.app.features.analytics.infrastructure.controlled_analytics.sql_safety import (
    SQLSafetyGateway,
    ValidatedQuery,
)
from customer_analytics.app.features.chat.domain.providers.llm_provider import (
    ChatMessage,
    LLMProvider,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException

PLANNER_SYSTEM_PROMPT = """You are a controlled analytics query planner.
Return JSON only. Use this shape:
{"mode":"aggregate","metric":"revenue","date_from":"2025-10-01",
 "date_to":"2025-11-01","group_by":[],"time_bucket":null,
 "filters":{},"order_by":null,"order_direction":"desc","limit":100}
For row listings use:
{"mode":"rows","source":"public.customers","columns":["*"],"limit":10}
If the supplied semantic views cannot answer the question, return:
{"mode":"unsupported"}
Never invent a source, metric, dimension, column, or score.
Never return markdown or explanations. Do not return SQL unless a semantic plan
cannot represent the request. Use only the supplied views, tables, columns,
metrics, dimensions, and relationships. For aggregate plans, select a metric
and convert natural-language dates to half-open ISO date ranges. Apply
status = 'delivered' for order and sales metrics unless the user explicitly
asks for another supported status. Use view_count/product_views for product
view questions, not quantity_sold/product_sales. Use group_by product_name,
order_by the metric, and limit 1 for "most/highest/top" questions. Use
time_bucket only for grouped time series. Current potential-customer rows
are available only from analytics.customer_potential_current. Use that source
for potential questions; do not use customer_sales. Customer segmentation
rankings, purchase predictions, and full customer profiles are not available
unless a supplied view explicitly contains those fields.
ADMIN raw tables may contain PII and are available only in ADMIN mode.
"""
NO_DATA_ANSWER = (
    "Xin lỗi, tôi không tìm thấy dữ liệu phù hợp cho yêu cầu này trong "
    "khoảng thời gian đã chọn."
)
NO_POTENTIAL_SNAPSHOT_ANSWER = (
    "Xin lỗi, hiện chưa có snapshot điểm tiềm năng mới để trả lời yêu cầu này. "
    "Hãy chạy lại phân tích tiềm năng trước."
)

EXPLAINER_SYSTEM_PROMPT = """You explain controlled analytics results in Vietnamese.
Use only the rows supplied by the system. Do not invent values, trends, dates,
or causes that are absent from the result. Be concise and mention when the
result set is empty. Return plain text only.
"""


@dataclass(frozen=True)
class ControlledAnalyticsResult:
    """Answer plus safe structured query data."""

    query_id: uuid.UUID
    answer: str
    rows: list[dict[str, Any]]
    execution: QueryExecution
    query: ValidatedQuery


class ControlledAnalyticsAgent:
    """Plan, validate, execute, and explain one analytics question."""

    def __init__(
        self,
        provider: LLMProvider,
        safety_gateway: SQLSafetyGateway,
        executor: AnalyticsQueryExecutor,
        audit_repository: AnalyticsAuditRepository,
    ) -> None:
        self._provider = provider
        self._safety_gateway = safety_gateway
        self._executor = executor
        self._audit = audit_repository

    async def answer(
        self,
        question: str,
        *,
        user_id: uuid.UUID | None,
        analytics_session: AsyncSession,
        admin_mode: bool = False,
    ) -> ControlledAnalyticsResult:
        """Run the controlled analytics flow and write an audit record."""
        query_id = uuid.uuid4()
        generated_sql: str | None = None
        validated_query: ValidatedQuery | None = None
        try:
            # Bước 1: LLM hiểu câu hỏi và tạo semantic plan.
            plan = await self._plan(question, admin_mode=admin_mode)
            # Bước 2: Backend tự tạo SQL, không dùng SQL tự do của LLM.
            generated_sql = compile_query(plan, admin_mode=admin_mode)
            # Bước 3: Kiểm tra SQL trước khi gửi xuống database.
            validated_query = self._safety_gateway.validate(generated_sql)
            # Bước 4: Chạy truy vấn trong transaction chỉ đọc.
            execution = await self._executor.execute(analytics_session, validated_query)
            # Bước 5: Dùng kết quả thật để tạo câu trả lời.
            answer = (
                await self._explain(question, execution.rows)
                if execution.rows
                else _empty_answer(plan)
            )
            await self._audit.record(
                query_id=query_id,
                user_id=user_id,
                question=question,
                status="SUCCEEDED",
                generated_sql=generated_sql,
                validated_sql=validated_query.sql,
                row_count=len(execution.rows),
                execution_time_ms=execution.execution_time_ms,
            )
            return ControlledAnalyticsResult(
                query_id=query_id,
                answer=answer,
                rows=execution.rows,
                execution=execution,
                query=validated_query,
            )
        except AppException as exc:
            await self._audit.record(
                query_id=query_id,
                user_id=user_id,
                question=question,
                status="REJECTED",
                generated_sql=generated_sql,
                validated_sql=validated_query.sql if validated_query else None,
                rejection_reason=exc.message,
            )
            raise
        except Exception as exc:
            await self._audit.record(
                query_id=query_id,
                user_id=user_id,
                question=question,
                status="FAILED",
                generated_sql=generated_sql,
                validated_sql=validated_query.sql if validated_query else None,
                rejection_reason="Controlled analytics execution failed.",
            )
            raise AppException(
                ErrorCode.SERVICE_UNAVAILABLE,
                message="Controlled analytics is temporarily unavailable.",
            ) from exc

    async def _plan(
        self,
        question: str,
        *,
        admin_mode: bool,
    ) -> AnalyticsQueryPlan:
        # Schema context giúp LLM biết bảng, cột và metric được phép dùng.
        schema_context = build_schema_context(admin_mode=admin_mode)
        messages: list[ChatMessage] = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{schema_context}\n\nQuestion:\n{question}",
            },
        ]
        raw = await self._provider.complete(
            messages,
            response_format={"type": "json_object"},
        )
        try:
            return AnalyticsQueryPlan.model_validate(json.loads(_strip_json(raw)))
        except (json.JSONDecodeError, ValidationError) as exc:
            raise AppException(
                ErrorCode.ANALYTICS_QUERY_REJECTED,
                message="Analytics planner returned an invalid query plan.",
            ) from exc

    async def _explain(self, question: str, rows: list[dict[str, Any]]) -> str:
        result_json = json.dumps(rows, ensure_ascii=False, default=str)
        messages: list[ChatMessage] = [
            {"role": "system", "content": EXPLAINER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Question:\n{question}\n\nSQL result:\n{result_json}",
            },
        ]
        return await self._provider.complete(messages)


def _empty_answer(plan: AnalyticsQueryPlan) -> str:
    """Return a specific message when the canonical source is not populated."""
    if plan.mode == "rows" and plan.source == "customer_potential_current":
        return NO_POTENTIAL_SNAPSHOT_ANSWER
    return NO_DATA_ANSWER


def _strip_json(value: str) -> str:
    """Accept a fenced JSON response without accepting arbitrary prose."""
    normalized = value.strip()
    if normalized.startswith("```") and normalized.endswith("```"):
        lines = normalized.splitlines()
        return "\n".join(lines[1:-1]).strip()
    return normalized
