"""Seed deterministic product catalog metadata for local verification."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal

import uuid_utils
from sqlalchemy import select

from customer_analytics.app.features.product.infrastructure.models.product import (
    ProductModel,
)
from customer_analytics.core.database import Base, engine
from customer_analytics.core.database.session import AsyncSessionFactory

TEST_PRODUCTS = (
    ("QA Dataset Product 1", "QA Electronics", Decimal("1500000.00")),
    ("QA Dataset Product 2", "QA Home", Decimal("1750000.00")),
    ("QA Dataset Product 3", "QA Electronics", Decimal("2000000.00")),
    ("QA Dataset Product 4", "QA Home", Decimal("2250000.00")),
    ("QA Dataset Product 5", "QA Electronics", Decimal("2500000.00")),
)


async def seed() -> None:
    """Create or enrich deterministic products without external credentials."""
    now = datetime.now(UTC)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionFactory() as session:
        for index, (name, category, price) in enumerate(TEST_PRODUCTS, start=1):
            result = await session.execute(
                select(ProductModel).where(ProductModel.name == name)
            )
            product = result.scalar_one_or_none()
            if product is None:
                product = ProductModel(
                    id=uuid_utils.uuid7(),
                    name=name,
                    category=category,
                    price=price,
                    status="ACTIVE",
                )
                session.add(product)

            product.sku = f"QA-SKU-{index:03d}"
            product.description = (
                f"Sản phẩm kiểm thử {index} dùng để xác minh catalog API "
                "và hiển thị thông tin sản phẩm."
            )
            product.image_url = None
            product.updated_at = now

        await session.commit()

    await engine.dispose()
    print(f"Seeded {len(TEST_PRODUCTS)} product catalog test records.")


if __name__ == "__main__":
    asyncio.run(seed())
