"""Add customer soft-deletion state from the aligned data contract.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add a non-destructive soft-deletion flag to customers."""
    op.add_column(
        "customers",
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
    )


def downgrade() -> None:
    """Remove the customer soft-deletion flag."""
    op.drop_column("customers", "is_deleted")
