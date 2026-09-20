"""Domain query model for the dashboard overview contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException

BUSINESS_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")
MAX_CUSTOM_RANGE_DAYS = 366
MAX_DASHBOARD_PAGE_SIZE = 100


class DashboardPeriod(StrEnum):
    """Supported dashboard periods."""

    DAYS_30 = "30d"
    DAYS_90 = "90d"
    MONTHS_6 = "6m"
    MONTHS_12 = "12m"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class DashboardWindow:
    """A pair of inclusive business-local date ranges."""

    from_date: date
    to_date: date
    previous_from: date
    previous_to: date

    @property
    def days(self) -> int:
        """Return the number of days in the current period."""
        return (self.to_date - self.from_date).days + 1

    @property
    def from_utc(self) -> datetime:
        """Return the inclusive current range start in UTC."""
        return datetime.combine(self.from_date, time(), BUSINESS_TIMEZONE).astimezone(
            UTC
        )

    @property
    def to_utc_exclusive(self) -> datetime:
        """Return the exclusive current range end in UTC."""
        return datetime.combine(
            self.to_date + timedelta(days=1), time(), BUSINESS_TIMEZONE
        ).astimezone(UTC)

    @property
    def previous_from_utc(self) -> datetime:
        """Return the inclusive previous range start in UTC."""
        return datetime.combine(
            self.previous_from, time(), BUSINESS_TIMEZONE
        ).astimezone(UTC)

    @property
    def previous_to_utc_exclusive(self) -> datetime:
        """Return the exclusive previous range end in UTC."""
        return datetime.combine(
            self.previous_to + timedelta(days=1), time(), BUSINESS_TIMEZONE
        ).astimezone(UTC)


@dataclass(frozen=True, slots=True)
class DashboardOverviewQuery:
    """Validated query used by the dashboard overview application use case."""

    period: DashboardPeriod = DashboardPeriod.DAYS_90
    from_date: date | None = None
    to_date: date | None = None
    segment: str = "all"
    potential: str = "all"
    category: str = "all"
    employee: str = "all"
    opportunity_page: int = 1
    opportunity_page_size: int = 80
    priority_page: int = 1
    priority_page_size: int = 10

    def resolve_window(self, analysis_date: date | None = None) -> DashboardWindow:
        """Resolve preset or custom dates in the business timezone."""
        if (
            self.opportunity_page < 1
            or self.priority_page < 1
            or self.opportunity_page_size < 1
            or self.priority_page_size < 1
            or self.opportunity_page_size > MAX_DASHBOARD_PAGE_SIZE
            or self.priority_page_size > MAX_DASHBOARD_PAGE_SIZE
        ):
            raise AppException(
                ErrorCode.VALIDATION_ERROR,
                "Tham số phân trang dashboard không hợp lệ.",
            )
        current_to = analysis_date or datetime.now(BUSINESS_TIMEZONE).date()
        if self.period is DashboardPeriod.CUSTOM:
            if self.from_date is None or self.to_date is None:
                raise AppException(
                    ErrorCode.VALIDATION_ERROR,
                    "from và to là bắt buộc khi period=custom.",
                )
            from_date = self.from_date
            to_date = self.to_date
        else:
            if self.period is DashboardPeriod.DAYS_30:
                from_date = current_to - timedelta(days=29)
            elif self.period is DashboardPeriod.DAYS_90:
                from_date = current_to - timedelta(days=89)
            elif self.period is DashboardPeriod.MONTHS_6:
                from_date = _subtract_months(current_to, 6) + timedelta(days=1)
            elif self.period is DashboardPeriod.MONTHS_12:
                from_date = _subtract_months(current_to, 12) + timedelta(days=1)
            else:
                raise AppException(
                    ErrorCode.VALIDATION_ERROR,
                    f"Period không hợp lệ: {self.period}.",
                )
            to_date = current_to

        if from_date > to_date:
            raise AppException(
                ErrorCode.VALIDATION_ERROR,
                "from phải nhỏ hơn hoặc bằng to.",
            )
        days = (to_date - from_date).days + 1
        if days > MAX_CUSTOM_RANGE_DAYS:
            raise AppException(
                ErrorCode.VALIDATION_ERROR,
                f"Khoảng thời gian không được vượt quá {MAX_CUSTOM_RANGE_DAYS} ngày.",
            )
        previous_to = from_date - timedelta(days=1)
        previous_from = previous_to - timedelta(days=days - 1)
        return DashboardWindow(from_date, to_date, previous_from, previous_to)


def _subtract_months(value: date, months: int) -> date:
    """Subtract calendar months while clamping to the target month."""
    month_index = value.year * 12 + value.month - 1 - months
    year, month_index = divmod(month_index, 12)
    month = month_index + 1
    last_day = _days_in_month(year, month)
    return value.replace(year=year, month=month, day=min(value.day, last_day))


def _days_in_month(year: int, month: int) -> int:
    """Return the number of days in a Gregorian month."""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day
