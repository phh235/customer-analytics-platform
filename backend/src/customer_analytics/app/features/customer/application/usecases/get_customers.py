"""Get customers use case — Business logic for listing customers."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.customer.application.dto.customer_query_model import (  # noqa: E501
    CustomerListResult,
    CustomerReadModel,
)
from customer_analytics.app.features.customer.domain.repositories.customer_unit_of_work import (  # noqa: E501
    CustomerUnitOfWork,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetCustomersUseCase(BaseUseCase[tuple[int, int, str | None], CustomerListResult]):
    """Get customers use case interface."""

    unit_of_work: CustomerUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[int, int, str | None]) -> CustomerListResult:
        raise NotImplementedError()


class GetCustomersUseCaseImpl(GetCustomersUseCase):
    """Get customers use case implementation."""

    def __init__(self, unit_of_work: CustomerUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[int, int, str | None]) -> CustomerListResult:
        (skip, limit, search) = args

        customers = await self.unit_of_work.repository.find_all(
            skip=skip, limit=limit, search=search
        )
        total = await self.unit_of_work.repository.count_customers(search=search)
        pages = (total + limit - 1) // limit if limit > 0 else 1
        current = (skip // limit) + 1 if limit > 0 else 1

        return CustomerListResult(
            current=current,
            size=limit,
            total=total,
            pages=pages,
            records=[CustomerReadModel.from_entity(c) for c in customers],
        )
