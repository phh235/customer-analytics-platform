"""Grant the analytics role access to approved views.

Revision ID: m3d4e5f6a7b8
Revises: l2c3d4e5f6a7
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "m3d4e5f6a7b8"
down_revision: str | None = "l2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


_ROLE_EXISTS = """
    SELECT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'ai_analytics'
    )
"""


def upgrade() -> None:
    """Grant only schema usage and SELECT on approved analytics views."""
    op.execute(
        f"""
        DO $$
        BEGIN
            IF ({_ROLE_EXISTS}) THEN
                EXECUTE 'GRANT USAGE ON SCHEMA analytics TO ai_analytics';
                EXECUTE 'GRANT SELECT ON analytics.customer_sales TO ai_analytics';
                EXECUTE 'GRANT SELECT ON analytics.product_sales TO ai_analytics';
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Revoke approved view access from the analytics role."""
    op.execute(
        f"""
        DO $$
        BEGIN
            IF ({_ROLE_EXISTS}) THEN
                EXECUTE 'REVOKE SELECT ON analytics.customer_sales FROM ai_analytics';
                EXECUTE 'REVOKE SELECT ON analytics.product_sales FROM ai_analytics';
                EXECUTE 'REVOKE USAGE ON SCHEMA analytics FROM ai_analytics';
            END IF;
        END $$;
        """
    )
