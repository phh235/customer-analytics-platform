"""Seed script — Create initial roles, permissions, and admin user."""

from __future__ import annotations

import asyncio

import uuid_utils
from sqlalchemy import select, update

from customer_analytics.app.features.analytics.infrastructure.models.analytics_history import (  # noqa: E501, F401
    PurchasePredictionModel,
    SegmentHistoryModel,
)
from customer_analytics.app.features.analytics.infrastructure.models.model_registry import (  # noqa: E501, F401
    ModelRegistryModel,
)
from customer_analytics.app.features.customer.infrastructure.models.customer import (  # noqa: F401
    CustomerModel,
)
from customer_analytics.app.features.identity.domain.enums import UserStatus
from customer_analytics.app.features.identity.infrastructure.models.user import (
    PermissionModel,
    RoleModel,
    TeamModel,
    UserModel,
)
from customer_analytics.app.features.identity.infrastructure.password_hasher import (
    hash_password,
)
from customer_analytics.app.features.import_data.infrastructure.models.import_job import (  # noqa: E501, F401
    ImportJobModel,
)
from customer_analytics.app.features.order.infrastructure.models.order import (  # noqa: F401
    OrderItemModel,
    OrderModel,
)
from customer_analytics.app.features.product.infrastructure.models.product import (  # noqa: F401
    ProductModel,
)
from customer_analytics.app.features.reference_data.infrastructure.models import (  # noqa: F401
    EmployeeModel,
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
    ("customers:create", "customers", "create", "Tạo khách hàng mới"),
    ("customers:update", "customers", "update", "Cập nhật khách hàng"),
    ("customers:delete", "customers", "delete", "Xóa khách hàng"),
    # Products
    ("products:read", "products", "read", "Xem sản phẩm"),
    ("products:create", "products", "create", "Tạo sản phẩm mới"),
    ("products:update", "products", "update", "Cập nhật sản phẩm"),
    ("products:delete", "products", "delete", "Xóa sản phẩm"),
    # Orders
    ("orders:read", "orders", "read", "Xem đơn hàng"),
    ("orders:create", "orders", "create", "Tạo đơn hàng mới"),
    ("orders:update", "orders", "update", "Cập nhật đơn hàng"),
    ("orders:delete", "orders", "delete", "Hủy đơn hàng"),
    # Analytics
    ("analytics:read", "analytics", "read", "Xem phân tích"),
    ("analytics:run", "analytics", "run", "Chạy phân tích"),
    ("analytics:score", "analytics", "score", "Tính điểm khách hàng"),
    ("analytics:predict", "analytics", "predict", "Chạy dự đoán mua lại"),
    # Import
    ("import:create", "import", "create", "Upload và import dữ liệu"),
    ("import:read", "import", "read", "Xem trạng thái import"),
    ("import:update", "import", "update", "Cập nhật import job"),
    # Consolidation
    ("consolidation:create", "consolidation", "create", "Hợp nhất dữ liệu khách hàng"),
    ("consolidation:read", "consolidation", "read", "Xem kết quả hợp nhất"),
    ("customers:export", "customers", "export", "Xuất dữ liệu khách hàng"),
]
DEMO_TEAM_CODE = "DEMO_TEAM"
DEMO_USERS = (
    ("user@example.com", "Demo User", "USER", "User123!"),
)
SUPPORTED_ROLE_CODES = frozenset({"ADMIN", "USER"})


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
    permission_codes = tuple(code for code, *_ in PERMISSIONS)
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(PermissionModel).where(PermissionModel.code.in_(permission_codes))
        )
        permission_map = {
            permission.code: permission for permission in result.scalars().all()
        }

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
        admin_role.permissions = list(permission_map.values())
        roles["ADMIN"] = admin_role


        # USER role — customer-facing access without backoffice permissions
        result = await session.execute(
            select(RoleModel).where(RoleModel.code == "USER")
        )
        user_role = result.scalar_one_or_none()
        if not user_role:
            user_role = RoleModel(
                id=uuid_utils.uuid7(),
                code="USER",
                name="User",
                description="Người dùng khách hàng",
            )
            session.add(user_role)
        user_role.permissions = (
            [permission_map["products:read"]]
            if "products:read" in permission_map
            else []
        )
        roles["USER"] = user_role
        # Migrate legacy role assignments before removing unsupported roles.
        result = await session.execute(
            select(RoleModel).where(~RoleModel.code.in_(SUPPORTED_ROLE_CODES))
        )
        legacy_roles = result.scalars().all()
        if legacy_roles:
            legacy_role_ids = [role.id for role in legacy_roles]
            await session.execute(
                update(UserModel)
                .where(UserModel.role_id.in_(legacy_role_ids))
                .values(role_id=user_role.id, team_id=None)
            )
            await session.flush()
            for role in legacy_roles:
                role.permissions = []
                await session.delete(role)
            await session.flush()

        await session.commit()
    return roles


async def seed_admin_user(roles: dict[str, RoleModel]) -> UserModel | None:
    """Create initial admin user if not exists."""
    async with AsyncSessionFactory() as session:
        admin_role = roles.get("ADMIN")
        if not admin_role:
            raise ValueError("ADMIN role not found")

        result = await session.execute(
            select(UserModel).where(UserModel.email == "admin@example.com")
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.role_id = admin_role.id
            existing.status = UserStatus.ACTIVE
            await session.commit()
            return existing

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


async def seed_demo_users(roles: dict[str, RoleModel]) -> dict[str, UserModel]:
    """Create demo accounts and assign the dataset for role testing."""
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(TeamModel).where(TeamModel.code == DEMO_TEAM_CODE)
        )
        team = result.scalar_one_or_none()
        if team is None:
            team = TeamModel(
                id=uuid_utils.uuid7(),
                code=DEMO_TEAM_CODE,
                name="Demo Team",
                description="Default team for local role testing",
                is_active=True,
            )
            session.add(team)
            await session.flush()

        users: dict[str, UserModel] = {}
        for email, full_name, role_code, password in DEMO_USERS:
            role = roles.get(role_code)
            if role is None:
                raise ValueError(f"{role_code} role not found")

            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.scalar_one_or_none()
            if user is None:
                user = UserModel(
                    id=uuid_utils.uuid7(),
                    email=email,
                    password_hash=hash_password(password),
                    full_name=full_name,
                    status=UserStatus.ACTIVE,
                )
                session.add(user)

            user.role_id = role.id
            user.status = UserStatus.ACTIVE
            user.team_id = None
            users[role_code] = user

        await session.flush()
        customers = list(
            (
                await session.execute(select(CustomerModel).order_by(CustomerModel.id))
            ).scalars()
        )
        scoped_users = [users["USER"]]
        for index, customer in enumerate(customers):
            customer.team_id = team.id
            customer.assigned_user_id = scoped_users[index % len(scoped_users)].id

        await session.commit()
    return users


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
    demo_users = await seed_demo_users(roles)
    print(f"✓ Demo users ready: {len(demo_users)}")

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
