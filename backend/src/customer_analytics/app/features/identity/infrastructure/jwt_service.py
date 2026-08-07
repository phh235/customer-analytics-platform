"""JWT authentication service — Access token creation and verification."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import uuid_utils

from customer_analytics.app.config import settings
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def _create_token(
    payload: dict[str, Any],
    secret_key: str,
    algorithm: str,
) -> str:
    """Create JWT token with given payload."""
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def _decode_token(
    token: str,
    secret_key: str,
    algorithm: str,
    expected_type: str,
    app_name: str,
) -> dict[str, Any]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            issuer=app_name,
            audience=f"{app_name}-web",
        )
    except jwt.ExpiredSignatureError:
        error_code = (
            ErrorCode.TOKEN_EXPIRED
            if expected_type == "access"
            else ErrorCode.INVALID_REFRESH_TOKEN
        )
        raise AppException(
            error_code=error_code,
            message=f"{expected_type.capitalize()} token đã hết hạn.",
        ) from None
    except jwt.InvalidTokenError:
        error_code = (
            ErrorCode.TOKEN_INVALID
            if expected_type == "access"
            else ErrorCode.INVALID_REFRESH_TOKEN
        )
        raise AppException(
            error_code=error_code,
            message=f"{expected_type.capitalize()} token không hợp lệ.",
        ) from None

    # Verify token type
    if payload.get("type") != expected_type:
        error_code = (
            ErrorCode.TOKEN_INVALID
            if expected_type == "access"
            else ErrorCode.INVALID_REFRESH_TOKEN
        )
        raise AppException(
            error_code=error_code,
            message="Token type không hợp lệ.",
        )

    return payload


def create_access_token(
    user_id: uuid.UUID,
    role_code: str,
    permissions: list[str],
) -> str:
    """Create JWT access token.

    Args:
        user_id: User's UUID.
        role_code: User's role code (e.g., ADMIN, CLIENT).
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

    return _create_token(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT access token.

    Args:
        token: Encoded JWT string.

    Returns:
        Decoded payload dict.

    Raises:
        AppException: If token is invalid or expired.
    """
    return _decode_token(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
        expected_type="access",
        app_name=settings.APP_NAME,
    )


def create_refresh_token(user_id: uuid.UUID, family_id: str | None = None) -> str:
    """Create JWT refresh token.

    Args:
        user_id: User's UUID.
        family_id: Token family ID for rotation tracking (optional).

    Returns:
        Encoded JWT refresh token string.
    """
    now = datetime.now(UTC)
    exp = now + timedelta(days=settings.JWT_REFRESH_TOKEN_TTL_DAYS)

    payload = {
        "sub": str(user_id),
        "jti": str(uuid_utils.uuid7()),
        "type": "refresh",
        "family_id": family_id or str(uuid_utils.uuid7()),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "iss": settings.APP_NAME,
        "aud": f"{settings.APP_NAME}-web",
    }

    return _create_token(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT refresh token.

    Args:
        token: Encoded JWT refresh token string.

    Returns:
        Decoded payload dict.

    Raises:
        AppException: If token is invalid or expired.
    """
    return _decode_token(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
        expected_type="refresh",
        app_name=settings.APP_NAME,
    )


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
    return hashlib.sha256(token.encode()).hexdigest()
