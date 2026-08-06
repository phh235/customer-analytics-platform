"""Update user use case — Business logic for updating user information."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
    UserUpdateModel,
)
from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class UpdateUserUseCase(BaseUseCase[tuple[str, UserUpdateModel], UserReadModel]):
    """Update user use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str, UserUpdateModel]) -> UserReadModel:
        raise NotImplementedError()


class UpdateUserUseCaseImpl(UpdateUserUseCase):
    """Update user use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str, UserUpdateModel]) -> UserReadModel:
        user_id, update_data = args

        user = await self.unit_of_work.repository.find_by_id(user_id)
        if user is None:
            raise AppException(
                error_code=ErrorCode.USER_NOT_FOUND,
                message=f"User '{user_id}' not found",
            )

        # Update user fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for attr_name, value in update_dict.items():
            setattr(user, attr_name, value)

        try:
            updated_user = await self.unit_of_work.repository.update(user)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return UserReadModel.from_entity(updated_user)
