"""Backfill human-readable customer and product reference codes.

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "g7b8c9d0e1f2"
down_revision: str | Sequence[str] | None = "f6a7b8c9d0e1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Assign stable display codes to records that do not have one."""
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
    op.execute(
        sa.text(
            """
            WITH numbered AS (
                SELECT id, ROW_NUMBER() OVER (ORDER BY created_at, id) AS row_number
                FROM products
                WHERE product_code IS NULL
            ), offsets AS (
                SELECT COALESCE(
                    MAX(CAST(SUBSTRING(product_code FROM 4) AS BIGINT)), 0
                ) AS value
                FROM products
                WHERE product_code ~ '^SP-[0-9]+$'
            )
            UPDATE products AS product
            SET product_code = 'SP-' || LPAD(
                (numbered.row_number + offsets.value)::text, 6, '0'
            )
            FROM numbered, offsets
            WHERE product.id = numbered.id
            """
        )
    )


def downgrade() -> None:
    """Remove generated codes using the reserved display-code formats."""
    op.execute(
        sa.text(
            "UPDATE customers "
            "SET customer_code = NULL "
            "WHERE customer_code ~ '^KH-[0-9]+$'"
        )
    )
    op.execute(
        sa.text(
            "UPDATE products "
            "SET product_code = NULL "
            "WHERE product_code ~ '^SP-[0-9]+$'"
        )
    )
