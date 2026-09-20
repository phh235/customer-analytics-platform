"""Add timestamp defaults required by analytics audit ORM model.

Revision ID: l2c3d4e5f6a7
Revises: k1b2c3d4e5f6
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "l2c3d4e5f6a7"
down_revision: str | None = "k1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Make audit timestamps safe for ORM inserts."""
    timestamp_type = sa.DateTime(timezone=True)
    op.alter_column(
        "ai_query_audits",
        "created_at",
        existing_type=timestamp_type,
        existing_nullable=False,
        server_default=sa.func.now(),
    )
    op.alter_column(
        "ai_query_audits",
        "updated_at",
        existing_type=timestamp_type,
        existing_nullable=False,
        server_default=sa.func.now(),
    )


def downgrade() -> None:
    """Remove audit timestamp defaults."""
    timestamp_type = sa.DateTime(timezone=True)
    op.alter_column(
        "ai_query_audits",
        "updated_at",
        existing_type=timestamp_type,
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "ai_query_audits",
        "created_at",
        existing_type=timestamp_type,
        existing_nullable=False,
        server_default=None,
    )
