"""Reset-password use case."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from customer_analytics.app.features.identity.application.password_reset_tokens import (
    hash_reset_secret,
)
from customer_analytics.app.features.identity.domain.repositories.password_reset_repository import (
    PasswordResetRepository,
)
from customer_analytics.app.features.identity.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class ResetPasswordUseCaseImpl:
    """Set a new password from a verified, one-time reset token."""

    def __init__(
        self,
        unit_of_work: UserUnitOfWork,
        reset_repository: PasswordResetRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.reset_repository = reset_repository
        self.refresh_token_repository = refresh_token_repository

    async def __call__(self, reset_token: str, new_password: str) -> None:
        """Reset the password and invalidate all existing sessions."""
        challenge = await self.reset_repository.find_by_reset_token(
            hash_reset_secret(reset_token), datetime.now(UTC)
        )
        if challenge is None:
            raise AppException(
                error_code=ErrorCode.INVALID_PASSWORD_RESET_TOKEN,
                message="Reset token is invalid or expired.",
            )

        await self.unit_of_work.repository.update_password(
            challenge.user_id, hash_password(new_password)
        )
        await self.reset_repository.consume(challenge.id_, datetime.now(UTC))
        await self.refresh_token_repository.revoke_all_by_user(
            uuid.UUID(challenge.user_id)
        )
        await self.unit_of_work.commit()
