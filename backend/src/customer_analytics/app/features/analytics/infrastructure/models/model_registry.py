"""Prediction model lifecycle persistence."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import JSON, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ModelLifecycleStatus(StrEnum):
    """Allowed states for a prediction model version."""

    DRAFT = "DRAFT"
    TRAINING = "TRAINING"
    TRAINED = "TRAINED"
    EVALUATING = "EVALUATING"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    RETIRED = "RETIRED"
    FAILED = "FAILED"


class ModelRegistryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A registered ML model version and deployment candidate."""

    __tablename__ = "model_registry"

    model_code: Mapped[str] = mapped_column(
        String(100), nullable=False, default="PURCHASE_REPEAT", index=True
    )
    version: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    model_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[ModelLifecycleStatus] = mapped_column(
        String(20), nullable=False, default=ModelLifecycleStatus.TRAINED, index=True
    )
    dataset_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trained_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    feature_window_days: Mapped[int | None] = mapped_column(nullable=True)
    prediction_horizon_days: Mapped[int | None] = mapped_column(nullable=True)
    precision: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    recall: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    f1_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    roc_auc: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    pr_auc: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    lift_top10: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    precision_top10: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 6), nullable=True
    )
    baseline_pr_auc: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    artifact_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


MLModelVersionModel = ModelRegistryModel
