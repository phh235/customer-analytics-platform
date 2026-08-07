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
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from customer_analytics.app.config import settings
from customer_analytics.app.features.identity.application.usecases.login_user import (
    LoginUserUseCaseImpl,
)
from customer_analytics.app.features.identity.infrastructure.jwt_service import (
    create_access_token,
    create_refresh_token,
    create_refresh_token_family,
    decode_refresh_token,
    hash_refresh_token,
)
from customer_analytics.app.features.identity.infrastructure.repositories.refresh_token_repository_impl import (  # noqa: E501
    RefreshTokenRepositoryImpl,
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
from customer_analytics.core.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


# ── Refresh Token Cookie Settings ───────────────────────────
# Only refresh_token goes in HTTP-only cookie
# access_token stays in response body for frontend to use
REFRESH_TOKEN_COOKIE = "refresh_token"

# HTTP-only cookies: JavaScript can't access (prevents XSS)
# SameSite=Strict: Browser won't send on cross-site requests (prevents CSRF)
# secure=True: Only send over HTTPS (set False for local dev only)
COOKIE_SECURE = settings.APP_ENV == "production"
COOKIE_SAMESITE = "strict"
COOKIE_PATH = "/api/v1/auth"  # Only send to auth endpoints
COOKIE_MAX_AGE_SECONDS = settings.JWT_REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60


def _set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Set HTTP-only refresh token cookie."""
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=COOKIE_MAX_AGE_SECONDS,
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


def _get_refresh_token_repository(
    session: DatabaseSessionDep,
) -> RefreshTokenRepositoryImpl:
    """Dependency to get refresh token repository."""
    return RefreshTokenRepositoryImpl(session)


# Type alias for UnitOfWork dependency
UnitOfWorkDep = Annotated[UserUnitOfWorkImpl, Depends(_get_user_unit_of_work)]

# Type alias for RefreshTokenRepository dependency
RefreshTokenRepoDep = Annotated[
    RefreshTokenRepositoryImpl, Depends(_get_refresh_token_repository)
]


def _to_uuid(value: str | uuid.UUID) -> uuid.UUID:
    """Convert value to UUID (handles both str and UUID)."""
    return uuid.UUID(value) if isinstance(value, str) else value


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
@limiter.limit("5/minute")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    unit_of_work: UnitOfWorkDep,
    refresh_token_repo: RefreshTokenRepoDep,
) -> LoginResponse:
    """Dang nhap bang email/password.

    - access_token: Returned in response body (frontend stores in memory)
    - refresh_token: Set as HTTP-only cookie (browser auto-sends on refresh)
    """
    use_case = LoginUserUseCaseImpl(unit_of_work)
    user = await use_case((body.email, body.password))

    # Create tokens
    access_token = create_access_token(
        user_id=user.id_,
        role_code=user.role_code,
        permissions=user.permissions,
    )
    family_id = create_refresh_token_family()
    refresh_token = create_refresh_token(user_id=user.id_, family_id=family_id)

    # Save refresh token to DB
    token_hash = hash_refresh_token(refresh_token)
    expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_TTL_DAYS)
    await refresh_token_repo.save(
        token_hash=token_hash,
        user_id=_to_uuid(user.id_),
        family_id=family_id,
        expires_at=expires_at,
        created_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Commit all changes (user update + refresh token insert)
    await unit_of_work.commit()

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
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
    unit_of_work: UnitOfWorkDep,
    refresh_token_repo: RefreshTokenRepoDep,
) -> LoginResponse:
    """Lam moi access token bang refresh token.

    - Reads refresh_token from HTTP-only cookie (auto-sent by browser)
    - Returns new access_token in response body
    - Sets new refresh_token in HTTP-only cookie
    - Revokes old refresh token (rotation)
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
    user_id = payload.get("sub")
    family_id = payload.get("family_id")

    if not user_id:
        raise AppException(
            error_code=ErrorCode.INVALID_REFRESH_TOKEN,
            message="Invalid refresh token payload.",
        )

    # Check if token is revoked in DB
    token_hash = hash_refresh_token(refresh_token_value)
    stored_token = await refresh_token_repo.find_by_token_hash(token_hash)
    if stored_token and stored_token.get("revoked_at"):
        # Token reuse detected — revoke all tokens in this family
        if family_id:
            await refresh_token_repo.revoke_all_by_family(family_id)
        raise AppException(
            error_code=ErrorCode.REFRESH_TOKEN_REUSED,
            message="Refresh token đã bị sử dụng lại — tất cả session đã bị thu hồi.",
        )

    # Find user
    user = await unit_of_work.repository.find_by_id(user_id)
    if not user:
        raise AppException(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message="User not found.",
        )

    # Check if user is active
    if user.status != "ACTIVE":
        raise AppException(
            error_code=ErrorCode.USER_DISABLED,
            message="Tài khoản đã bị vô hiệu hóa.",
        )

    # Revoke old refresh token
    await refresh_token_repo.revoke_by_token_hash(token_hash)

    # Create new tokens with same family_id
    new_access_token = create_access_token(
        user_id=user.id_,
        role_code=user.role_code,
        permissions=user.permissions,
    )
    new_family_id = family_id or create_refresh_token_family()
    new_refresh_token = create_refresh_token(user_id=user.id_, family_id=new_family_id)

    # Save new refresh token to DB
    new_token_hash = hash_refresh_token(new_refresh_token)
    expires_at = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_TTL_DAYS)
    await refresh_token_repo.save(
        token_hash=new_token_hash,
        user_id=_to_uuid(user.id_),
        family_id=new_family_id,
        expires_at=expires_at,
        created_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    # Commit all changes (revoke old token + insert new token)
    await unit_of_work.commit()

    # Set new refresh token in HTTP-only cookie
    _set_refresh_token_cookie(response, new_refresh_token)

    # Return new access token in response body
    return LoginResponse(
        access_token=new_access_token,
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
    request: Request,
    response: Response,
    current_user: CurrentUserDep,
    refresh_token_repo: RefreshTokenRepoDep,
) -> MessageResponse:
    """Dang xuat (thu hoi current session).

    - Clears refresh token HTTP-only cookie
    - Revokes refresh token in database (blacklist)
    - Frontend should also clear access_token from memory
    """
    # Read refresh token from cookie and revoke in DB
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if refresh_token_value:
        token_hash = hash_refresh_token(refresh_token_value)
        await refresh_token_repo.revoke_by_token_hash(token_hash)

    # Clear refresh token cookie
    _clear_refresh_token_cookie(response)
    return MessageResponse(message="Dang xuat thanh cong.")
