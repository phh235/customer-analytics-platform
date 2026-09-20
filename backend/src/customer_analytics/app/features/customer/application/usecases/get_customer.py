"""Get customer use case — Business logic for getting a customer."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.customer.application.dto.customer_query_model import (  # noqa: E501
    CustomerReadModel,
)
from customer_analytics.app.features.customer.domain.repositories.customer_unit_of_work import (  # noqa: E501
    CustomerUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetCustomerUseCase(BaseUseCase[tuple[str], CustomerReadModel]):
    """Get customer use case interface."""

    unit_of_work: CustomerUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> CustomerReadModel:
        raise NotImplementedError()


class GetCustomerUseCaseImpl(GetCustomerUseCase):
    """Get customer use case implementation."""

    def __init__(self, unit_of_work: CustomerUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str]) -> CustomerReadModel:
        (customer_id,) = args

        customer = await self.unit_of_work.repository.find_by_id(customer_id)
        if customer is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )

        return CustomerReadModel.from_entity(customer)
