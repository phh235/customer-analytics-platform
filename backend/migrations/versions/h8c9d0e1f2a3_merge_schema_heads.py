"""Merge the pre-existing schema branch with reference code backfill.

Revision ID: h8c9d0e1f2a3
Revises: c9d0e1f2a3b4, g7b8c9d0e1f2
"""

from __future__ import annotations

from collections.abc import Sequence

revision: str = "h8c9d0e1f2a3"
down_revision: tuple[str, str] = ("c9d0e1f2a3b4", "g7b8c9d0e1f2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge the migration branches without changing schema data."""


def downgrade() -> None:
    """Keep the merge revision reversible as a graph-only migration."""
