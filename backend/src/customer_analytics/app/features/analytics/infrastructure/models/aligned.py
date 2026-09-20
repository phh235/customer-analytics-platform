"""Configuration and analysis-history models for the aligned data contract."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ConfigurationVersionModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Versioned analytics and segmentation configuration."""

    __tablename__ = "configuration_versions"

    version: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class ScoringRuleModel(UUIDPrimaryKeyMixin, Base):
    """Weighted component of a potential-score configuration."""

    __tablename__ = "scoring_rules"
    __table_args__ = (
        UniqueConstraint(
            "configuration_version_id",
            "component",
            name="uq_scoring_rules_version_component",
        ),
    )
    configuration_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    component: Mapped[str] = mapped_column(String(50), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ScoringThresholdModel(UUIDPrimaryKeyMixin, Base):
    """Scoring threshold used to normalize an analytics component."""

    __tablename__ = "scoring_thresholds"

    configuration_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    component: Mapped[str] = mapped_column(String(50), nullable=False)
    min_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    max_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    score: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class SegmentationRuleModel(UUIDPrimaryKeyMixin, Base):
    """Versioned rule for assigning a customer segment."""

    __tablename__ = "segmentation_rules"

    configuration_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    segment_code: Mapped[str] = mapped_column(String(50), nullable=False)
    min_potential_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    max_potential_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ValidOrderStatusConfigModel(UUIDPrimaryKeyMixin, Base):
    """Versioned inclusion rule for transaction analytics."""

    __tablename__ = "valid_order_status_configs"
    __table_args__ = (
        UniqueConstraint(
            "configuration_version_id",
            "order_status",
            name="uq_valid_order_status_config_version_status",
        ),
    )
    configuration_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    order_status: Mapped[str] = mapped_column(String(30), nullable=False)
    is_valid_for_analytics: Mapped[bool] = mapped_column(Boolean, nullable=False)


class AnalysisRunModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Auditable execution metadata for an analytics run."""

    __tablename__ = "analysis_runs"

    run_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False)
    data_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    executed_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    configuration_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("model_registry.id", ondelete="SET NULL"),
        nullable=True,
    )
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class CustomerBehaviorHistoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persisted customer behavior features for an analysis run."""

    __tablename__ = "customer_behavior_history"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    recency_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)
    monetary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    aov: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    avg_purchase_cycle_days: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    trend: Mapped[str | None] = mapped_column(String(30), nullable=True)
    avg_review_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )


class CustomerPotentialScoreHistoryModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persisted potential-score result for an analysis run."""

    __tablename__ = "customer_potential_score_history"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    r_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    f_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    m_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)
    interaction_score: Mapped[Decimal] = mapped_column(
        Numeric(6, 2), nullable=False, default=Decimal("0")
    )
    potential_score: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2), nullable=True
    )
    potential_level: Mapped[str] = mapped_column(String(30), nullable=False)
    configuration_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("configuration_versions.id", ondelete="SET NULL"),
        nullable=True,
    )


class CustomerProductPreferenceModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Persisted product preference result."""

    __tablename__ = "customer_product_preferences"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_category_name: Mapped[str] = mapped_column(String(100), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    purchase_frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monetary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    purchase_share: Mapped[Decimal] = mapped_column(Numeric(8, 5), nullable=False)
    last_purchase_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class MLModelEvaluationModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Evaluation metrics for a registered model version."""

    __tablename__ = "ml_model_evaluations"

    model_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("model_registry.id", ondelete="CASCADE"),
        nullable=False,
    )
    evaluation_dataset_version: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    precision: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    recall: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    f1_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    roc_auc: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    pr_auc: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    precision_at_k: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 6), nullable=True
    )
    recall_at_k: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    lift_at_k: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
