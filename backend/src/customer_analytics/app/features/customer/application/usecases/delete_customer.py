"""Delete customer use case — Business logic for soft deleting a customer."""

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


class DeleteCustomerUseCase(BaseUseCase[tuple[str], CustomerReadModel]):
    """Delete customer use case interface."""

    unit_of_work: CustomerUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> CustomerReadModel:
        raise NotImplementedError()


class DeleteCustomerUseCaseImpl(DeleteCustomerUseCase):
    """Delete customer use case implementation (soft delete)."""

    def __init__(self, unit_of_work: CustomerUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str]) -> CustomerReadModel:
        (customer_id,) = args

        # Find existing customer
        customer = await self.unit_of_work.repository.find_by_id(customer_id)
        if customer is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )

        # Soft delete (set status to INACTIVE)
        disabled_customer = customer.disable()

        try:
            saved_customer = await self.unit_of_work.repository.update(
                disabled_customer
            )
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return CustomerReadModel.from_entity(saved_customer)
