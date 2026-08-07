"""Update user use case — Business logic for updating user information."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
    UserUpdateModel,
)
from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.enums import UserStatus
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class UpdateUserUseCase(BaseUseCase[tuple[str, UserUpdateModel, str], UserReadModel]):
    """Update user use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str, UserUpdateModel, str]) -> UserReadModel:
        raise NotImplementedError()


class UpdateUserUseCaseImpl(UpdateUserUseCase):
    """Update user use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str, UserUpdateModel, str]) -> UserReadModel:
        user_id, update_data, current_user_id = args

        if user_id == current_user_id and update_data.status == UserStatus.DISABLED:
            raise AppException(
                error_code=ErrorCode.CANNOT_DISABLE_SELF,
                message="Không thể tự vô hiệu hóa tài khoản.",
            )

        user = await self.unit_of_work.repository.find_by_id(user_id)
        if user is None:
            raise AppException(
                error_code=ErrorCode.USER_NOT_FOUND,
                message=f"User '{user_id}' not found",
            )

        update_dict = update_data.model_dump(exclude_unset=True)

        role_code = update_dict.pop("role_code", None)
        if role_code is not None:
            role_code = role_code.upper()
            role_id = await self.unit_of_work.repository.find_role_id_by_code(role_code)
            if role_id is None:
                raise AppException(
                    error_code=ErrorCode.ROLE_NOT_FOUND,
                    message=f"Role '{role_code}' not found.",
                )
            user.role_code = role_code
            user.role_id = str(role_id)

        for attr_name, value in update_dict.items():
            if attr_name == "status" and hasattr(value, "value"):
                value = value.value
            setattr(user, attr_name, value)

        try:
            updated_user = await self.unit_of_work.repository.update(user)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return UserReadModel.from_entity(updated_user)
