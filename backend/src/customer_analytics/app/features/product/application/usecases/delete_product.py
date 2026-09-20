"""Delete product use case — Business logic for deleting a product."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.product.application.dto.product_query_model import (  # noqa: E501
    ProductReadModel,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class DeleteProductUseCase(BaseUseCase[tuple[str], ProductReadModel]):
    """Delete product use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> ProductReadModel:
        raise NotImplementedError()


class DeleteProductUseCaseImpl(DeleteProductUseCase):
    """Delete product use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[str]) -> ProductReadModel:
        (product_id,) = args

        # Find existing product
        product = await self.repository.find_by_id(product_id)
        if product is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Product with ID '{product_id}' không tồn tại.",
            )

        # Soft delete (set status to INACTIVE)
        product.status = "INACTIVE"
        updated_product = await self.repository.update(product)

        return ProductReadModel.from_entity(updated_product)
