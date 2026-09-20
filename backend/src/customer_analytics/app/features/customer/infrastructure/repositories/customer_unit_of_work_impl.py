"""Customer Unit of Work implementation."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.customer.domain.repositories.customer_unit_of_work import (
    CustomerUnitOfWork,
)
from customer_analytics.app.features.customer.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)


class CustomerUnitOfWorkImpl(CustomerUnitOfWork):
    """Customer Unit of Work implementation using SQLAlchemy."""

    def __init__(
        self,
        session: AsyncSession,
        current_user: UserEntity | None = None,
    ) -> None:
        self._session = session
        self.repository = CustomerRepositoryImpl(session, current_user)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
