from __future__ import annotations

import uuid
from uuid import uuid4

import pytest

from customer_analytics.app.features.identity.application.dto.user_command_model import (  # noqa: E501
    UserCreateModel,
    UserUpdateModel,
)
from customer_analytics.app.features.identity.application.dto.user_query_model import (
    UserListQueryModel,
)
from customer_analytics.app.features.identity.application.usecases.create_user import (
    CreateUserUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.get_users import (
    GetUsersUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.login_user import (
    LoginUserUseCaseImpl,
)
from customer_analytics.app.features.identity.application.usecases.update_user import (
    UpdateUserUseCaseImpl,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.domain.enums import UserStatus
from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
    verify_password,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


class FakeUserRepository:
    def __init__(self, user: UserEntity | None = None) -> None:
        self.user = user
        self.created: UserEntity | None = None
        self.updated: UserEntity | None = None
        self.role_id = uuid4()

    async def find_by_email(self, _email: str) -> UserEntity | None:
        return None

    async def find_by_id(self, _user_id: str) -> UserEntity | None:
        return self.user

    async def find_role_id_by_code(self, _role_code: str) -> uuid.UUID:
        return self.role_id

    async def create(self, entity: UserEntity) -> UserEntity:
        entity.id_ = str(uuid4())
        self.created = entity
        return entity

    async def update(self, entity: UserEntity) -> UserEntity:
        self.updated = entity
        return entity


class FakeUnitOfWork:
    def __init__(self, repository: FakeUserRepository) -> None:
        self.repository = repository
        self.committed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        pass


class FakeListUserRepository:
    def __init__(self, user: UserEntity) -> None:
        self.user = user
        self.find_all_params: dict[str, object] = {}
        self.count_params: dict[str, object] = {}

    async def find_all(self, **params: object) -> list[UserEntity]:
        self.find_all_params = params
        return [self.user]

    async def count_users(self, **params: object) -> int:
        self.count_params = params
        return 1

    async def get_users_permissions_batch(
        self, _user_ids: list[str]
    ) -> dict[str, list[str]]:
        return {str(self.user.id_): ["users:read"]}


class FakeListUnitOfWork:
    def __init__(self, repository: FakeListUserRepository) -> None:
        self.repository = repository


class FakeLoginUserRepository:
    def __init__(self, user: UserEntity) -> None:
        self.user = user
        self.updated: UserEntity | None = None

    async def find_by_email_with_permissions(
        self, _email: str
    ) -> tuple[UserEntity, list[str]]:
        return self.user, []

    async def update(self, user: UserEntity) -> UserEntity:
        self.updated = user
        return user


class FakeLoginUnitOfWork:
    def __init__(self, repository: FakeLoginUserRepository) -> None:
        self.repository = repository
        self.committed = False

    async def commit(self) -> None:
        self.committed = True


@pytest.mark.asyncio
async def test_create_user_hashes_password_and_assigns_role() -> None:
    repository = FakeUserRepository()
    unit_of_work = FakeUnitOfWork(repository)
    use_case = CreateUserUseCaseImpl(unit_of_work)

    result = await use_case(
        (
            UserCreateModel(
                email="new-user@example.com",
                password="StrongPassword123!",
                full_name="New User",
                role_code="ANALYST",
            ),
        )
    )

    assert repository.created is not None
    assert repository.created.password_hash != "StrongPassword123!"
    assert verify_password("StrongPassword123!", repository.created.password_hash)
    assert repository.created.role_id == str(repository.role_id)
    assert result.email == "new-user@example.com"
    assert unit_of_work.committed is True


def test_create_user_model_accepts_user_role() -> None:
    model = UserCreateModel(
        email="customer@example.com",
        password="Customer123!",
        full_name="Customer",
        role_code="USER",
    )

    assert model.role_code == "USER"


@pytest.mark.asyncio
async def test_update_user_cannot_disable_current_account() -> None:
    user_id = str(uuid4())
    repository = FakeUserRepository(
        UserEntity(
            id_=user_id,
            email="admin@example.com",
            password_hash="hash",
            full_name="Admin",
            role_code="ADMIN",
        )
    )
    use_case = UpdateUserUseCaseImpl(FakeUnitOfWork(repository))

    with pytest.raises(AppException) as error:
        await use_case(
            (
                user_id,
                UserUpdateModel(status=UserStatus.DISABLED),
                user_id,
            )
        )

    assert error.value.error_code is ErrorCode.CANNOT_DISABLE_SELF


@pytest.mark.asyncio
async def test_get_users_forwards_filters_and_sorting() -> None:
    user = UserEntity(
        id_=str(uuid4()),
        email="admin@example.com",
        password_hash="hash",
        full_name="Admin",
        role_code="ADMIN",
    )
    repository = FakeListUserRepository(user)
    use_case = GetUsersUseCaseImpl(FakeListUnitOfWork(repository))

    result = await use_case(
        UserListQueryModel(
            skip=10,
            limit=10,
            search="admin",
            role_code="ADMIN",
            status="ACTIVE",
            sort_by="full_name",
            sort_order="asc",
        )
    )

    assert repository.find_all_params == {
        "skip": 10,
        "limit": 10,
        "search": "admin",
        "role_code": "ADMIN",
        "status": "ACTIVE",
        "sort_by": "full_name",
        "sort_order": "asc",
    }
    assert repository.count_params == {
        "search": "admin",
        "role_code": "ADMIN",
        "status": "ACTIVE",
    }
    assert result.current == 2
    assert result.total == 1
    assert result.records[0].role_code == "ADMIN"


@pytest.mark.asyncio
async def test_user_role_can_login_without_backoffice_permissions() -> None:
    user = UserEntity(
        id_=str(uuid4()),
        email="customer@example.com",
        password_hash=hash_password("Customer123!"),
        full_name="Customer",
        role_code="USER",
    )
    repository = FakeLoginUserRepository(user)
    unit_of_work = FakeLoginUnitOfWork(repository)
    use_case = LoginUserUseCaseImpl(unit_of_work)

    result = await use_case(("customer@example.com", "Customer123!"))

    assert result.role_code == "USER"
    assert result.permissions == []
    assert result.last_login_at is not None
    assert repository.updated is not None
    assert unit_of_work.committed is True
