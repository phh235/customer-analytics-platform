"""Google auth use case — Handle Google OAuth2 authentication."""

from __future__ import annotations

from abc import abstractmethod

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase


class GoogleAuthUseCase(BaseUseCase[tuple[dict], UserEntity]):
    """Google auth use case interface."""

    unit_of_work: UserUnitOfWork

    @abstractmethod
    async def __call__(self, args: tuple[dict]) -> UserEntity:
        raise NotImplementedError()


class GoogleAuthUseCaseImpl(GoogleAuthUseCase):
    """Google auth use case implementation.

    Flow:
    1. Check if user exists by google_id
    2. Find by email (link existing account)
    3. If not, create new user with role USER
    4. Return user entity (tokens created in route layer)
    """

    def __init__(self, unit_of_work: UserUnitOfWork):
        self.unit_of_work = unit_of_work

    async def __call__(self, args: tuple[dict]) -> UserEntity:
        (google_user,) = args

        google_id = google_user.get("sub")
        email = google_user.get("email")
        full_name = google_user.get("name", "")
        email_verified = google_user.get("email_verified", False)

        # Kiểm tra các trường bắt buộc và email đã được Google xác thực.
        if not google_id:
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Invalid Google token: missing sub",
            )

        if not email:
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Invalid Google token: missing email",
            )

        if not email_verified:
            raise AppException(
                error_code=ErrorCode.INVALID_CREDENTIALS,
                message="Google email not verified. Please verify your email first.",
            )

        # Nếu đã có tài khoản Google thì cập nhật lần đăng nhập cuối.
        user = await self.unit_of_work.repository.find_by_google_id(google_id)
        if user:
            user = user.record_successful_login()
            await self.unit_of_work.repository.update(user)
            return user

        # Nếu email đã tồn tại, liên kết tài khoản đó với Google.
        user = await self.unit_of_work.repository.find_by_email(email)
        if user:
            user = user.update(
                google_id=google_id,
                auth_provider="google",
            )
            user = user.record_successful_login()
            await self.unit_of_work.repository.update(user)
            return user

        # Nếu chưa có tài khoản, tạo tài khoản USER mới.
        from customer_analytics.app.features.identity.infrastructure.password_hasher import (
            hash_password,
        )

        # Người dùng đăng ký qua Google luôn nhận role USER mặc định.
        role_id = await self.unit_of_work.repository.find_role_id_by_code("USER")
        if role_id is None:
            raise AppException(
                error_code=ErrorCode.ROLE_NOT_FOUND,
                message="Role 'USER' not found.",
            )

        user = UserEntity(
            id_=None,
            email=email.lower(),
            password_hash=hash_password("oauth_placeholder"),
            full_name=full_name,
            role_code="USER",
            role_id=str(role_id),
            google_id=google_id,
            auth_provider="google",
        )

        try:
            created_user = await self.unit_of_work.repository.create(user)
        except Exception:
            await self.unit_of_work.rollback()
            raise

        return created_user
