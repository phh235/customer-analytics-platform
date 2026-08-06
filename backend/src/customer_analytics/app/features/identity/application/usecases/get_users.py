"""Get users use case — Business logic for listing users with pagination."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserListReadModel,
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetUsersUseCase(BaseUseCase[tuple[int, int, str | None], UserListReadModel]):
    """Get users use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[int, int, str | None]) -> UserListReadModel:
        raise NotImplementedError()


class GetUsersUseCaseImpl(GetUsersUseCase):
    """Get users use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[int, int, str | None]) -> UserListReadModel:
        skip, limit, search = args

        users = await self.unit_of_work.repository.find_all(
            skip=skip, limit=limit, search=search
        )
        total = await self.unit_of_work.repository.count_users(search=search)

        # Batch load permissions for all users in a single query
        user_ids = [u.id_ for u in users]
        permissions_map = (
            await self.unit_of_work.repository.get_users_permissions_batch(user_ids)
            if user_ids
            else {}
        )

        records = []
        for u in users:
            permissions = permissions_map.get(u.id_, [])
            records.append(
                UserReadModel(
                    id=u.id_,
                    email=u.email,
                    full_name=u.full_name,
                    status=u.status,
                    role_code=u.role_code,
                    permissions=permissions,
                    created_at=u.created_at,
                    last_login_at=u.last_login_at,
                )
            )

        pages = (total + limit - 1) // limit if limit > 0 else 0
        current = skip // limit + 1 if limit > 0 else 1

        return UserListReadModel(
            current=current,
            size=limit,
            total=total,
            pages=pages,
            records=records,
        )
