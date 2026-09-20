"""Helpers for generating and hashing password reset secrets."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from customer_analytics.app.config import settings


def generate_otp() -> str:
    """Generate a cryptographically secure six-digit OTP."""
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_reset_token() -> str:
    """Generate an opaque, high-entropy reset token."""
    return secrets.token_urlsafe(32)


def hash_reset_secret(value: str) -> str:
    """Hash an OTP/token with the application secret as a pepper."""
    return hmac.new(
        settings.JWT_SECRET_KEY.encode(),
        value.encode(),
        hashlib.sha256,
    ).hexdigest()
