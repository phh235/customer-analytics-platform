"""Get user use case — Business logic for getting a user by ID."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetUserUseCase(BaseUseCase[tuple[str], UserReadModel]):
    """Get user use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str]) -> UserReadModel:
        raise NotImplementedError()


class GetUserUseCaseImpl(GetUserUseCase):
    """Get user use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str]) -> UserReadModel:
        (user_id,) = args

        user = await self.unit_of_work.repository.find_by_id(user_id)
        if user is None:
            raise AppException(
                error_code=ErrorCode.USER_NOT_FOUND,
                message=f"User '{user_id}' not found",
            )

        return UserReadModel.from_entity(user)
