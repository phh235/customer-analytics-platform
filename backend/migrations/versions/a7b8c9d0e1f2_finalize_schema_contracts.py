"""Finalize schema contracts for analytics, authorization, and audit fields.

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "a7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


_UUID_PATTERN = "'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'"


def upgrade() -> None:
    """Apply the final schema contracts without recreating the database."""
    op.create_table(
        "teams",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_teams"),
    )
    op.create_index("ix_teams_code", "teams", ["code"], unique=True)

    op.create_foreign_key(
        "fk_users_team_id_teams",
        "users",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_customers_team_id_teams",
        "customers",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # users.role_id is the single authorization ownership mechanism.
    op.drop_table("user_roles")

    op.alter_column(
        "customer_product_preferences",
        "product_category_id",
        new_column_name="product_id",
    )

    op.alter_column(
        "customer_behavior_history",
        "recency_days",
        existing_type=sa.Integer(),
        nullable=True,
    )
    for column in ("r_score", "f_score", "m_score", "potential_score"):
        op.alter_column(
            "customer_potential_score_history",
            column,
            existing_type=sa.Numeric(6, 2),
            nullable=True,
        )

    op.alter_column(
        "import_jobs",
        "created_by",
        existing_type=sa.String(length=100),
        type_=sa.Uuid(),
        postgresql_using=(
            "CASE WHEN created_by ~* "
            f"{_UUID_PATTERN} THEN created_by::uuid ELSE NULL END"
        ),
        nullable=True,
    )
    op.create_foreign_key(
        "fk_import_jobs_created_by_users",
        "import_jobs",
        "users",
        ["created_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Restore the previous schema contracts."""
    op.drop_constraint(
        "fk_import_jobs_created_by_users", "import_jobs", type_="foreignkey"
    )
    op.alter_column(
        "import_jobs",
        "created_by",
        existing_type=sa.Uuid(),
        type_=sa.String(length=100),
        postgresql_using="created_by::text",
        nullable=True,
    )

    for column in ("r_score", "f_score", "m_score", "potential_score"):
        op.alter_column(
            "customer_potential_score_history",
            column,
            existing_type=sa.Numeric(6, 2),
            nullable=False,
        )
    op.alter_column(
        "customer_behavior_history",
        "recency_days",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "customer_product_preferences",
        "product_id",
        new_column_name="product_category_id",
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id", name="pk_user_roles"),
    )
    op.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) SELECT id, role_id FROM users"
        )
    )

    op.drop_constraint("fk_customers_team_id_teams", "customers", type_="foreignkey")
    op.drop_constraint("fk_users_team_id_teams", "users", type_="foreignkey")
    op.drop_index("ix_teams_code", table_name="teams")
    op.drop_table("teams")
