"""Create user use case — Business logic for creating a new user."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
    UserCreateModel,
)
from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class CreateUserUseCase(BaseUseCase[tuple[UserCreateModel], UserReadModel]):
    """Create user use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[UserCreateModel]) -> UserReadModel:
        raise NotImplementedError()


class CreateUserUseCaseImpl(CreateUserUseCase):
    """Create user use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[UserCreateModel]) -> UserReadModel:
        (data,) = args

        # Check if user already exists
        existing_user = await self.unit_of_work.repository.find_by_email(data.email)
        if existing_user is not None:
            raise AppException(
                error_code=ErrorCode.EMAIL_EXISTS,
                message=f"Email '{data.email}' đã được đăng ký.",
            )

        role_code = data.role_code.upper()
        role_id = await self.unit_of_work.repository.find_role_id_by_code(role_code)
        if role_id is None:
            raise AppException(
                error_code=ErrorCode.ROLE_NOT_FOUND,
                message=f"Role '{role_code}' not found.",
            )

        # Never store a plaintext password in the domain entity or database.
        user = UserEntity(
            id_=None,
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role_code=role_code,
            role_id=str(role_id),
        )

        try:
            created_user = await self.unit_of_work.repository.create(user)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return UserReadModel.from_entity(created_user)
