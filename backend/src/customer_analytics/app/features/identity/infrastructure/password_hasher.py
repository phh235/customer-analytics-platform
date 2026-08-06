"""Password hashing service — Argon2id via pwdlib."""

from __future__ import annotations

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# Initialize with Argon2id hasher
_password_hasher = PasswordHash([Argon2Hasher()])


def hash_password(password: str) -> str:
    """Hash password using Argon2id.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string.
    """
    return _password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to verify against.

    Returns:
        True if password matches hash.
    """
    return _password_hasher.verify(plain_password, hashed_password)


def needs_rehash(hashed_password: str) -> bool:
    """Check if password needs rehashing (e.g., after config change).

    Args:
        hashed_password: Hashed password to check.

    Returns:
        True if rehashing is needed.
    """
    # pwdlib's verify_and_update returns (verified, new_hash)
    # If new_hash is not None, rehashing is recommended
    _, new_hash = _password_hasher.verify_and_update("dummy_password", hashed_password)
    return new_hash is not None
