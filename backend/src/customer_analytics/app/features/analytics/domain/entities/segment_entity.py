"""Customer segment domain entity."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from customer_analytics.app.features.analytics.domain.enums import (
    ScoreLevel,
    SegmentType,
)


class SegmentEntity:
    """Represents the assigned segment for a customer."""

    def __init__(
        self,
        customer_id: str,
        segment_type: SegmentType,
        reason: str,
        calculated_at: datetime,
        potential_score: float | None = None,
        potential_level: ScoreLevel = ScoreLevel.INSUFFICIENT_DATA,
        analysis_date: date | None = None,
        rfm: dict[str, Any] | None = None,
        score_components: dict[str, Any] | None = None,
    ):
        self.customer_id = customer_id
        self.segment_type = segment_type
        self.reason = reason
        self.calculated_at = calculated_at
        self.potential_score = potential_score
        self.potential_level = potential_level
        self.analysis_date = analysis_date
        self.rfm = rfm
        self.score_components = score_components

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "customer_id": self.customer_id,
            "segment_type": self.segment_type.value,
            "reason": self.reason,
            "potential_score": self.potential_score,
            "potential_level": self.potential_level.value,
            "calculated_at": self.calculated_at,
            "analysis_date": self.analysis_date,
            "rfm": self.rfm,
            "score_components": self.score_components,
        }
