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
    ("customers:export", "customers", "export", "Xuất dữ liệu khách hàng"),
    # Analytics
    ("analytics:read", "analytics", "read", "Xem phân tích"),
    ("analytics:predict", "analytics", "predict", "Chạy dự đoán"),
]


async def seed_permissions() -> dict[str, PermissionModel]:
    """Seed permissions and return mapping."""
    permissions: dict[str, PermissionModel] = {}
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
    roles: dict[str, RoleModel] = {}
    async with AsyncSessionFactory() as session:
        # Re-load permission models in this session. The objects returned by
        # seed_permissions belong to a different, already-closed session.
        permission_result = await session.execute(
            select(PermissionModel).where(PermissionModel.code.in_(permissions.keys()))
        )
        permission_models = {
            permission.code: permission
            for permission in permission_result.scalars().all()
        }

        # ADMIN role
        admin_result = await session.execute(
            select(RoleModel).where(RoleModel.code == "ADMIN")
        )
        admin_role = admin_result.scalar_one_or_none()
        if not admin_role:
            admin_role = RoleModel(
                id=uuid_utils.uuid7(),
                code="ADMIN",
                name="Administrator",
                description="Quản trị viên hệ thống",
            )
            session.add(admin_role)
        admin_role.permissions = list(permission_models.values())
        roles["ADMIN"] = admin_role

        # ANALYST role
        analyst_result = await session.execute(
            select(RoleModel).where(RoleModel.code == "ANALYST")
        )
        analyst_role = analyst_result.scalar_one_or_none()
        if not analyst_role:
            analyst_role = RoleModel(
                id=uuid_utils.uuid7(),
                code="ANALYST",
                name="Data Analyst",
                description="Phân tích dữ liệu",
            )
            session.add(analyst_role)
        # ANALYST gets read-only + analytics permissions
        analyst_permissions = [
            permission_models[code]
            for code in [
                "customers:read",
                "customers:export",
                "analytics:read",
                "analytics:predict",
            ]
            if code in permission_models
        ]
        analyst_role.permissions = analyst_permissions
        roles["ANALYST"] = analyst_role

        # USER role. It intentionally starts without back-office permissions.
        user_result = await session.execute(
            select(RoleModel).where(RoleModel.code == "USER")
        )
        user_role = user_result.scalar_one_or_none()
        if not user_role:
            user_role = RoleModel(
                id=uuid_utils.uuid7(),
                code="USER",
                name="Customer",
                description="Người dùng ứng dụng",
            )
            session.add(user_role)
        roles["USER"] = user_role

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
