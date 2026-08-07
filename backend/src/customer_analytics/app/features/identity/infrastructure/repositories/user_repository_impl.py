"""User repository implementation — SQLAlchemy implementation."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.identity.domain.repositories.user_repository import (  # noqa: E501
    UserRepository,
)
from customer_analytics.app.features.identity.infrastructure.models.user import (
    PermissionModel,
    RoleModel,
    RolePermissionModel,
    UserModel,
)


class UserRepositoryImpl(UserRepository):
    """User repository using SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _to_entity(self, model: UserModel) -> UserEntity:
        """Convert database model to domain entity."""
        # Eagerly load role relationship if not already loaded
        if "role" not in model.__dict__:
            await self._session.refresh(model, ["role"])

        return UserEntity(
            id_=str(model.id),
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            status=model.status.value
            if hasattr(model.status, "value")
            else model.status,
            role_code=model.role.code if model.role else "CLIENT",
            is_active=model.status.value == "ACTIVE"
            if hasattr(model.status, "value")
            else model.status == "ACTIVE",
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login_at=model.last_login_at,
            failed_login_count=model.failed_login_count,
            locked_until=model.locked_until,
        )

    def _to_model(self, entity: UserEntity) -> UserModel:
        """Convert domain entity to database model."""
        from customer_analytics.app.features.identity.domain.enums import UserStatus

        status = (
            UserStatus(entity.status)
            if entity.status in [s.value for s in UserStatus]
            else UserStatus.ACTIVE
        )

        return UserModel(
            id=entity.id_,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            status=status,
            failed_login_count=entity.failed_login_count,
            locked_until=entity.locked_until,
            last_login_at=entity.last_login_at,
        )

    async def create(self, entity: UserEntity) -> UserEntity:
        """Create a new user."""
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        # Refresh model to load server-generated values (id, created_at, etc.)
        await self._session.refresh(model)
        return await self._to_entity(model)

    async def find_by_id(self, id_: str) -> UserEntity | None:
        """Find a user by ID."""

        result = await self._session.execute(
            select(UserModel).where(UserModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model else None

    async def find_by_email(self, email: str) -> UserEntity | None:
        """Find a user by email."""
        result = await self._session.execute(
            select(UserModel).where(func.lower(UserModel.email) == email.lower())
        )
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model else None

    async def find_by_email_with_permissions(
        self, email: str
    ) -> tuple[UserEntity, list[str]] | None:
        """Find user by email with role + permissions in single query.

        Optimised for login flow — avoids N+1 by joining all needed data.
        Returns (UserEntity, permissions) or None.
        """
        # Single query: user + role + permissions
        stmt = (
            select(
                UserModel,
                PermissionModel.code.label("permission_code"),
            )
            .options(selectinload(UserModel.role))
            .join(
                RolePermissionModel,
                UserModel.role_id == RolePermissionModel.role_id,
            )
            .join(
                PermissionModel,
                RolePermissionModel.permission_id == PermissionModel.id,
            )
            .where(func.lower(UserModel.email) == email.lower())
            .distinct()
        )
        result = await self._session.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # First row has the user model (with role loaded via selectinload)
        model = rows[0][0]
        permissions = [row.permission_code for row in rows]

        entity = await self._to_entity(model)
        return entity, permissions

    async def find_role_id_by_code(self, role_code: str) -> uuid.UUID | None:
        """Find a role ID by its stable role code."""
        result = await self._session.execute(
            select(RoleModel.id).where(RoleModel.code == role_code)
        )
        row = result.scalar_one_or_none()
        return row

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        role_code: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[UserEntity]:
        """Find all users with pagination, filters, and deterministic ordering.

        Uses selectinload to eagerly load role relationship in a single query.
        """
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.role))
        )

        # Search filter
        if search:
            stmt = stmt.where(
                func.lower(UserModel.email).contains(search.lower())
                | func.lower(UserModel.full_name).contains(search.lower())
            )

        # Role filter
        if role_code:
            stmt = stmt.join(RoleModel).where(RoleModel.code == role_code)

        # Status filter
        if status:
            from customer_analytics.app.features.identity.domain.enums import UserStatus

            try:
                status_enum = UserStatus(status)
                stmt = stmt.where(UserModel.status == status_enum)
            except ValueError:
                pass

        # Sorting
        sort_column = getattr(UserModel, sort_by, UserModel.created_at)
        if sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._to_entity(m) for m in models]

    async def count_users(
        self,
        search: str | None = None,
        role_code: str | None = None,
        status: str | None = None,
    ) -> int:
        """Count users matching the supplied filters."""
        stmt = select(func.count()).select_from(UserModel)

        if search:
            stmt = stmt.where(
                func.lower(UserModel.email).contains(search.lower())
                | func.lower(UserModel.full_name).contains(search.lower())
            )

        if role_code:
            stmt = stmt.join(RoleModel).where(RoleModel.code == role_code)

        if status:
            from customer_analytics.app.features.identity.domain.enums import UserStatus

            try:
                status_enum = UserStatus(status)
                stmt = stmt.where(UserModel.status == status_enum)
            except ValueError:
                pass

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_user_permissions(self, user_id: str) -> list[str]:
        """Get list of permission codes for a user.

        Query: user → role → role_permissions → permissions

        Args:
            user_id: User's UUID.

        Returns:
            List of permission codes (e.g., ["users:create", "analytics:read"]).
        """
        stmt = (
            select(PermissionModel.code)
            .join(
                RolePermissionModel,
                RolePermissionModel.permission_id == PermissionModel.id,
            )
            .join(UserModel, UserModel.role_id == RolePermissionModel.role_id)
            .where(UserModel.id == user_id)
            .distinct()
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_users_permissions_batch(
        self, user_ids: list[str]
    ) -> dict[str, list[str]]:
        """Get permissions for multiple users in a single query.

        Returns:
            Dict mapping user_id → list of permission codes.
        """
        if not user_ids:
            return {}

        # Start from UserModel, join to role_permissions, then to permissions
        stmt = (
            select(
                UserModel.id.label("user_id"),
                PermissionModel.code.label("permission_code"),
            )
            .join(
                RolePermissionModel,
                UserModel.role_id == RolePermissionModel.role_id,
            )
            .join(
                PermissionModel,
                RolePermissionModel.permission_id == PermissionModel.id,
            )
            .where(UserModel.id.in_(user_ids))
            .distinct()
        )
        result = await self._session.execute(stmt)

        permissions_map: dict[str, list[str]] = {}
        for row in result:
            user_id = str(row.user_id)
            if user_id not in permissions_map:
                permissions_map[user_id] = []
            permissions_map[user_id].append(row.permission_code)

        return permissions_map

    async def update(self, entity: UserEntity) -> UserEntity:
        """Update an existing user."""
        if entity.id_ is None:
            raise ValueError("Cannot update user without ID")

        result = await self._session.execute(
            select(UserModel).where(UserModel.id == entity.id_)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"User with ID {entity.id_} not found")

        # Update model fields
        model.email = entity.email
        model.full_name = entity.full_name
        model.failed_login_count = entity.failed_login_count
        model.locked_until = entity.locked_until
        model.last_login_at = entity.last_login_at

        # Update status
        from customer_analytics.app.features.identity.domain.enums import UserStatus

        model.status = (
            UserStatus(entity.status)
            if entity.status in [s.value for s in UserStatus]
            else UserStatus.ACTIVE
        )

        await self._session.flush()
        # Refresh model to load server-generated values (updated_at, etc.)
        await self._session.refresh(model)
        return await self._to_entity(model)

    async def delete(self, id_: str) -> None:
        """Delete a user (hard delete — use with caution)."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == id_)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
