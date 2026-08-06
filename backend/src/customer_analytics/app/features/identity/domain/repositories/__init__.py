"""Identity domain repositories — Repository interfaces."""

from customer_analytics.app.features.identity.domain.repositories.user_repository import (  # noqa: E501
    UserRepository,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)

__all__ = ["UserRepository", "UserUnitOfWork"]
