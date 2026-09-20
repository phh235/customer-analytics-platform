"""Create non-PII analytics views and query audit storage.

Revision ID: k1b2c3d4e5f6
Revises: j0a1b2c3d4e5
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "k1b2c3d4e5f6"
down_revision: str | None = "j0a1b2c3d4e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Expose only approved analytics columns through views."""
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.execute(
        """
        CREATE OR REPLACE VIEW analytics.customer_sales AS
        SELECT
            o.order_date AS created_at,
            o.total_amount,
            o.net_amount,
            o.status,
            c.region AS customer_region
        FROM public.customers AS c
        JOIN public.orders AS o ON o.customer_id = c.id
        WHERE c.is_deleted = FALSE
        """
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW analytics.product_sales AS
        SELECT
            p.name AS product_name,
            p.category,
            o.order_date AS created_at,
            oi.quantity,
            COALESCE(oi.line_total, oi.line_subtotal, oi.subtotal) AS line_total,
            o.status
        FROM public.order_items AS oi
        JOIN public.orders AS o ON o.id = oi.order_id
        JOIN public.products AS p ON p.id = oi.product_id
        WHERE p.is_deleted = FALSE
        """
    )
    op.create_table(
        "ai_query_audits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("organization_id", sa.String(length=100), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("generated_sql", sa.Text(), nullable=True),
        sa.Column("validated_sql", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("model", sa.String(length=150), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_ai_query_audits"),
    )
    op.create_index("ix_ai_query_audits_user_id", "ai_query_audits", ["user_id"])
    op.create_index("ix_ai_query_audits_status", "ai_query_audits", ["status"])


def downgrade() -> None:
    """Remove controlled analytics storage and views."""
    op.drop_index("ix_ai_query_audits_status", table_name="ai_query_audits")
    op.drop_index("ix_ai_query_audits_user_id", table_name="ai_query_audits")
    op.drop_table("ai_query_audits")
    op.execute("DROP VIEW IF EXISTS analytics.product_sales")
    op.execute("DROP VIEW IF EXISTS analytics.customer_sales")
    op.execute("DROP SCHEMA IF EXISTS analytics")
