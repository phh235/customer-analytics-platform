"""Product interest analytics repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class ProductInterestRepository(ABC):
    """Read-only product-interest analytics contract."""

    @abstractmethod
    async def get_product_summary(
        self, product_id: str, from_date: date, to_date: date
    ) -> dict[str, Any]:
        """Return product views and unique viewers for a date window."""
        raise NotImplementedError()

    @abstractmethod
    async def get_product_viewers(
        self, product_id: str, from_date: date, to_date: date, limit: int
    ) -> list[dict[str, Any]]:
        """Return customers ranked by product-view count."""
        raise NotImplementedError()

    @abstractmethod
    async def get_product_trend(
        self,
        product_id: str,
        from_date: date,
        to_date: date,
        group_by: str,
    ) -> list[dict[str, Any]]:
        """Return product-view counts grouped by time period."""
        raise NotImplementedError()

    @abstractmethod
    async def get_trending_products(
        self, to_date: date, period_days: int, limit: int
    ) -> list[dict[str, Any]]:
        """Return products ranked by current-versus-previous view growth."""
        raise NotImplementedError()
