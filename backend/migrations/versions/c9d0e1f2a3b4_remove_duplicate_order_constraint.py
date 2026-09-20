"""Remove the duplicate order-number constraint represented by a unique index.

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
"""

from __future__ import annotations

from alembic import op

revision = "c9d0e1f2a3b4"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Keep order_number unique through its existing unique index only."""
    op.execute('ALTER TABLE orders DROP CONSTRAINT IF EXISTS "uq_orders_order_number"')


def downgrade() -> None:
    """Restore the named order-number uniqueness constraint."""
    op.create_unique_constraint("uq_orders_order_number", "orders", ["order_number"])
