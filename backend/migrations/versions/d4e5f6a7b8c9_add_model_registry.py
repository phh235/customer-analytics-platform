"""Add prediction model lifecycle registry.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create model registry for explicit evaluation and deployment."""
    op.create_table(
        "model_registry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("pr_auc", sa.Numeric(10, 6), nullable=True),
        sa.Column("lift_top10", sa.Numeric(10, 4), nullable=True),
        sa.Column("precision_top10", sa.Numeric(10, 6), nullable=True),
        sa.Column("baseline_pr_auc", sa.Numeric(10, 6), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("artifact_uri", sa.String(length=500), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_model_registry"),
        sa.UniqueConstraint("version", name="uq_model_registry_version"),
    )
    op.create_index("ix_model_registry_status", "model_registry", ["status"])


def downgrade() -> None:
    """Drop model registry."""
    op.drop_index("ix_model_registry_status", table_name="model_registry")
    op.drop_table("model_registry")
