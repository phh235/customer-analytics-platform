"""Get product use case — Business logic for getting a single product."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.product.application.dto.product_query_model import (  # noqa: E501
    ProductReadModel,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetProductUseCase(BaseUseCase[tuple[str], ProductReadModel]):
    """Get product use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> ProductReadModel:
        raise NotImplementedError()


class GetProductUseCaseImpl(GetProductUseCase):
    """Get product use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[str]) -> ProductReadModel:
        (product_id,) = args

        product = await self.repository.find_by_id(product_id)
        if product is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Product with ID '{product_id}' không tồn tại.",
            )

        return ProductReadModel.from_entity(product)
