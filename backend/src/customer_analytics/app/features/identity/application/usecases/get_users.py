"""Get users use case — Business logic for listing users with pagination."""

from __future__ import annotations

import uuid
from abc import abstractmethod

from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserListQueryModel,
    UserListReadModel,
    UserReadModel,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GetUsersUseCase(BaseUseCase[UserListQueryModel, UserListReadModel]):
    """Get users use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: UserListQueryModel) -> UserListReadModel:
        raise NotImplementedError()


class GetUsersUseCaseImpl(GetUsersUseCase):
    """Get users use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: UserListQueryModel) -> UserListReadModel:
        users = await self.unit_of_work.repository.find_all(
            skip=args.skip,
            limit=args.limit,
            search=args.search,
            role_code=args.role_code,
            status=args.status,
            sort_by=args.sort_by,
            sort_order=args.sort_order,
        )
        total = await self.unit_of_work.repository.count_users(
            search=args.search,
            role_code=args.role_code,
            status=args.status,
        )

        # Batch load permissions for all users in a single query
        user_ids = [user.id_ for user in users if user.id_ is not None]
        permissions_map = (
            await self.unit_of_work.repository.get_users_permissions_batch(user_ids)
            if user_ids
            else {}
        )

        records = []
        for u in users:
            if u.id_ is None:
                raise ValueError("Persisted user is missing an ID")

            permissions = permissions_map.get(u.id_, [])
            records.append(
                UserReadModel(
                    id=uuid.UUID(u.id_),
                    email=u.email,
                    full_name=u.full_name,
                    status=u.status,
                    role_code=u.role_code,
                    permissions=permissions,
                    created_at=u.created_at,
                    last_login_at=u.last_login_at,
                )
            )

        pages = (total + args.limit - 1) // args.limit
        current = args.skip // args.limit + 1

        return UserListReadModel(
            current=current,
            size=args.limit,
            total=total,
            pages=pages,
            records=records,
        )
