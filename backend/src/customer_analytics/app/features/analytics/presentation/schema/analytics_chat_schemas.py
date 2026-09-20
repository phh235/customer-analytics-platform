"""Public schemas for controlled analytics chat."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyticsChatRequest(BaseModel):
    """A natural-language business analytics question."""

    message: str = Field(min_length=1, max_length=10_000)


class AnalyticsChatMetadata(BaseModel):
    """Safe execution metadata returned to the frontend."""

    rows: int
    execution_time_ms: int
    estimated_cost: float
    query_id: UUID


class AnalyticsChatResponse(BaseModel):
    """Natural-language answer and the structured rows behind it."""

    answer: str
    data: list[dict[str, Any]]
    metadata: AnalyticsChatMetadata
