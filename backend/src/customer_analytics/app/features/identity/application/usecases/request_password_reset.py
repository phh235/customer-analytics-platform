"""Request-password-reset use case."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from customer_analytics.app.features.identity.application.password_reset_tokens import (
    generate_otp,
    hash_reset_secret,
)
from customer_analytics.app.features.identity.domain.entities.password_reset_challenge import (
    PasswordResetChallenge,
)
from customer_analytics.app.features.identity.domain.repositories.password_reset_repository import (
    PasswordResetRepository,
)
from customer_analytics.app.features.identity.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from customer_analytics.app.features.identity.infrastructure.email_sender import (
    EmailSender,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class RequestPasswordResetUseCaseImpl:
    """Create a reset challenge and deliver its OTP without exposing user existence."""

    def __init__(
        self,
        unit_of_work: UserUnitOfWork,
        reset_repository: PasswordResetRepository,
        email_sender: EmailSender,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.reset_repository = reset_repository
        self.email_sender = email_sender

    async def __call__(
        self,
        email: str,
        requested_ip: str | None,
        user_agent: str | None,
    ) -> bool:
        """Send an OTP when a matching local account exists."""
        if not getattr(self.email_sender, "is_configured", True):
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="Email service is temporarily unavailable.",
            )
        normalized_email = email.lower()
        now = datetime.now(UTC)
        user = await self.unit_of_work.repository.find_by_email(normalized_email)
        if user is None or user.id_ is None or user.auth_provider != "local":
            return False
        if await self.reset_repository.has_recent_request(
            normalized_email, now - timedelta(minutes=1)
        ):
            raise AppException(
                error_code=ErrorCode.TOO_MANY_REQUESTS,
                message="Please wait before requesting another OTP.",
            )

        otp = generate_otp()
        challenge = PasswordResetChallenge(
            id_=None,
            email=normalized_email,
            user_id=user.id_,
            otp_hash=hash_reset_secret(otp),
            expires_at=now + timedelta(minutes=10),
            requested_ip=requested_ip,
            user_agent=user_agent,
        )
        await self.reset_repository.invalidate_active(normalized_email)
        await self.reset_repository.create(challenge)
        try:
            await self.email_sender.send_password_reset_otp(
                recipient=normalized_email,
                full_name=user.full_name,
                otp=otp,
            )
        except RuntimeError as exc:
            raise AppException(
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                message="Email service is temporarily unavailable.",
            ) from exc
        return True
