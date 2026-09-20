"""Identity security — JWT scheme and auth dependencies.

Security Pattern:
- access_token: Read from Authorization header (frontend sends manually)
- refresh_token: Read from HTTP-only cookie (browser auto-sends)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.infrastructure.jwt_service import (
    decode_access_token,
)
from customer_analytics.app.features.identity.infrastructure.repositories.user_repository_impl import (  # noqa: E501
    UserRepositoryImpl,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.dependencies import DatabaseSessionDep

# Security scheme for OAuth2 password flow
# tokenUrl: Swagger UI sẽ gọi endpoint này để login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_user_repository(session: DatabaseSessionDep) -> UserRepositoryImpl:
    """Dependency to get user repository."""
    return UserRepositoryImpl(session)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepositoryImpl, Depends(get_user_repository)],
) -> UserEntity:
    """Get current authenticated user from access token.

    Reads access_token from Authorization header (Bearer token).
    Frontend stores access_token in memory after login and sends it on each request.

    Raises:
        AppException: 401 if token is invalid or user not found.
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AppException(
                error_code=ErrorCode.TOKEN_INVALID,
                message="Invalid token: missing subject",
            )

        user = await user_repo.find_by_id(user_id)
        if not user:
            raise AppException(
                error_code=ErrorCode.USER_NOT_FOUND,
                message=f"User '{user_id}' not found",
            )

        if user.status != "ACTIVE":
            error_code = (
                ErrorCode.USER_LOCKED
                if user.status == "LOCKED"
                else ErrorCode.USER_DISABLED
            )
            raise AppException(error_code=error_code)

        # Resolve authorization from the database so role/permission changes
        # take effect without waiting for the access token to expire.
        user.permissions = await user_repo.get_user_permissions(user.id_)

        return user
    except AppException:
        raise
    except Exception as e:
        raise AppException(
            error_code=ErrorCode.TOKEN_INVALID,
            message=f"Cannot authenticate: {e}",
        ) from None


def require_permission(permission: str) -> Callable[..., object]:
    """Dependency factory to require specific permission.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_permission("users:read"))])
    """

    async def _check_permission(
        current_user: Annotated[UserEntity, Depends(get_current_user)],
    ) -> UserEntity:
        if permission not in current_user.permissions:
            raise AppException(
                error_code=ErrorCode.PERMISSION_DENIED,
                message=f"Không có quyền '{permission}'.",
            )
        return current_user

    return _check_permission


def require_admin(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
) -> UserEntity:
    """Dependency to require ADMIN role."""
    if current_user.role_code != "ADMIN":
        raise AppException(
            error_code=ErrorCode.PERMISSION_DENIED,
            message="Admin access required",
        )
    return current_user
