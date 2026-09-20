"""Analytics enums for segmentation and potential scoring."""

from __future__ import annotations

from enum import StrEnum


class SegmentType(StrEnum):
    """Approved customer segment types in priority order."""

    HIGH_VALUE = "HIGH_VALUE"
    LOYAL = "LOYAL"
    AT_RISK = "AT_RISK"
    POTENTIAL = "POTENTIAL"
    NEW_CUSTOMER = "NEW_CUSTOMER"
    NORMAL = "NORMAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ScoreLevel(StrEnum):
    """Potential score bands defined by the scenario."""

    HIGH = "HIGH"
    POTENTIAL = "POTENTIAL"
    NORMAL = "NORMAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
