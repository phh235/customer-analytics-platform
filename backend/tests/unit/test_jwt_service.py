"""Unit tests for JWT authentication service."""

from __future__ import annotations

import uuid

import jwt
import pytest

from customer_analytics.app.features.identity.infrastructure.jwt_service import (
    create_access_token,
    create_refresh_token_family,
    decode_access_token,
    hash_refresh_token,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def test_create_access_token_returns_string():
    """Create access token should return a valid JWT string."""
    user_id = uuid.uuid4()
    token = create_access_token(
        user_id=user_id,
        role_code="ADMIN",
        permissions=["users:read", "users:create"],
    )
    assert isinstance(token, str)
    assert len(token) > 0
    # JWT has 3 parts separated by dots
    assert token.count(".") == 2


def test_decode_access_token_valid():
    """Decode valid access token should return payload."""
    user_id = uuid.uuid4()
    permissions = ["users:read", "analytics:read"]
    token = create_access_token(
        user_id=user_id,
        role_code="ANALYST",
        permissions=permissions,
    )
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ANALYST"
    assert payload["permissions"] == permissions
    assert payload["type"] == "access"


def test_decode_access_token_invalid():
    """Decode invalid token should raise AppException."""
    with pytest.raises(AppException) as exc_info:
        decode_access_token("invalid.token.here")
    assert exc_info.value.error_code == ErrorCode.TOKEN_INVALID


def test_decode_access_token_wrong_type():
    """Decode token with wrong type should raise AppException."""
    user_id = uuid.uuid4()
    payload = {
        "sub": str(user_id),
        "type": "refresh",  # Wrong type
        "role": "ADMIN",
        "permissions": [],
    }
    token = jwt.encode(
        payload,
        "change_me",  # matches settings.JWT_SECRET_KEY
        algorithm="HS256",
    )
    with pytest.raises(AppException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.error_code == ErrorCode.TOKEN_INVALID


def test_create_refresh_token_family_returns_uuid():
    """Create refresh token family should return a UUID string."""
    family_id = create_refresh_token_family()
    assert isinstance(family_id, str)
    # Should be valid UUID
    uuid.UUID(family_id)


def test_hash_refresh_token_returns_hash():
    """Hash refresh token should return a SHA-256 hash."""
    token = "test_refresh_token_123"
    hashed = hash_refresh_token(token)
    assert isinstance(hashed, str)
    assert len(hashed) == 64  # SHA-256 hex digest length
    assert hashed != token


def test_hash_refresh_token_deterministic():
    """Hashing same token should produce same hash."""
    token = "same_token_123"
    hash1 = hash_refresh_token(token)
    hash2 = hash_refresh_token(token)
    assert hash1 == hash2
