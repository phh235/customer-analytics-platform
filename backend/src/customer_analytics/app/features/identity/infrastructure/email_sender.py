"""Email delivery abstraction and SMTP implementation."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from typing import Protocol

from customer_analytics.app.config import Settings


class EmailSender(Protocol):
    """Application-facing email delivery contract."""

    async def send_password_reset_otp(
        self, recipient: str, full_name: str, otp: str
    ) -> None:
        """Send a password reset OTP email."""
        ...


class SmtpEmailSender:
    """Send transactional email through a configured SMTP server."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def is_configured(self) -> bool:
        """Return whether enough SMTP configuration is available."""
        return bool(
            self._settings.SMTP_HOST
            and self._settings.SMTP_USERNAME
            and self._settings.SMTP_PASSWORD
        )

    async def send_password_reset_otp(
        self, recipient: str, full_name: str, otp: str
    ) -> None:
        """Send OTP without blocking the async event loop."""
        if not self.is_configured:
            raise RuntimeError("SMTP email service is not configured")
        try:
            await asyncio.to_thread(
                self._send_password_reset_otp_sync,
                recipient,
                full_name,
                otp,
            )
        except (OSError, smtplib.SMTPException) as exc:
            raise RuntimeError("SMTP email delivery failed") from exc

    def _send_password_reset_otp_sync(
        self, recipient: str, full_name: str, otp: str
    ) -> None:
        settings = self._settings
        host = settings.SMTP_HOST
        username = settings.SMTP_USERNAME
        password = settings.SMTP_PASSWORD
        from_email = settings.SMTP_FROM_EMAIL or username
        if not host or not username or not password or not from_email:
            raise RuntimeError("SMTP email service is not configured")

        message = EmailMessage()
        message["Subject"] = "Mã OTP đặt lại mật khẩu Customer Analytics"
        message["From"] = f"{settings.SMTP_FROM_NAME} <{from_email}>"
        message["To"] = recipient
        message.set_content(
            "Xin chào "
            f"{full_name},\n\n"
            "Mã OTP để đặt lại mật khẩu của bạn là:\n\n"
            f"{otp}\n\n"
            "Mã có hiệu lực trong 10 phút và chỉ được sử dụng một lần.\n"
            "Nếu bạn không thực hiện yêu cầu này, hãy bỏ qua email.\n"
            "Không chia sẻ mã OTP với bất kỳ ai."
        )

        with smtplib.SMTP(host, settings.SMTP_PORT, timeout=15) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)
