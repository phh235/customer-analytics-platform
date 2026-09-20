"""Expose product-view events through the controlled analytics boundary."""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "p6a7b8c9d0e1"
down_revision: str | Sequence[str] | None = "o5f6a7b8c9d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the non-PII product-view analytics view and grant read access."""
    op.execute(
        """
        CREATE OR REPLACE VIEW analytics.product_views AS
        SELECT
            p.name AS product_name,
            p.category,
            ci.interaction_timestamp AS created_at,
            1::integer AS view_count
        FROM public.customer_interactions AS ci
        JOIN public.customers AS c ON c.id = ci.customer_id
        JOIN public.products AS p ON p.id = ci.product_id
        WHERE ci.interaction_type = 'product_view'
          AND c.is_deleted = FALSE
          AND p.is_deleted = FALSE
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_analytics') THEN
                GRANT SELECT ON analytics.product_views TO ai_analytics;
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    """Remove the product-view analytics view."""
    op.execute("DROP VIEW IF EXISTS analytics.product_views")
