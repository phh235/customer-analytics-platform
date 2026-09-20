"""Backfill customer codes for profiles created without imports."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "o5f6a7b8c9d0"
down_revision: str | Sequence[str] | None = "n4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Assign stable display codes to customers missing one."""
    op.execute(
        sa.text(
            """
            WITH numbered AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, id) AS row_number
                FROM customers
                WHERE customer_code IS NULL
            ), offsets AS (
                SELECT COALESCE(
                    MAX(CAST(SUBSTRING(customer_code FROM 4) AS BIGINT)), 0
                ) AS value
                FROM customers
                WHERE customer_code ~ '^KH-[0-9]+$'
            )
            UPDATE customers AS customer
            SET customer_code = 'KH-' || LPAD(
                (numbered.row_number + offsets.value)::text, 6, '0'
            )
            FROM numbered, offsets
            WHERE customer.id = numbered.id
            """
        )
    )


def downgrade() -> None:
    """Keep generated codes because the migration has no ownership marker."""
    pass
