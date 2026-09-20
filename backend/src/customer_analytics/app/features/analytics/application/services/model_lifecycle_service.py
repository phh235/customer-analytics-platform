"""Explicit prediction-model evaluation and deployment workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.infrastructure.models.model_registry import (  # noqa: E501
    ModelLifecycleStatus,
    ModelRegistryModel,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class ModelLifecycleService:
    """Enforce trained, evaluated, approved, and deployed transitions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def register_trained(
        self,
        version: str,
        artifact_uri: str | None = None,
        baseline_pr_auc: Decimal | None = None,
        model_type: str | None = None,
        feature_window_days: int | None = None,
        prediction_horizon_days: int | None = None,
    ) -> ModelRegistryModel:
        """Register a trained artifact without deploying it."""
        existing = await self._get(version)
        if existing is not None:
            raise AppException(
                ErrorCode.RESOURCE_EXISTS,
                f"Model version '{version}' is already registered.",
            )
        now = datetime.now(UTC)
        model = ModelRegistryModel(
            version=version,
            status=ModelLifecycleStatus.TRAINED,
            baseline_pr_auc=baseline_pr_auc
            or Decimal(str(settings.ML_BASELINE_PR_AUC)),
            artifact_uri=artifact_uri,
            model_type=model_type,
            feature_window_days=feature_window_days,
            prediction_horizon_days=prediction_horizon_days,
            created_at=now,
            updated_at=now,
        )
        self._session.add(model)
        await self._session.flush()
        return model

    @staticmethod
    def acceptance_passes(
        *,
        pr_auc: Decimal,
        lift_top10: Decimal,
        precision_top10: Decimal | None,
        overall_conversion: Decimal | None,
        baseline_pr_auc: Decimal,
    ) -> bool:
        """Return whether a candidate clears every configured acceptance gate."""
        precision_passes = True
        if precision_top10 is not None and overall_conversion is not None:
            precision_passes = precision_top10 >= (
                Decimal(str(settings.ML_MIN_PRECISION_TOP10_MULTIPLIER))
                * overall_conversion
            )
        return (
            pr_auc > baseline_pr_auc
            and lift_top10 >= Decimal(str(settings.ML_MIN_LIFT_TOP10))
            and precision_passes
        )

    async def evaluate(
        self,
        version: str,
        pr_auc: Decimal,
        lift_top10: Decimal,
        precision_top10: Decimal | None = None,
        overall_conversion: Decimal | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> ModelRegistryModel:
        """Evaluate a candidate and approve it only when every gate passes."""
        model = await self._require(version)
        if model.status not in {
            ModelLifecycleStatus.TRAINED,
            ModelLifecycleStatus.EVALUATING,
        }:
            raise AppException(
                ErrorCode.INVALID_OPERATION,
                f"Model '{version}' cannot be evaluated from {model.status}.",
            )
        model.status = ModelLifecycleStatus.EVALUATING
        model.pr_auc = pr_auc
        model.lift_top10 = lift_top10
        model.precision_top10 = precision_top10
        model.precision = (
            Decimal(str(metrics["precision"]))
            if metrics and "precision" in metrics
            else None
        )
        model.recall = (
            Decimal(str(metrics["recall"])) if metrics and "recall" in metrics else None
        )
        model.f1_score = (
            Decimal(str(metrics["f1_score"]))
            if metrics and "f1_score" in metrics
            else None
        )
        model.roc_auc = (
            Decimal(str(metrics["roc_auc"]))
            if metrics and "roc_auc" in metrics
            else None
        )
        model.metrics = metrics
        model.evaluated_at = datetime.now(UTC)
        if self.acceptance_passes(
            pr_auc=pr_auc,
            lift_top10=lift_top10,
            precision_top10=precision_top10,
            overall_conversion=overall_conversion,
            baseline_pr_auc=model.baseline_pr_auc,
        ):
            model.status = ModelLifecycleStatus.APPROVED
        await self._session.flush()
        return model

    async def deploy(self, version: str) -> ModelRegistryModel:
        """Deploy an approved version and leave all other versions undeployed."""
        model = await self._require(version)
        if model.status != ModelLifecycleStatus.APPROVED:
            raise AppException(
                ErrorCode.INVALID_OPERATION,
                f"Only APPROVED models can be deployed; got {model.status}.",
            )
        await self._session.execute(
            update(ModelRegistryModel)
            .where(ModelRegistryModel.status == ModelLifecycleStatus.DEPLOYED)
            .values(status=ModelLifecycleStatus.APPROVED)
        )
        model.status = ModelLifecycleStatus.DEPLOYED
        await self._session.flush()
        return model

    async def get_deployed(self) -> ModelRegistryModel | None:
        """Return the one explicitly deployed model, if any."""
        result = await self._session.execute(
            select(ModelRegistryModel).where(
                ModelRegistryModel.status == ModelLifecycleStatus.DEPLOYED
            )
        )
        return result.scalar_one_or_none()

    async def list_models(self) -> list[ModelRegistryModel]:
        """Return registered model versions newest first."""
        result = await self._session.execute(
            select(ModelRegistryModel).order_by(ModelRegistryModel.created_at.desc())
        )
        return list(result.scalars().all())

    async def _get(self, version: str) -> ModelRegistryModel | None:
        result = await self._session.execute(
            select(ModelRegistryModel).where(ModelRegistryModel.version == version)
        )
        return result.scalar_one_or_none()

    async def _require(self, version: str) -> ModelRegistryModel:
        model = await self._get(version)
        if model is None:
            raise AppException(
                ErrorCode.NOT_FOUND,
                f"Model version '{version}' was not found.",
            )
        return model
