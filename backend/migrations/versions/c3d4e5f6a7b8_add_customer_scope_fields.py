"""Add team and assignment scope fields.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add user/team ownership columns for data scoping."""
    op.add_column("users", sa.Column("team_id", sa.Uuid(), nullable=True))
    op.create_index("ix_users_team_id", "users", ["team_id"])
    op.add_column("customers", sa.Column("assigned_user_id", sa.Uuid(), nullable=True))
    op.add_column("customers", sa.Column("team_id", sa.Uuid(), nullable=True))
    op.create_index("ix_customers_assigned_user_id", "customers", ["assigned_user_id"])
    op.create_index("ix_customers_team_id", "customers", ["team_id"])
    op.create_foreign_key(
        "fk_customers_assigned_user_id_users",
        "customers",
        "users",
        ["assigned_user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Remove user/team ownership columns."""
    op.drop_constraint(
        "fk_customers_assigned_user_id_users", "customers", type_="foreignkey"
    )
    op.drop_index("ix_customers_team_id", table_name="customers")
    op.drop_index("ix_customers_assigned_user_id", table_name="customers")
    op.drop_column("customers", "team_id")
    op.drop_column("customers", "assigned_user_id")
    op.drop_index("ix_users_team_id", table_name="users")
    op.drop_column("users", "team_id")
