"""JWT authentication service — Access token creation and verification."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import uuid_utils

from customer_analytics.app.config import settings
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def create_access_token(
    user_id: uuid.UUID,
    role_code: str,
    permissions: list[str],
) -> str:
    """Create JWT access token.

    Args:
        user_id: User's UUID.
        role_code: User's role code (e.g., ADMIN, ANALYST).
        permissions: List of permission codes.

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(UTC)
    exp = now + timedelta(seconds=settings.jwt_access_token_ttl_seconds)

    payload = {
        "sub": str(user_id),
        "jti": str(uuid_utils.uuid7()),
        "type": "access",
        "role": role_code,
        "permissions": permissions,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "iss": settings.APP_NAME,
        "aud": f"{settings.APP_NAME}-web",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT access token.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        AppException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.APP_NAME,
            audience=f"{settings.APP_NAME}-web",
        )
    except jwt.ExpiredSignatureError:
        raise AppException(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message="Access token đã hết hạn.",
        ) from None
    except jwt.InvalidTokenError:
        raise AppException(
            error_code=ErrorCode.TOKEN_INVALID,
            message="Access token không hợp lệ.",
        ) from None

    # Verify token type
    if payload.get("type") != "access":
        raise AppException(
            error_code=ErrorCode.TOKEN_INVALID,
            message="Token type không hợp lệ.",
        )

    return payload


def create_refresh_token(user_id: uuid.UUID) -> str:
    """Create JWT refresh token.

    Args:
        user_id: User's UUID.

    Returns:
        Encoded JWT refresh token string.
    """
    now = datetime.now(UTC)
    exp = now + timedelta(days=settings.JWT_REFRESH_TOKEN_TTL_DAYS)

    payload = {
        "sub": str(user_id),
        "jti": str(uuid_utils.uuid7()),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "iss": settings.APP_NAME,
        "aud": f"{settings.APP_NAME}-web",
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT refresh token.

    Args:
        token: Encoded JWT refresh token string.

    Returns:
        Decoded payload dict.

    Raises:
        AppException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.APP_NAME,
            audience=f"{settings.APP_NAME}-web",
        )
    except jwt.ExpiredSignatureError:
        raise AppException(
            error_code=ErrorCode.INVALID_REFRESH_TOKEN,
            message="Refresh token đã hết hạn.",
        ) from None
    except jwt.InvalidTokenError:
        raise AppException(
            error_code=ErrorCode.INVALID_REFRESH_TOKEN,
            message="Refresh token không hợp lệ.",
        ) from None

    # Verify token type
    if payload.get("type") != "refresh":
        raise AppException(
            error_code=ErrorCode.INVALID_REFRESH_TOKEN,
            message="Token type không hợp lệ.",
        )

    return payload


def create_refresh_token_family() -> str:
    """Create a new refresh token family ID.

    Returns:
        UUID string for token family.
    """
    return str(uuid_utils.uuid7())


def hash_refresh_token(token: str) -> str:
    """Hash refresh token for secure storage.

    Args:
        token: Plain refresh token.

    Returns:
        SHA-256 hash of token.
    """
    import hashlib

    return hashlib.sha256(token.encode()).hexdigest()
