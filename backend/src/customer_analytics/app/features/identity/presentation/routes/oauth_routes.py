"""OAuth routes — Google OAuth2 authentication.

Security Pattern (same as normal login):
- refresh_token: HTTP-only cookie (browser auto-manages, JS can't access)
- access_token: Redirect URL param (frontend reads, stores in memory)

Flow:
1. GET /google/login → redirect to Google consent screen
2. GET /google/callback → verify Google token → create/find user →
   set refresh_token cookie + redirect with access_token
"""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from customer_analytics.app.config import settings
from customer_analytics.app.features.identity.application.usecases.google_auth import (
    GoogleAuthUseCaseImpl,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.features.identity.infrastructure.jwt_service import (
    create_access_token,
    create_refresh_token,
    create_refresh_token_family,
    hash_refresh_token,
)
from customer_analytics.app.features.identity.infrastructure.oauth import oauth
from customer_analytics.app.features.identity.infrastructure.repositories.refresh_token_repository_impl import (  # noqa: E501
    RefreshTokenRepositoryImpl,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.database import get_db

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["auth"],
)


# ── Refresh Token Cookie Settings ───────────────────────────
REFRESH_TOKEN_COOKIE = "refresh_token"
COOKIE_PATH = "/api/v1/auth"
COOKIE_MAX_AGE_SECONDS = settings.JWT_REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60


def _cookie_security(request: Request) -> tuple[bool, str]:
    """Choose cookie flags that work locally and through HTTPS tunnels."""
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",", 1)[0]
    is_https = request.url.scheme == "https" or forwarded_proto.strip() == "https"
    return is_https, "none" if is_https else "lax"


def _set_refresh_token_cookie(
    request: Request,
    response: Response,
    refresh_token: str,
) -> None:
    """Set HTTP-only refresh token cookie."""
    secure, samesite = _cookie_security(request)
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path=COOKIE_PATH,
    )


async def _get_user_unit_of_work(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> UserUnitOfWork:
    """User unit of work dependency."""
    from customer_analytics.app.features.identity.infrastructure.repositories.user_unit_of_work_impl import (  # noqa: E501
        UserUnitOfWorkImpl,
    )

    return UserUnitOfWorkImpl(db)


async def _get_refresh_token_repository(
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> RefreshTokenRepositoryImpl:
    """Refresh token repository dependency."""
    from customer_analytics.app.features.identity.infrastructure.repositories.refresh_token_repository_impl import (  # noqa: E501
        RefreshTokenRepositoryImpl,
    )

    return RefreshTokenRepositoryImpl(db)


UnitOfWorkDep = Annotated[UserUnitOfWork, Depends(_get_user_unit_of_work)]
RefreshTokenRepoDep = Annotated[
    RefreshTokenRepositoryImpl, Depends(_get_refresh_token_repository)
]


def _to_uuid(value: str) -> uuid.UUID:
    """Convert string to UUID."""
    return uuid.UUID(value)


@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth2 login flow."""
    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    user_unit_of_work: UnitOfWorkDep,
    refresh_token_repo: RefreshTokenRepoDep,
):
    """Handle Google OAuth2 callback.

    Flow matches normal login:
    1. Verify Google token → find/create user
    2. Create access_token + refresh_token
    3. Save refresh_token hash to DB
    4. Set refresh_token as HTTP-only cookie
    5. Redirect to frontend with access_token in URL
    """
    try:
        # Verify state token for CSRF protection
        stored_state = request.session.get("oauth_state")
        received_state = request.query_params.get("state")

        if not stored_state or stored_state != received_state:
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Invalid OAuth state token",
            )

        # Get token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        google_user = token.get("userinfo")
        if not google_user:
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Failed to get user info from Google",
            )

        # Call use case → find/create user
        use_case = GoogleAuthUseCaseImpl(user_unit_of_work)
        user = await use_case((google_user,))

        # Create tokens (same as normal login)
        access_token = create_access_token(
            user_id=user.id_,
            role_code=user.role_code,
            permissions=user.permissions,
        )
        family_id = create_refresh_token_family()
        refresh_token = create_refresh_token(user_id=user.id_, family_id=family_id)

        # Save refresh token to DB (same as normal login)
        token_hash = hash_refresh_token(refresh_token)
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_TTL_DAYS
        )
        await refresh_token_repo.save(
            token_hash=token_hash,
            user_id=_to_uuid(user.id_),
            family_id=family_id,
            expires_at=expires_at,
            created_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        await user_unit_of_work.commit()

        # Redirect to frontend with access_token in URL
        # Frontend will store access_token in memory
        frontend_url = f"{settings.FRONTEND_URL.rstrip('/')}/auth/google/callback"
        redirect_response = RedirectResponse(
            url=f"{frontend_url}?access_token={access_token}"
        )
        _set_refresh_token_cookie(request, redirect_response, refresh_token)
        return redirect_response

    except AppException:
        raise
    except Exception as exc:
        raise AppException(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message="Google authentication failed",
        ) from exc
