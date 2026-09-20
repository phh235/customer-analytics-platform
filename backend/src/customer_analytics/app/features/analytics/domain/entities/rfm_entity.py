"""RFM domain entity."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


class RFMEntity:
    """Represents computed RFM analytics for one customer."""

    def __init__(
        self,
        customer_id: str,
        recency_days: float | None,
        frequency: int,
        monetary: Decimal,
        r_score: int | None,
        f_score: int | None,
        m_score: int | None,
        rfm_score: int | None,
        first_purchase_date: datetime | None = None,
        trend: str = "STABLE",
        analysis_date: date | None = None,
        interaction_score: float = 0.0,
        interaction_normalized_score: float | None = None,
    ):
        self.customer_id = customer_id
        self.recency_days = recency_days
        self.frequency = frequency
        self.monetary = monetary
        self.r_score = r_score
        self.f_score = f_score
        self.m_score = m_score
        self.rfm_score = rfm_score
        self.first_purchase_date = first_purchase_date
        self.trend = trend
        self.analysis_date = analysis_date
        self.interaction_score = interaction_score
        self.interaction_normalized_score = interaction_normalized_score

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "customer_id": self.customer_id,
            "recency_days": self.recency_days,
            "frequency": self.frequency,
            "monetary": self.monetary,
            "r_score": self.r_score,
            "f_score": self.f_score,
            "m_score": self.m_score,
            "rfm_score": self.rfm_score,
            "first_purchase_date": self.first_purchase_date,
            "trend": self.trend,
            "interaction_score": self.interaction_score,
            "analysis_date": self.analysis_date,
        }
