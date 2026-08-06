"""change status column to enum type

Revision ID: c44defbe5678
Revises: b33adfbc0435
Create Date: 2026-08-05 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c44defbe5678"
down_revision: str | Sequence[str] | None = "b33adfbc0435"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Define the enum values
user_status_enum = sa.Enum("ACTIVE", "DISABLED", "LOCKED", name="userstatus")


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type
    user_status_enum.create(op.get_bind(), checkfirst=True)

    # Alter the status column from VARCHAR to ENUM
    op.alter_column(
        "users",
        "status",
        existing_type=sa.String(length=20),
        type_=user_status_enum,
        nullable=False,
        server_default="ACTIVE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Alter the status column back to VARCHAR
    op.alter_column(
        "users",
        "status",
        existing_type=user_status_enum,
        type_=sa.String(length=20),
        nullable=False,
        server_default="ACTIVE",
    )

    # Drop the enum type
    user_status_enum.drop(op.get_bind(), checkfirst=True)
