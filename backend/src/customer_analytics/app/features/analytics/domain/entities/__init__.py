"""Analytics domain entities re-exports."""

from __future__ import annotations

from customer_analytics.app.features.analytics.domain.entities.potential_score_entity import (  # noqa: E501
    PotentialScoreEntity,
)
from customer_analytics.app.features.analytics.domain.entities.rfm_entity import (
    RFMEntity,
)
from customer_analytics.app.features.analytics.domain.entities.segment_entity import (
    SegmentEntity,
)

__all__ = ["PotentialScoreEntity", "RFMEntity", "SegmentEntity"]
