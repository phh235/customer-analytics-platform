from __future__ import annotations

from uuid import uuid4

import pytest
from starlette.requests import Request
from starlette.responses import Response

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.presentation import security
from customer_analytics.app.features.identity.presentation.routes import auth_routes
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class FakeRefreshRepository:
    def __init__(self, user: UserEntity, permissions: list[str]) -> None:
        self.user = user
        self.permissions = permissions

    async def find_by_id(self, _user_id: str) -> UserEntity:
        return self.user

    async def get_user_permissions(self, _user_id: str) -> list[str]:
        return self.permissions


class FakeRefreshTokenRepository:
    async def find_by_token_hash(self, _token_hash: str) -> None:
        return None

    async def revoke_by_token_hash(self, _token_hash: str) -> None:
        return None

    async def save(self, **_kwargs: object) -> None:
        return None


class FakeRefreshUnitOfWork:
    def __init__(self, repository: FakeRefreshRepository) -> None:
        self.repository = repository

    async def commit(self) -> None:
        return None

@pytest.mark.asyncio
async def test_refresh_access_token_includes_current_permissions(monkeypatch) -> None:
    user_id = str(uuid4())
    permissions = ["users:read", "users:create"]
    user = UserEntity(
        id_=user_id,
        email="admin@example.com",
        password_hash="hash",
        full_name="Admin",
        role_code="ADMIN",
    )
    unit_of_work = FakeRefreshUnitOfWork(FakeRefreshRepository(user, permissions))
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        auth_routes,
        "decode_refresh_token",
        lambda _token: {"sub": user_id},
    )

    def fake_create_access_token(**kwargs: object) -> str:
        captured.update(kwargs)
        return "access-token"

    monkeypatch.setattr(auth_routes, "create_access_token", fake_create_access_token)
    monkeypatch.setattr(
        auth_routes,
        "create_refresh_token",
        lambda **_kwargs: "refresh-token",
    )

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/auth/refresh",
            "headers": [(b"cookie", b"refresh_token=refresh-token")],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
        }
    )
    response = Response()

    result = await auth_routes.refresh_token(
        request,
        response,
        unit_of_work,
        FakeRefreshTokenRepository(),
    )

    assert result.access_token == "access-token"
    assert captured["permissions"] == permissions



@pytest.mark.asyncio
async def test_current_user_resolves_permissions_from_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = UserEntity(
        id_=str(uuid4()),
        email="user@example.com",
        password_hash="hash",
        full_name="User",
        role_code="USER",
    )
    repository = FakeRefreshRepository(user, ["analytics:read"])
    monkeypatch.setattr(
        security,
        "decode_access_token",
        lambda _token: {"sub": user.id_},
    )

    result = await security.get_current_user("stale-token", repository)  # type: ignore[arg-type]

    assert result.role_code == "USER"


@pytest.mark.asyncio
async def test_current_user_rejects_disabled_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = UserEntity(
        id_=str(uuid4()),
        email="disabled@example.com",
        password_hash="hash",
        full_name="Disabled",
        role_code="USER",
        status="DISABLED",
    )
    repository = FakeRefreshRepository(user, [])
    monkeypatch.setattr(
        security,
        "decode_access_token",
        lambda _token: {"sub": user.id_},
    )

    with pytest.raises(AppException) as error:
        await security.get_current_user("token", repository)  # type: ignore[arg-type]

    assert error.value.error_code is ErrorCode.USER_DISABLED
    assert error.value.status_code == 401