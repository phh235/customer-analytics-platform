"""Identity presentation dependencies — Type aliases for route injection.

Re-export from security.py for convenient imports in routes:
    from ..dependencies import CurrentUserDep, AdminDep, require_permission
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation.security import (
    get_current_user,
    require_admin,
    require_permission,
)

CurrentUserDep = Annotated[UserEntity, Depends(get_current_user)]
AdminDep = Annotated[UserEntity, Depends(require_admin)]

__all__ = [
    "AdminDep",
    "CurrentUserDep",
    "get_current_user",
    "require_admin",
    "require_permission",
]
