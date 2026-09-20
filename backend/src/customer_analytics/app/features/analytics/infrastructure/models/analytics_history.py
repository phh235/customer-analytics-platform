"""Persisted analytics snapshots for auditability and exports."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class SegmentHistoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A point-in-time rule-based segment assignment."""

    __tablename__ = "segment_history"

    analysis_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    segment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    segment_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    segment_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    configuration_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class PurchasePredictionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A persisted transaction-only purchase repeat prediction."""

    __tablename__ = "purchase_predictions"

    analysis_run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("model_registry.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    prediction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    prediction_horizon_days: Mapped[int] = mapped_column(nullable=False)
    feature_window_days: Mapped[int] = mapped_column(nullable=False)
    purchase_probability: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    feature_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    feature_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
