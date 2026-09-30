"""Delete user use case — Business logic for disabling a user."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class DeleteUserUseCase(BaseUseCase[tuple[str, str], UserReadModel]):
    """Delete user use case interface (soft delete — disable)."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str, str]) -> UserReadModel:
        raise NotImplementedError()


class DeleteUserUseCaseImpl(DeleteUserUseCase):
    """Delete user use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str, str]) -> UserReadModel:
        user_id, current_user_id = args

        # Cannot disable yourself
        if user_id == current_user_id:
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

        # Disable user
        disabled_user = user.disable()

        try:
            updated_user = await self.unit_of_work.repository.update(disabled_user)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        await self.unit_of_work.commit()

        return UserReadModel.from_entity(updated_user)
