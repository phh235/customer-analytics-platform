"""Unit tests for password hashing service."""

from __future__ import annotations

from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
    needs_rehash,
    verify_password,
)


def test_hash_password_returns_hash():
    """Hash password should return a non-empty string."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    assert hashed
    assert hashed != password
    assert "$argon2" in hashed


def test_verify_password_correct():
    """Verify password with correct password should return True."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Verify password with incorrect password should return False."""
    password = "TestPassword123!"
    wrong_password = "WrongPassword456!"
    hashed = hash_password(password)
    assert verify_password(wrong_password, hashed) is False


def test_needs_rehash_returns_bool():
    """Needs rehash should return a boolean."""
    password = "TestPassword123!"
    hashed = hash_password(password)
    result = needs_rehash(hashed)
    assert isinstance(result, bool)
