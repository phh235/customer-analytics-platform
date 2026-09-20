"""Update customer use case — Business logic for updating a customer."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.customer.application.dto.customer_command_model import (
    CustomerUpdateModel,
)
from customer_analytics.app.features.customer.application.dto.customer_query_model import (
    CustomerReadModel,
)
from customer_analytics.app.features.customer.domain.repositories.customer_unit_of_work import (
    CustomerUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class UpdateCustomerUseCase(
    BaseUseCase[tuple[str, CustomerUpdateModel], CustomerReadModel]
):
    """Update customer use case interface."""

    unit_of_work: CustomerUnitOfWork

    @abstractmethod
    async def __call__(
        self, args: tuple[str, CustomerUpdateModel]
    ) -> CustomerReadModel:
        raise NotImplementedError()


class UpdateCustomerUseCaseImpl(UpdateCustomerUseCase):
    """Update customer use case implementation."""

    def __init__(self, unit_of_work: CustomerUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(
        self, args: tuple[str, CustomerUpdateModel]
    ) -> CustomerReadModel:
        (customer_id, data) = args

        # Find existing customer
        customer = await self.unit_of_work.repository.find_by_id(customer_id)
        if customer is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Customer '{customer_id}' not found.",
            )

        # Check email uniqueness if changed
        if data.email and data.email != customer.email:
            existing = await self.unit_of_work.repository.find_by_email(data.email)
            if existing is not None:
                raise AppException(
                    error_code=ErrorCode.EMAIL_EXISTS,
                    message=f"Email '{data.email}' đã được sử dụng.",
                )

        # Check phone uniqueness if changed
        if data.phone and data.phone != customer.phone:
            existing = await self.unit_of_work.repository.find_by_phone(data.phone)
            if existing is not None:
                raise AppException(
                    error_code=ErrorCode.RESOURCE_EXISTS,
                    message=f"Phone '{data.phone}' đã được sử dụng.",
                )

        # Update entity
        update_data = data.model_dump(exclude_unset=True)
        updated_customer = customer.update(**update_data)

        try:
            saved_customer = await self.unit_of_work.repository.update(updated_customer)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return CustomerReadModel.from_entity(saved_customer)
