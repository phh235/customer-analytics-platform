"""Login user use case — Business logic for user authentication."""

from __future__ import annotations

from abc import abstractmethod
from datetime import UTC, datetime

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
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

        # Tìm người dùng và tải quyền trong cùng một truy vấn.
        result = await self.unit_of_work.repository.find_by_email_with_permissions(
            email
        )
        if result is None:
            # Không tiết lộ email có tồn tại hay không.
            # Xác thực mật khẩu giả để thời gian xử lý tương đương.
            verify_password(password, hash_password("dummy"))
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Email hoặc mật khẩu không chính xác.",
            )

        user, permissions = result

        # Tài khoản chỉ liên kết với Google không được đăng nhập bằng mật khẩu.
        if user.auth_provider == "google":
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message=(
                    "Tài khoản này sử dụng Google để đăng nhập. "
                    "Vui lòng sử dụng nút 'Đăng nhập bằng Google'."
                ),
            )

        # Tài khoản đã bị vô hiệu hóa thì không được đăng nhập.
        if user.status == "DISABLED":
            raise AppException(
                error_code=ErrorCode.USER_DISABLED,
                message="Tài khoản đã bị vô hiệu hóa.",
            )

        # Nếu tài khoản bị khóa, chỉ cho đăng nhập sau khi hết thời gian khóa.
        if user.status == "LOCKED":
            if user.locked_until and user.locked_until > datetime.now(UTC):
                locked_until_str = user.locked_until.isoformat()
                msg = f"Tài khoản bị khóa tạm thời. Mở khóa sau: {locked_until_str}"
                raise AppException(
                    error_code=ErrorCode.USER_LOCKED,
                    message=msg,
                )
            # Hết thời gian khóa thì mở lại tài khoản.
            user = user.enable()

        # Kiểm tra mật khẩu và ghi nhận lần đăng nhập thất bại.
        if not verify_password(password, user.password_hash):
            updated_user = user.record_failed_login()
            await self.unit_of_work.repository.update(updated_user)
            # Lưu ngay để không mất thông tin phục vụ bảo mật.
            await self.unit_of_work.commit()
            # Luôn trả cùng một thông báo để không lộ thông tin tài khoản.
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Email hoặc mật khẩu không chính xác.",
            )

        # Ghi nhận đăng nhập thành công và cập nhật thời điểm đăng nhập.
        updated_user = user.record_successful_login()
        await self.unit_of_work.repository.update(updated_user)
        await self.unit_of_work.commit()
        # Gắn danh sách quyền đã tải từ truy vấn đăng nhập.
        updated_user.permissions = permissions

        return updated_user
