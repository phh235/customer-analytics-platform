"""Get products use case — Business logic for listing products."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.product.application.dto.product_query_model import (  # noqa: E501
    ProductListResult,
    ProductReadModel,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetProductsUseCase(BaseUseCase[tuple[int, int, str | None], ProductListResult]):
    """Get products use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[int, int, str | None]) -> ProductListResult:
        raise NotImplementedError()


class GetProductsUseCaseImpl(GetProductsUseCase):
    """Get products use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[int, int, str | None]) -> ProductListResult:
        skip, limit, category = args

        products, total = await self.repository.find_page(
            skip=skip,
            limit=limit,
            category=category,
        )

        pages = (total + limit - 1) // limit if limit > 0 else 1
        current = (skip // limit) + 1 if limit > 0 else 1

        return ProductListResult(
            current=current,
            size=limit,
            total=total,
            pages=pages,
            records=[ProductReadModel.from_entity(p) for p in products],
        )
