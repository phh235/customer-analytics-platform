"""Identity domain usecases — Re-exports for backward compatibility."""

from customer_analytics.app.features.identity.application.usecases.create_user import (
    CreateUserUseCase,
)
from customer_analytics.app.features.identity.application.usecases.delete_user import (
    DeleteUserUseCase,
)
from customer_analytics.app.features.identity.application.usecases.get_user import (
    GetUserUseCase,
)
from customer_analytics.app.features.identity.application.usecases.get_users import (
    GetUsersUseCase,
)
from customer_analytics.app.features.identity.application.usecases.login_user import (
    LoginUserUseCase,
)
from customer_analytics.app.features.identity.application.usecases.update_user import (
    UpdateUserUseCase,
)

__all__ = [
    "CreateUserUseCase",
    "GetUserUseCase",
    "GetUsersUseCase",
    "UpdateUserUseCase",
    "DeleteUserUseCase",
    "LoginUserUseCase",
]
