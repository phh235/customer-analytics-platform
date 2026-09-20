"""Link customer-facing users to customer profiles."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "n4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "m3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add an optional one-to-one user/customer link and backfill email matches."""
    op.add_column("users", sa.Column("customer_id", sa.Uuid(), nullable=True))
    op.create_index("uq_users_customer_id", "users", ["customer_id"], unique=True)
    op.create_foreign_key(
        "fk_users_customer_id_customers",
        "users",
        "customers",
        ["customer_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        """
        UPDATE users AS u
        SET customer_id = c.id
        FROM customers AS c
        WHERE lower(u.email) = lower(c.email)
          AND c.email IS NOT NULL
          AND c.is_deleted = false
        """
    )


def downgrade() -> None:
    """Remove the user/customer link."""
    op.drop_constraint(
        "fk_users_customer_id_customers", "users", type_="foreignkey"
    )
    op.drop_index("uq_users_customer_id", table_name="users")
    op.drop_column("users", "customer_id")
