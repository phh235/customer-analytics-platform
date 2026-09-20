"""Create product use case — Business logic for creating a new product."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.product.application.dto.product_command_model import (  # noqa: E501
    ProductCreateModel,
)
from customer_analytics.app.features.product.application.dto.product_query_model import (  # noqa: E501
    ProductReadModel,
)
from customer_analytics.app.features.product.domain.entities.product_entity import (
    ProductEntity,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class CreateProductUseCase(BaseUseCase[tuple[ProductCreateModel], ProductReadModel]):
    """Create product use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[ProductCreateModel]) -> ProductReadModel:
        raise NotImplementedError()


class CreateProductUseCaseImpl(CreateProductUseCase):
    """Create product use case implementation."""

    def __init__(self, repository):
        self.repository = repository

    async def __call__(self, args: tuple[ProductCreateModel]) -> ProductReadModel:
        (data,) = args

        # Check if product name already exists
        existing = await self.repository.find_by_name(data.name)
        if existing is not None:
            raise AppException(
                error_code=ErrorCode.RESOURCE_EXISTS,
                message=f"Product '{data.name}' đã tồn tại.",
            )
        product_code = await self.repository.next_product_code()


        # Create entity
        product = ProductEntity(
            id_=None,
            product_code=product_code,
            name=data.name,
            category=data.category,
            price=data.price,
            status=data.status,
            sku=data.sku,
            description=data.description,
            image_url=data.image_url,
        )

        created_product = await self.repository.create(product)
        return ProductReadModel.from_entity(created_product)
