"""
Alembic environment configuration.

Kết nối với SQLAlchemy metadata của project và lấy database URL từ settings.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.infrastructure.models.aligned import (  # noqa: F401
    AnalysisRunModel,
    ConfigurationVersionModel,
    CustomerBehaviorHistoryModel,
    CustomerPotentialScoreHistoryModel,
    CustomerProductPreferenceModel,
    MLModelEvaluationModel,
    ScoringRuleModel,
    ScoringThresholdModel,
    SegmentationRuleModel,
    ValidOrderStatusConfigModel,
)
from customer_analytics.app.features.analytics.infrastructure.models.analytics_history import (  # noqa: E501, F401
    PurchasePredictionModel,
    SegmentHistoryModel,
)
from customer_analytics.app.features.analytics.infrastructure.models.analytics_query_audit import (  # noqa: E501, F401
    AnalyticsQueryAuditModel,
)
from customer_analytics.app.features.analytics.infrastructure.models.model_registry import (  # noqa: E501, F401
    ModelRegistryModel,
)
from customer_analytics.app.features.customer.infrastructure.models.customer import (  # noqa: F401
    CustomerAssignmentModel,
    CustomerModel,
)
from customer_analytics.app.features.identity.infrastructure.models.password_reset_challenge import (  # noqa: E501, F401
    PasswordResetChallengeModel,
)
from customer_analytics.app.features.identity.infrastructure.models.refresh_token import (  # noqa: E501, F401
    RefreshTokenModel,
)

# Import all ORM models so Alembic can detect them
from customer_analytics.app.features.identity.infrastructure.models.user import (  # noqa: F401
    PermissionModel,
    RoleModel,
    RolePermissionModel,
    TeamModel,
    UserModel,
)
from customer_analytics.app.features.import_data.infrastructure.models.import_job import (  # noqa: E501, F401
    ImportJobModel,
)
from customer_analytics.app.features.operations.infrastructure.models import (  # noqa: F401
    AuditLogModel,
    ImportErrorModel,
)
from customer_analytics.app.features.order.infrastructure.models.order import (  # noqa: F401
    OrderItemModel,
    OrderModel,
)
from customer_analytics.app.features.product.infrastructure.models.product import (  # noqa: F401
    ProductModel,
)
from customer_analytics.app.features.reference_data.infrastructure.models import (  # noqa: F401
    CampaignModel,
    CustomerInteractionModel,
    EmployeeModel,
    GeolocationModel,
    PaymentModel,
    ReviewModel,
    SellerModel,
)

# Import project modules
from customer_analytics.core.database import Base

# Alembic Config object
config = context.config

# Cấu hình logging từ alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Gắn metadata — để Alembic tự động phát hiện thay đổi model
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Chạy migration ở offline mode (không cần database).

    Dùng khi muốn generate SQL script mà không chạy thật.
    """
    url = settings.database_url_sync
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Chạy migration trên một connection có sẵn."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Chạy migration ở online mode — kết nối database thật."""
    # Dùng async engine với URL async (có +asyncpg)
    connectable = create_async_engine(settings.database_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
