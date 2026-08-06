"""Unit tests for identity domain exceptions — AppException with ErrorCode."""

from __future__ import annotations

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def test_app_exception_is_base_exception():
    """AppException should be base exception for business errors."""
    error = AppException(error_code=ErrorCode.USER_NOT_FOUND)
    assert isinstance(error, Exception)
    assert error.error_code == ErrorCode.USER_NOT_FOUND


def test_user_not_found_error_message():
    """AppException with USER_NOT_FOUND should have descriptive message."""
    error = AppException(
        error_code=ErrorCode.USER_NOT_FOUND,
        message="User 'user-123' not found",
    )
    assert "user-123" in str(error)
    assert error.status_code == 404


def test_invalid_credentials_error_message():
    """AppException with INVALID_CREDENTIALS should have generic message."""
    error = AppException(error_code=ErrorCode.INVALID_CREDENTIALS)
    assert "Email" in str(error) or "mật khẩu" in str(error)
    assert error.status_code == 401


def test_user_disabled_error_message():
    """AppException with USER_DISABLED should mention disabled status."""
    error = AppException(error_code=ErrorCode.USER_DISABLED)
    assert "disabled" in str(error).lower()
    assert error.status_code == 401


def test_user_locked_error_message():
    """AppException with USER_LOCKED should mention lock status."""
    error = AppException(
        error_code=ErrorCode.USER_LOCKED,
        message="Tài khoản bị khóa đến 2024-01-01",
    )
    assert "khóa" in str(error)
    assert error.status_code == 401


def test_email_already_exists_error_message():
    """AppException with EMAIL_EXISTS should include the email."""
    error = AppException(
        error_code=ErrorCode.EMAIL_EXISTS,
        message="Email 'test@example.com' đã tồn tại",
    )
    assert "test@example.com" in str(error)
    assert error.status_code == 409


def test_role_not_found_error_message():
    """AppException with ROLE_NOT_FOUND should include the role code."""
    error = AppException(
        error_code=ErrorCode.ROLE_NOT_FOUND,
        message="Role 'ADMIN' not found",
    )
    assert "ADMIN" in str(error)
    assert error.status_code == 404


def test_insufficient_permissions_error_message():
    """AppException with PERMISSION_DENIED should include the permission."""
    error = AppException(
        error_code=ErrorCode.PERMISSION_DENIED,
        message="Không có quyền 'users:delete'",
    )
    assert "users:delete" in str(error)
    assert error.status_code == 403


def test_refresh_token_error_message():
    """AppException with INVALID_REFRESH_TOKEN should have default message."""
    error = AppException(error_code=ErrorCode.INVALID_REFRESH_TOKEN)
    assert "refresh token" in str(error).lower() or "invalid" in str(error).lower()
    assert error.status_code == 401


def test_refresh_token_reuse_error_message():
    """AppException with INVALID_REFRESH_TOKEN reuse should mention reuse."""
    error = AppException(
        error_code=ErrorCode.INVALID_REFRESH_TOKEN,
        message="Phát hiện sử dụng lại refresh token. Vui lòng đăng nhập lại.",
    )
    assert "sử dụng lại" in str(error)


def test_cannot_disable_self_error_message():
    """AppException with CANNOT_DISABLE_SELF should mention self-disable."""
    error = AppException(error_code=ErrorCode.CANNOT_DISABLE_SELF)
    assert "own account" in str(error).lower() or "disable" in str(error).lower()
    assert error.status_code == 400


def test_app_exception_default_message():
    """AppException should use ErrorCode.message as default message."""
    error = AppException(error_code=ErrorCode.INVALID_CREDENTIALS)
    assert error.message == ErrorCode.INVALID_CREDENTIALS.message


def test_app_exception_custom_message():
    """AppException should accept custom message."""
    error = AppException(
        error_code=ErrorCode.INVALID_CREDENTIALS,
        message="Custom error message",
    )
    assert error.message == "Custom error message"
