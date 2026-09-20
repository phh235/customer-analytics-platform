"""add product catalog fields

Revision ID: a1b2c3d4e5f6
Revises: e76cb3a5caaf
Create Date: 2026-09-16 23:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "e76cb3a5caaf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add catalog metadata and media URL to products."""
    op.add_column(
        "products",
        sa.Column("sku", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.add_column(
        "products",
        sa.Column("image_url", sa.String(length=1024), nullable=True),
    )
    op.create_index("uq_products_sku", "products", ["sku"], unique=True)


def downgrade() -> None:
    """Remove catalog metadata and media URL from products."""
    op.drop_index("uq_products_sku", table_name="products")
    op.drop_column("products", "image_url")
    op.drop_column("products", "description")
    op.drop_column("products", "sku")
