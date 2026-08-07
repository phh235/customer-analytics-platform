"""Seed script — Create initial roles, permissions, and admin user."""

from __future__ import annotations

import asyncio

import uuid_utils
from sqlalchemy import select

from customer_analytics.app.features.identity.domain.enums import UserStatus
from customer_analytics.app.features.identity.infrastructure.models.user import (
    PermissionModel,
    RoleModel,
    UserModel,
)
from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
)
from customer_analytics.core.database import (
    AsyncSessionFactory,
    Base,
    engine,
)

# ── Permissions seed data ───────────────────────────────────

PERMISSIONS = [
    # Users
    ("users:create", "users", "create", "Tạo người dùng mới"),
    ("users:read", "users", "read", "Xem thông tin người dùng"),
    ("users:update", "users", "update", "Cập nhật thông tin người dùng"),
    ("users:delete", "users", "delete", "Xóa người dùng"),
    # Customers
    ("customers:read", "customers", "read", "Xem dữ liệu khách hàng"),
    # Analytics
    ("analytics:read", "analytics", "read", "Xem phân tích"),
]


async def seed_permissions() -> dict[str, PermissionModel]:
    """Seed permissions and return mapping."""
    permissions = {}
    async with AsyncSessionFactory() as session:
        for code, resource, action, description in PERMISSIONS:
            # Check if exists
            result = await session.execute(
                select(PermissionModel).where(PermissionModel.code == code)
            )
            existing = result.scalar_one_or_none()
            if existing:
                permissions[code] = existing
                continue

            perm = PermissionModel(
                id=uuid_utils.uuid7(),
                code=code,
                resource=resource,
                action=action,
                description=description,
            )
            session.add(perm)
            permissions[code] = perm

        await session.commit()
    return permissions


async def seed_roles(permissions: dict[str, PermissionModel]) -> dict[str, RoleModel]:
    """Seed roles and assign permissions."""
    roles = {}
    async with AsyncSessionFactory() as session:
        # ADMIN role — full access
        result = await session.execute(
            select(RoleModel).where(RoleModel.code == "ADMIN")
        )
        admin_role = result.scalar_one_or_none()
        if not admin_role:
            admin_role = RoleModel(
                id=uuid_utils.uuid7(),
                code="ADMIN",
                name="Administrator",
                description="Quản trị viên hệ thống",
            )
            session.add(admin_role)
        admin_role.permissions = list(permissions.values())
        roles["ADMIN"] = admin_role

        # CLIENT role — basic user
        result = await session.execute(
            select(RoleModel).where(RoleModel.code == "CLIENT")
        )
        client_role = result.scalar_one_or_none()
        if not client_role:
            client_role = RoleModel(
                id=uuid_utils.uuid7(),
                code="CLIENT",
                name="Client",
                description="Người dùng thông thường",
            )
            session.add(client_role)
        # CLIENT gets read-only permissions
        client_permissions = [
            p
            for code, p in permissions.items()
            if code in ["users:read", "customers:read", "analytics:read"]
        ]
        client_role.permissions = client_permissions
        roles["CLIENT"] = client_role

        await session.commit()
    return roles


async def seed_admin_user(roles: dict[str, RoleModel]) -> UserModel | None:
    """Create initial admin user if not exists."""
    async with AsyncSessionFactory() as session:
        # Check if admin exists
        result = await session.execute(
            select(UserModel).where(UserModel.email == "admin@example.com")
        )
        existing = result.scalar_one_or_none()
        if existing:
            return existing

        admin_role = roles.get("ADMIN")
        if not admin_role:
            raise ValueError("ADMIN role not found")

        user = UserModel(
            id=uuid_utils.uuid7(),
            email="admin@example.com",
            password_hash=hash_password("Admin123!"),
            full_name="System Admin",
            status=UserStatus.ACTIVE,
            role_id=admin_role.id,
        )
        session.add(user)
        await session.commit()

        print("✓ Created admin user: admin@example.com")
        return user


async def main() -> None:
    """Run seed script."""
    print("Seeding database...")

    # Create tables if not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed permissions
    permissions = await seed_permissions()
    print(f"✓ Seeded {len(permissions)} permissions")

    # Seed roles
    roles = await seed_roles(permissions)
    print(f"✓ Seeded {len(roles)} roles")

    # Seed admin user
    admin = await seed_admin_user(roles)
    if admin:
        print("✓ Admin user ready: admin@example.com")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
