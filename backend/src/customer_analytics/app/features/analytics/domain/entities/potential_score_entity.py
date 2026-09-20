"""Potential score domain entity."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from customer_analytics.app.features.analytics.domain.enums import ScoreLevel


class PotentialScoreEntity:
    """Represents customer potential score analytics."""

    def __init__(
        self,
        customer_id: str,
        score: float | None,
        level: ScoreLevel,
        components: dict[str, Any],
        calculated_at: datetime,
        customer_code: str | None = None,
        analysis_date: date | None = None,
    ):
        self.customer_id = customer_id
        self.customer_code = customer_code
        self.analysis_date = analysis_date
        self.score = score
        self.level = level
        self.components = components
        self.calculated_at = calculated_at

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "customer_id": self.customer_id,
            "customer_code": self.customer_code,
            "score": self.score,
            "level": self.level.value,
            "components": self.components,
            "calculated_at": self.calculated_at,
            "analysis_date": self.analysis_date,
        }
