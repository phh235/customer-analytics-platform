"""Identity domain repositories — Repository interfaces."""

from customer_analytics.app.features.identity.domain.repositories.user_repository import (
    UserRepository,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)

__all__ = ["UserRepository", "UserUnitOfWork"]
