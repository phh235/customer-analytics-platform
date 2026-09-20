"""Add Cloudinary image URL to customers.

Revision ID: i9d0e1f2a3b4
Revises: h8c9d0e1f2a3
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "i9d0e1f2a3b4"
down_revision: str | None = "h8c9d0e1f2a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add nullable image URL storage for customer profiles."""
    op.add_column(
        "customers",
        sa.Column("image_url", sa.String(length=1024), nullable=True),
    )


def downgrade() -> None:
    """Remove customer image URL storage."""
    op.drop_column("customers", "image_url")
