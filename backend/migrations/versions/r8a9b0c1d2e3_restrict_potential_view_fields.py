"""Keep customer PII out of the controlled potential analytics view."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "r8a9b0c1d2e3"
down_revision: str | Sequence[str] | None = "q7a8b9c0d1e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Expose only the customer reference and score fields to analytics chat."""
    op.execute("DROP VIEW IF EXISTS analytics.customer_potential_current")
    op.execute(
        """
        CREATE VIEW analytics.customer_potential_current AS
        SELECT
            c.customer_code,
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
    """Restore the original canonical view shape."""
    op.execute("DROP VIEW IF EXISTS analytics.customer_potential_current")
    op.execute(
        """
        CREATE VIEW analytics.customer_potential_current AS
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
