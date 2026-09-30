"""Public user registration use case."""

from __future__ import annotations

from customer_analytics.app.features.identity.application.dto.user_command_model import (
    UserCreateModel,
)
from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserReadModel,
)
from customer_analytics.app.features.identity.application.usecases.create_user import (
    CreateUserUseCaseImpl,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)


class RegisterUserUseCaseImpl:
    """Create a customer-facing account with the fixed USER role."""

    def __init__(self, unit_of_work: UserUnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    async def __call__(
        self, email: str, password: str, full_name: str
    ) -> UserReadModel:
        """Register a public user without accepting privilege fields."""
        data = UserCreateModel(
            email=email,
            password=password,
            full_name=full_name,
            role_code="USER",
            team_id=None,
        )
        return await CreateUserUseCaseImpl(self.unit_of_work)((data,))
