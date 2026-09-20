"""Align the preference foreign-key constraint name with product_id.

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
"""

from __future__ import annotations

from alembic import op

revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


OLD_CONSTRAINT = "fk_customer_product_preferences_product_category_id_products"
NEW_CONSTRAINT = "fk_customer_product_preferences_product_id_products"


def upgrade() -> None:
    """Rename the foreign-key constraint after the product column rename."""
    op.execute(
        "ALTER TABLE customer_product_preferences "
        f'RENAME CONSTRAINT "{OLD_CONSTRAINT}" TO "{NEW_CONSTRAINT}"'
    )


def downgrade() -> None:
    """Restore the previous foreign-key constraint name."""
    op.execute(
        "ALTER TABLE customer_product_preferences "
        f'RENAME CONSTRAINT "{NEW_CONSTRAINT}" TO "{OLD_CONSTRAINT}"'
    )
