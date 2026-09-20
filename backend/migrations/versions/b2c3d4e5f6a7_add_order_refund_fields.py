"""Add refund and net amounts to orders.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add refund and net amount columns with validation constraints."""
    op.add_column(
        "orders",
        sa.Column(
            "refund_amount",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "orders",
        sa.Column("net_amount", sa.Numeric(12, 2), nullable=True),
    )
    op.execute("UPDATE orders SET net_amount = total_amount")
    op.alter_column("orders", "net_amount", nullable=False)
    op.create_check_constraint(
        "ck_orders_refund_amount_valid",
        "orders",
        "refund_amount >= 0 AND refund_amount <= total_amount",
    )
    op.create_check_constraint(
        "ck_orders_net_amount_non_negative",
        "orders",
        "net_amount >= 0",
    )


def downgrade() -> None:
    """Remove refund and net amount columns."""
    op.drop_constraint("ck_orders_net_amount_non_negative", "orders", type_="check")
    op.drop_constraint("ck_orders_refund_amount_valid", "orders", type_="check")
    op.drop_column("orders", "net_amount")
    op.drop_column("orders", "refund_amount")
