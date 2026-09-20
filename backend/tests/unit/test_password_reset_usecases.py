from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from customer_analytics.app.features.identity.application.password_reset_tokens import (
    hash_reset_secret,
)
from customer_analytics.app.features.identity.application.usecases.request_password_reset import (  # noqa: E501
    RequestPasswordResetUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.reset_password import (  # noqa: E501
    ResetPasswordUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.verify_password_reset import (  # noqa: E501
    VerifyPasswordResetUseCaseImpl,
)
from customer_analytics.app.features.identity.domain.entities.password_reset_challenge import (  # noqa: E501
    PasswordResetChallenge,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class FakeUserRepository:
    def __init__(self, user: UserEntity | None) -> None:
        self.user = user
        self.updated_password: tuple[str, str] | None = None

    async def find_by_email(self, _email: str) -> UserEntity | None:
        return self.user

    async def update_password(self, user_id: str, password_hash: str) -> None:
        self.updated_password = (user_id, password_hash)


class FakeUnitOfWork:
    def __init__(self, repository: FakeUserRepository) -> None:
        self.repository = repository
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


class FakeResetRepository:
    def __init__(self, challenge: PasswordResetChallenge | None = None) -> None:
        self.challenge = challenge
        self.invalidated_email: str | None = None
        self.created: PasswordResetChallenge | None = None
        self.incremented_id: str | None = None
        self.verified: dict[str, object] | None = None
        self.consumed_id: str | None = None

    async def invalidate_active(self, email: str) -> None:
        self.invalidated_email = email

    async def create(self, challenge: PasswordResetChallenge) -> None:
        self.created = challenge
        self.challenge = challenge

    async def find_active_by_email(
        self, _email: str, _now: datetime
    ) -> PasswordResetChallenge | None:
        return (
            self.challenge
            if self.challenge and not self.challenge.is_verified
            else None
        )

    async def increment_attempts(self, challenge_id: str) -> None:
        self.incremented_id = challenge_id
        assert self.challenge is not None
        self.challenge.attempt_count += 1

    async def has_recent_request(self, _email: str, _since: datetime) -> bool:
        return False

    async def mark_verified(
        self,
        challenge_id: str,
        reset_token_hash: str,
        reset_token_expires_at: datetime,
        verified_at: datetime,
    ) -> None:
        self.verified = {
            "challenge_id": challenge_id,
            "reset_token_hash": reset_token_hash,
            "reset_token_expires_at": reset_token_expires_at,
            "verified_at": verified_at,
        }
        assert self.challenge is not None
        self.challenge.verified_at = verified_at
        self.challenge.reset_token_hash = reset_token_hash

    async def find_by_reset_token(
        self, reset_token_hash: str, _now: datetime
    ) -> PasswordResetChallenge | None:
        if self.challenge and self.challenge.reset_token_hash == reset_token_hash:
            return self.challenge
        return None

    async def consume(self, challenge_id: str, _consumed_at: datetime) -> None:
        self.consumed_id = challenge_id


class FakeEmailSender:
    def __init__(self) -> None:
        self.sent: tuple[str, str, str] | None = None

    async def send_password_reset_otp(
        self, recipient: str, full_name: str, otp: str
    ) -> None:
        self.sent = (recipient, full_name, otp)


class FakeRefreshTokenRepository:
    def __init__(self) -> None:
        self.revoked_user_id = None

    async def revoke_all_by_user(self, user_id) -> int:
        self.revoked_user_id = user_id
        return 1


@pytest.mark.asyncio
async def test_request_password_reset_creates_challenge_and_sends_otp() -> None:
    user = UserEntity(
        id_=str(uuid4()),
        email="user@example.com",
        password_hash="hash",
        full_name="Test User",
        role_code="USER",
    )
    user_repository = FakeUserRepository(user)
    unit_of_work = FakeUnitOfWork(user_repository)
    reset_repository = FakeResetRepository()
    email_sender = FakeEmailSender()

    result = await RequestPasswordResetUseCaseImpl(
        unit_of_work, reset_repository, email_sender
    )("USER@EXAMPLE.COM", "127.0.0.1", "test-agent")

    assert result is True
    assert reset_repository.invalidated_email == "user@example.com"
    assert reset_repository.created is not None
    assert email_sender.sent is not None
    assert email_sender.sent[0] == "user@example.com"
    assert len(email_sender.sent[2]) == 6
    assert email_sender.sent[2].isdigit()
    assert reset_repository.created.otp_hash == hash_reset_secret(email_sender.sent[2])


@pytest.mark.asyncio
async def test_verify_password_reset_rejects_wrong_otp_and_records_attempt() -> None:
    challenge = PasswordResetChallenge(
        id_=str(uuid4()),
        email="user@example.com",
        user_id=str(uuid4()),
        otp_hash=hash_reset_secret("482913"),
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )
    repository = FakeResetRepository(challenge)

    token = await VerifyPasswordResetUseCaseImpl(repository)(
        "user@example.com", "000000"
    )

    assert token is None
    assert repository.incremented_id == challenge.id_
    assert challenge.attempt_count == 1


@pytest.mark.asyncio
async def test_reset_password_updates_hash_consumes_token_and_revokes_sessions() -> (
    None
):
    challenge = PasswordResetChallenge(
        id_=str(uuid4()),
        email="user@example.com",
        user_id=str(uuid4()),
        otp_hash=hash_reset_secret("482913"),
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
        verified_at=datetime.now(UTC),
        reset_token_hash=hash_reset_secret("reset-token"),
        reset_token_expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )
    user_repository = FakeUserRepository(None)
    unit_of_work = FakeUnitOfWork(user_repository)
    reset_repository = FakeResetRepository(challenge)
    refresh_repository = FakeRefreshTokenRepository()

    await ResetPasswordUseCaseImpl(unit_of_work, reset_repository, refresh_repository)(
        "reset-token", "NewStrongPassword123!"
    )

    assert user_repository.updated_password is not None
    assert user_repository.updated_password[0] == challenge.user_id
    assert user_repository.updated_password[1] != "NewStrongPassword123!"
    assert reset_repository.consumed_id == challenge.id_
    assert str(refresh_repository.revoked_user_id) == challenge.user_id
    assert unit_of_work.committed is True


@pytest.mark.asyncio
async def test_reset_password_rejects_invalid_token() -> None:
    unit_of_work = FakeUnitOfWork(FakeUserRepository(None))
    reset_repository = FakeResetRepository()
    refresh_repository = FakeRefreshTokenRepository()

    with pytest.raises(AppException) as error:
        await ResetPasswordUseCaseImpl(
            unit_of_work, reset_repository, refresh_repository
        )("invalid-token", "NewStrongPassword123!")

    assert error.value.error_code is ErrorCode.INVALID_PASSWORD_RESET_TOKEN
