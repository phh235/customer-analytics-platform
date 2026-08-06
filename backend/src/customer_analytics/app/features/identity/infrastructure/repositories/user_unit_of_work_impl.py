"""User unit of work implementation — SQLAlchemy implementation."""

from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.features.identity.infrastructure.repositories.user_repository_impl import (  # noqa: E501
    UserRepositoryImpl,
)

logger = structlog.get_logger(__name__)


class UserUnitOfWorkImpl(UserUnitOfWork):
    """User unit of work using SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.repository = UserRepositoryImpl(session)

    async def commit(self) -> None:
        """Commit the transaction."""
        try:
            await self._session.commit()
            logger.debug("unit_of_work_committed")
        except Exception:
            logger.exception("unit_of_work_commit_failed")
            await self._session.rollback()
            raise

    async def rollback(self) -> None:
        """Rollback the transaction."""
        try:
            await self._session.rollback()
            logger.debug("unit_of_work_rolled_back")
        except Exception:
            logger.exception("unit_of_work_rollback_failed")
            raise
