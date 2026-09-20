"""Business-time analysis window helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

BUSINESS_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


@dataclass(frozen=True, slots=True)
class AnalysisWindow:
    """Half-open UTC window derived from a business-local analysis date."""

    analysis_date: date
    from_utc: datetime
    to_utc: datetime


def resolve_analysis_window(
    days: int = 365,
    analysis_date: date | datetime | None = None,
) -> AnalysisWindow:
    """Resolve ``[fromInclusive, toExclusive)`` in the business timezone."""
    if days < 1:
        raise ValueError("Analysis period must contain at least one day")

    if analysis_date is None:
        local_date = datetime.now(UTC).astimezone(BUSINESS_TIMEZONE).date()
    elif isinstance(analysis_date, datetime):
        local_date = analysis_date.astimezone(BUSINESS_TIMEZONE).date()
    else:
        local_date = analysis_date

    local_to = datetime.combine(local_date, time(), BUSINESS_TIMEZONE)
    local_from = local_to - timedelta(days=days)
    return AnalysisWindow(
        analysis_date=local_date,
        from_utc=local_from.astimezone(UTC),
        to_utc=local_to.astimezone(UTC),
    )
