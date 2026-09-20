"""Consolidation use case — Consolidate customer data."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from customer_analytics.app.features.import_data.application.services.consolidation_service import (
    ConsolidationResult,
    CustomerConsolidationService,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase


class ConsolidateCustomersUseCase(
    BaseUseCase[
        tuple[list[dict[str, Any]], list[dict[str, Any]] | None], ConsolidationResult
    ]
):
    """Consolidate customers use case interface."""

    @abstractmethod
    async def __call__(
        self, args: tuple[list[dict[str, Any]], list[dict[str, Any]] | None]
    ) -> ConsolidationResult:
        raise NotImplementedError()


class ConsolidateCustomersUseCaseImpl(ConsolidateCustomersUseCase):
    """Consolidate customers use case implementation."""

    def __init__(self, customer_repository, order_repository=None):
        self.service = CustomerConsolidationService(
            customer_repository=customer_repository,
            order_repository=order_repository,
        )

    async def __call__(
        self, args: tuple[list[dict[str, Any]], list[dict[str, Any]] | None]
    ) -> ConsolidationResult:
        customers, orders = args
        return await self.service.consolidate(customers, orders)
