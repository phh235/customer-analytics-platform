"""Persist the canonical current potential-score snapshot."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "q7a8b9c0d1e2"
down_revision: str | Sequence[str] | None = "p6a7b8c9d0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the current score table and its non-PII analytics view."""
    op.create_table(
        "customer_potential_scores_current",
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("potential_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("potential_level", sa.String(30), nullable=False),
        sa.Column("analysis_date", sa.Date(), nullable=True),
        sa.Column("feature_window_days", sa.Integer(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scoring_configuration_version", sa.String(100), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint(
            "customer_id", name="pk_customer_potential_scores_current"
        ),
    )
    op.execute(
        """
        CREATE OR REPLACE VIEW analytics.customer_potential_current AS
        SELECT
            c.id::text AS customer_id,
            c.customer_code,
            c.name AS customer_name,
            s.potential_score,
            s.potential_level,
            s.analysis_date,
            s.feature_window_days,
            s.calculated_at,
            s.scoring_configuration_version
        FROM public.customer_potential_scores_current AS s
        JOIN public.customers AS c ON c.id = s.customer_id
        WHERE c.is_deleted = FALSE
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_analytics') THEN
                GRANT SELECT ON analytics.customer_potential_current TO ai_analytics;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    """Remove the current score view and snapshot table."""
    op.execute("DROP VIEW IF EXISTS analytics.customer_potential_current")
    op.drop_table("customer_potential_scores_current")
