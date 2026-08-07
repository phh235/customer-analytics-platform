"""Auth routes — API endpoints for authentication.

Security Pattern:
- refresh_token: HTTP-only cookie (browser auto-manages, JS can't access)
- access_token: Response body (frontend reads, stores in memory, sends
  via Authorization header)

Flow:
1. POST /login → access_token in body + refresh_token in HTTP-only cookie
2. POST /refresh → new access_token in body + new refresh_token in cookie
3. GET /me → Authorization: Bearer <access_token>
4. POST /logout → clear refresh_token cookie
"""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request, Response, status

from customer_analytics.app.config import settings
from customer_analytics.app.features.identity.application.usecases.login_user import (
    LoginUserUseCaseImpl,
)
from customer_analytics.app.features.identity.infrastructure.jwt_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from customer_analytics.app.features.identity.infrastructure.repositories.user_unit_of_work_impl import (  # noqa: E501
    UserUnitOfWorkImpl,
)
from customer_analytics.app.features.identity.presentation.dependencies import (
    CurrentUserDep,
)
from customer_analytics.app.features.identity.presentation.schema.user import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    UserResponse,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.dependencies import DatabaseSessionDep

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ── Refresh Token Cookie Settings ───────────────────────────
# Only refresh_token goes in HTTP-only cookie
# access_token stays in response body for frontend to use
REFRESH_TOKEN_COOKIE = "refresh_token"

# HTTP-only cookies: JavaScript can't access (prevents XSS)
# SameSite=Strict: Browser won't send on cross-site requests (prevents CSRF)
# secure=True: Only send over HTTPS (set False for local dev only)
COOKIE_SECURE = settings.APP_ENV == "production"
COOKIE_SAMESITE: Literal["strict"] = "strict"
COOKIE_PATH = "/api/v1/auth"  # Only send to auth endpoints


def _require_user_id(
    value: str | None,
    *,
    error_code: ErrorCode,
    message: str,
) -> tuple[str, uuid.UUID]:
    if value is None:
        raise AppException(error_code=error_code, message=message)

    try:
        return value, uuid.UUID(value)
    except ValueError:
        raise AppException(error_code=error_code, message=message) from None


def _set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Set HTTP-only refresh token cookie."""
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=settings.JWT_REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )


def _clear_refresh_token_cookie(response: Response) -> None:
    """Clear refresh token cookie (for logout)."""
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE,
        path=COOKIE_PATH,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
    )


def _get_user_unit_of_work(session: DatabaseSessionDep) -> UserUnitOfWorkImpl:
    """Dependency to get user unit of work."""
    return UserUnitOfWorkImpl(session)


# Type alias for UnitOfWork dependency
UnitOfWorkDep = Annotated[UserUnitOfWorkImpl, Depends(_get_user_unit_of_work)]


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Authenticate user. Returns access_token, sets refresh_token cookie.",
    responses={
        status.HTTP_200_OK: {
            "description": "Login successful",
            "model": LoginResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials",
            "model": ErrorResponse,
        },
    },
)
async def login(
    body: LoginRequest,
    response: Response,
    unit_of_work: UnitOfWorkDep,
) -> LoginResponse:
    """Dang nhap bang email/password.

    - access_token: Returned in response body (frontend stores in memory)
    - refresh_token: Set as HTTP-only cookie (browser auto-sends on refresh)
    """
    use_case = LoginUserUseCaseImpl(unit_of_work)
    user = await use_case((body.email, body.password))
    _, user_uuid = _require_user_id(
        user.id_,
        error_code=ErrorCode.INTERNAL_SERVER_ERROR,
        message="User account has an invalid ID.",
    )

    # Create tokens
    access_token = create_access_token(
        user_id=user_uuid,
        role_code=user.role_code,
        permissions=user.permissions,
    )
    refresh_token = create_refresh_token(user_id=user_uuid)

    # Set refresh token in HTTP-only cookie
    _set_refresh_token_cookie(response, refresh_token)

    # Return access token in response body (frontend reads this)
    return LoginResponse(
        access_token=access_token,
        role_code=user.role_code,
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token from HTTP-only cookie.",
    responses={
        status.HTTP_200_OK: {
            "description": "Token refreshed",
            "model": LoginResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or expired refresh token",
            "model": ErrorResponse,
        },
    },
)
async def refresh_token(
    request: Request,
    response: Response,
    unit_of_work: UnitOfWorkDep,
) -> LoginResponse:
    """Lam moi access token bang refresh token.

    - Reads refresh_token from HTTP-only cookie (auto-sent by browser)
    - Returns new access_token in response body
    - Sets new refresh_token in HTTP-only cookie
    """
    # Read refresh token from cookie
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not refresh_token_value:
        raise AppException(
            error_code=ErrorCode.INVALID_REFRESH_TOKEN,
            message="Refresh token cookie not found.",
        )

    # Decode and validate refresh token
    payload = decode_refresh_token(refresh_token_value)
    token_subject = payload.get("sub")

    if not isinstance(token_subject, str) or not token_subject:
        raise AppException(
            error_code=ErrorCode.INVALID_REFRESH_TOKEN,
            message="Invalid refresh token payload.",
        )

    # Find user
    user = await unit_of_work.repository.find_by_id(token_subject)
    if not user:
        raise AppException(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message="User not found.",
        )

    # Refresh tokens only contain the user ID. Load the current role
    # permissions before minting a new access token so permission changes
    # take effect after refresh instead of producing permissions: [].
    user_id, user_uuid = _require_user_id(
        user.id_,
        error_code=ErrorCode.INVALID_REFRESH_TOKEN,
        message="Invalid user ID in refresh session.",
    )
    user.permissions = await unit_of_work.repository.get_user_permissions(user_id)

    # Check if user is active
    if user.status != "ACTIVE":
        raise AppException(
            error_code=ErrorCode.USER_DISABLED,
            message="Tài khoản đã bị vô hiệu hóa.",
        )

    # Create new tokens
    access_token = create_access_token(
        user_id=user_uuid,
        role_code=user.role_code,
        permissions=user.permissions,
    )
    new_refresh_token = create_refresh_token(user_id=user_uuid)

    # Set new refresh token in HTTP-only cookie
    _set_refresh_token_cookie(response, new_refresh_token)

    # Return new access token in response body
    return LoginResponse(
        access_token=access_token,
        role_code=user.role_code,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get current authenticated user information.",
    responses={
        status.HTTP_200_OK: {
            "description": "User info",
            "model": UserResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid or missing token",
            "model": ErrorResponse,
        },
    },
)
async def get_me(
    current_user: CurrentUserDep,
) -> UserResponse:
    """Lay thong tin nguoi dung hien tai."""
    return UserResponse.from_entity(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Logout current session. Clears refresh token cookie.",
    responses={
        status.HTTP_200_OK: {
            "description": "Logout successful",
            "model": MessageResponse,
        },
    },
)
async def logout(
    response: Response,
    current_user: CurrentUserDep,
) -> MessageResponse:
    """Dang xuat (thu hoi current session).

    Clears refresh token HTTP-only cookie.
    Frontend should also clear access_token from memory.
    """
    _clear_refresh_token_cookie(response)
    # TODO: Add refresh token to blacklist in DB for extra security
    return MessageResponse(message="Dang xuat thanh cong.")
