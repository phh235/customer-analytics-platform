"""Analytics repository interface."""

from __future__ import annotations

from abc import abstractmethod
from datetime import date
from typing import Any

from customer_analytics.app.features.analytics.domain.dashboard_overview import (
    DashboardOverviewQuery,
)
from customer_analytics.app.features.analytics.domain.entities import (
    PotentialScoreEntity,
    RFMEntity,
    SegmentEntity,
)
from customer_analytics.core.repositories.base_repository import BaseRepository


class AnalyticsRepository(BaseRepository[RFMEntity]):
    """Analytics repository contract."""

    @abstractmethod
    async def calculate_rfm(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> RFMEntity | None:
        """Calculate RFM metrics for one customer."""
        raise NotImplementedError()

    @abstractmethod
    async def calculate_all_rfm(
        self, days: int = 365, analysis_date: date | None = None
    ) -> list[RFMEntity]:
        """Calculate RFM metrics for all customers."""
        raise NotImplementedError()

    @abstractmethod
    async def get_customer_segment(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> SegmentEntity | None:
        """Get segment for one customer."""
        raise NotImplementedError()

    @abstractmethod
    async def get_all_segments(
        self,
        days: int = 365,
        rows: list[dict[str, Any]] | None = None,
        analysis_date: date | None = None,
    ) -> list[SegmentEntity]:
        """Get segments for all customers."""
        raise NotImplementedError()

    @abstractmethod
    async def get_latest_analysis_date(self) -> date | None:
        """Return the newest completed analysis-run date, if one exists."""
        raise NotImplementedError()

    @abstractmethod
    async def get_potential_score(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> PotentialScoreEntity | None:
        """Get potential score for one customer."""
        raise NotImplementedError()

    @abstractmethod
    async def get_all_potential_scores(
        self,
        days: int = 365,
        rows: list[dict[str, Any]] | None = None,
        analysis_date: date | None = None,
    ) -> list[PotentialScoreEntity]:
        """Get potential scores for all customers."""
        raise NotImplementedError()

    @abstractmethod
    async def get_customer_360(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> dict[str, Any] | None:
        """Get full customer 360 analytics payload."""
        raise NotImplementedError()

    @abstractmethod
    async def get_behavior_metrics(
        self,
        customer_id: str,
        days: int = 365,
        analysis_date: date | None = None,
    ) -> dict[str, Any] | None:
        """Calculate purchase behavior metrics for one customer."""
        raise NotImplementedError()

    @abstractmethod
    async def get_dashboard(
        self,
        days: int = 365,
        channel: str | None = None,
        category: str | None = None,
        segment: str | None = None,
        level: str | None = None,
        analysis_date: date | None = None,
    ) -> dict[str, Any]:
        """Calculate dashboard aggregates with optional filters."""
        raise NotImplementedError()

    @abstractmethod
    async def get_dashboard_overview(
        self, query: DashboardOverviewQuery
    ) -> dict[str, Any]:
        """Calculate the live dashboard overview for the scoped user."""
        raise NotImplementedError()

    @abstractmethod
    async def get_dashboard_options(self) -> dict[str, Any]:
        """Return dashboard options visible to the scoped user."""
        raise NotImplementedError()

    @abstractmethod
    async def get_purchase_predictions(
        self,
        days: int = 365,
        horizon_days: int = 30,
        analysis_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Calculate predictions from a deployed model."""
        raise NotImplementedError()

    @abstractmethod
    async def get_segment_history(
        self, customer_id: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch persisted segment snapshots, newest first."""
        raise NotImplementedError()

    @abstractmethod
    async def get_customer_prediction(
        self,
        customer_id: str,
        days: int = 365,
        horizon_days: int = 30,
        analysis_date: date | None = None,
    ) -> dict[str, Any] | None:
        """Get one prediction from a deployed model."""
        raise NotImplementedError()

    @abstractmethod
    async def get_training_feature_rows(
        self,
        days: int = 365,
        horizon_days: int = 90,
        analysis_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Build labeled features for purchase-repeat model training."""
        raise NotImplementedError()

    @abstractmethod
    async def save_segment_history(self, segments: list[SegmentEntity]) -> None:
        """Persist the current segmentation snapshot."""
        raise NotImplementedError()

    @abstractmethod
    async def save_purchase_predictions(
        self, predictions: list[dict[str, Any]]
    ) -> None:
        """Persist the current prediction snapshot."""
        raise NotImplementedError()

    @abstractmethod
    async def commit(self) -> None:
        """Commit persisted analytics snapshots."""
        raise NotImplementedError()
