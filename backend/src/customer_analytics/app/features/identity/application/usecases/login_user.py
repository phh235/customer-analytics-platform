"""Login user use case — Business logic for user authentication."""

from __future__ import annotations

from abc import abstractmethod
from datetime import UTC, datetime

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (  # noqa: E501
    UserUnitOfWork,
)
from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
    verify_password,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class LoginUserUseCase(BaseUseCase[tuple[str, str], UserEntity]):
    """Login user use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[str, str]) -> UserEntity:
        raise NotImplementedError()


class LoginUserUseCaseImpl(LoginUserUseCase):
    """Login user use case implementation."""

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[str, str]) -> UserEntity:
        email, password = args

        # 1. Find user by email with permissions (single query)
        result = await self.unit_of_work.repository.find_by_email_with_permissions(
            email
        )
        if result is None:
            # Generic message to not leak email existence
            # Run dummy verify to keep timing constant
            verify_password(password, hash_password("dummy"))
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Email hoặc mật khẩu không chính xác.",
            )

        user, permissions = result

        # 2. Check if account is disabled
        if user.status == "DISABLED":
            raise AppException(
                error_code=ErrorCode.USER_DISABLED,
                message="Tài khoản đã bị vô hiệu hóa.",
            )

        # 3. Check if account is locked
        if user.status == "LOCKED":
            if user.locked_until and user.locked_until > datetime.now(UTC):
                locked_until_str = user.locked_until.isoformat()
                msg = f"Tài khoản bị khóa tạm thời. Mở khóa sau: {locked_until_str}"
                raise AppException(
                    error_code=ErrorCode.USER_LOCKED,
                    message=msg,
                )
            # Lock expired, unlock the account
            user = user.enable()

        # 4. Verify password
        if not verify_password(password, user.password_hash):
            # Record failed attempt
            updated_user = user.record_failed_login()
            await self.unit_of_work.repository.update(updated_user)
            # Commit immediately for failed login (security audit)
            await self.unit_of_work.commit()
            # Generic message to not leak info
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Email hoặc mật khẩu không chính xác.",
            )

        # 5. Record successful login (don't commit here - caller will commit)
        updated_user = user.record_successful_login()
        await self.unit_of_work.repository.update(updated_user)

        # 6. Attach permissions (already loaded from query)
        updated_user.permissions = permissions

        return updated_user
