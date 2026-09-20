"""Create customer use case — Business logic for creating a new customer."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.customer.application.dto.customer_command_model import (  # noqa: E501
    CustomerCreateModel,
)
from customer_analytics.app.features.customer.application.dto.customer_query_model import (  # noqa: E501
    CustomerReadModel,
)
from customer_analytics.app.features.customer.domain.entities.customer_entity import (
    CustomerEntity,
)
from customer_analytics.app.features.customer.domain.repositories.customer_unit_of_work import (  # noqa: E501
    CustomerUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class CreateCustomerUseCase(BaseUseCase[tuple[CustomerCreateModel], CustomerReadModel]):
    """Create customer use case interface."""

    unit_of_work: CustomerUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[CustomerCreateModel]) -> CustomerReadModel:
        raise NotImplementedError()


class CreateCustomerUseCaseImpl(CreateCustomerUseCase):
    """Create customer use case implementation."""

    def __init__(self, unit_of_work: CustomerUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[CustomerCreateModel]) -> CustomerReadModel:
        (data,) = args

        # Check if email already exists
        if data.email:
            existing = await self.unit_of_work.repository.find_by_email(data.email)
            if existing is not None:
                raise AppException(
                    error_code=ErrorCode.EMAIL_EXISTS,
                    message=f"Email '{data.email}' đã được sử dụng.",
                )

        # Check if phone already exists
        if data.phone:
            existing = await self.unit_of_work.repository.find_by_phone(data.phone)
            if existing is not None:
                raise AppException(
                    error_code=ErrorCode.RESOURCE_EXISTS,
                    message=f"Phone '{data.phone}' đã được sử dụng.",
                )

        customer_code = await self.unit_of_work.repository.next_customer_code()

        # Create entity
        customer = CustomerEntity(
            id_=None,
            customer_code=customer_code,
            name=data.name,
            image_url=data.image_url,
            email=data.email,
            phone=data.phone,
            address=data.address,
        )

        try:
            created_customer = await self.unit_of_work.repository.create(customer)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return CustomerReadModel.from_entity(created_customer)
