"""Seed test data — bulk insert for speed on remote DB."""

from __future__ import annotations

import asyncio
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import uuid_utils
from sqlalchemy import insert, text

# Import models for create_all
from customer_analytics.app.features.customer.infrastructure.models.customer import (  # noqa: E501
    CustomerModel,
)
from customer_analytics.app.features.order.infrastructure.models.order import (  # noqa: E501
    OrderItemModel,
    OrderModel,
)
from customer_analytics.app.features.product.infrastructure.models.product import (  # noqa: E501
    ProductModel,
)
from customer_analytics.core.database import Base, engine
from customer_analytics.core.database.session import AsyncSessionFactory

FIRST_NAMES = [
    "Nguyen",
    "Tran",
    "Le",
    "Pham",
    "Hoang",
    "Phan",
    "Vu",
    "Vo",
    "Dang",
    "Bui",
    "Do",
    "Ho",
    "Ngo",
    "Duong",
    "Ly",
]
LAST_NAMES = [
    "Van An",
    "Minh Tu",
    "Quoc Bao",
    "Huu Phuc",
    "Duc Tai",
    "Thanh Long",
    "Anh Khoi",
    "Ngoc Son",
    "Tien Dat",
    "Quang Huy",
    "Thi Mai",
    "Ngoc Anh",
    "Phuong Linh",
    "Thao Vy",
    "Minh Chau",
    "Ngoc Lan",
    "Thi Tam",
    "Kim Anh",
    "Thi Hue",
    "Bich Ngoc",
]
REGIONS = [
    "Ho Chi Minh",
    "Ha Noi",
    "Da Nang",
    "Hai Phong",
    "Can Tho",
    "Binh Duong",
    "Dong Nai",
    "Quang Ninh",
    "Thanh Hoa",
    "Nghe An",
]
CATEGORIES = [
    "Electronics",
    "Fashion",
    "Food & Beverage",
    "Health & Beauty",
    "Home & Living",
    "Sports",
    "Books",
    "Toys",
    "Automotive",
    "Grocery",
]
CHANNELS = ["online", "pos", "phone"]
ORDER_STATUSES = ["COMPLETED"] * 4 + ["CANCELLED"]

BATCH_SIZE = 100  # rows per bulk insert


def _rng_date(start_days: int, end_days: int = 0) -> datetime:
    days = random.randint(end_days, start_days)
    return datetime.now(UTC) - timedelta(days=days)


async def seed_products(session, count: int = 30) -> list[str]:
    now = datetime.now(UTC)
    ids = [str(uuid_utils.uuid7()) for _ in range(count)]
    rows = [
        {
            "id": ids[i],
            "name": f"Product {i + 1:03d}",
            "sku": f"SEED-SKU-{i + 1:03d}",
            "category": random.choice(CATEGORIES),
            "description": f"Seed product description {i + 1:03d}.",
            "image_url": None,
            "price": Decimal(str(round(random.uniform(50_000, 5_000_000), 2))),
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
        }
        for i in range(count)
    ]
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        await session.execute(insert(ProductModel.__table__), batch)
    await session.flush()
    return ids


async def seed_customers(session, count: int = 50) -> list[str]:
    now = datetime.now(UTC)
    ids = [str(uuid_utils.uuid7()) for _ in range(count)]
    rows = []
    for i in range(count):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        rows.append(
            {
                "id": ids[i],
                "name": name,
                "email": f"{name.lower().replace(' ', '.')}_{i}@example.com",
                "phone": f"09{random.randint(10_000_000, 99_999_999)}",
                "address": (
                    f"{random.randint(1, 200)} Duong "
                    f"{random.randint(1, 100)}, {random.choice(REGIONS)}"
                ),
                "status": "ACTIVE",
                "gender": random.choice(["M", "F"]),
                "date_of_birth": _rng_date(25_000, 7_000).date(),
                "region": random.choice(REGIONS),
                "customer_since": _rng_date(730, 30),
                "total_orders": 0,
                "total_spent": Decimal("0"),
                "avg_order_value": Decimal("0"),
                "last_purchase_date": None,
                "created_at": now,
                "updated_at": now,
            }
        )
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        await session.execute(insert(CustomerModel.__table__), batch)
    await session.flush()
    return ids


async def seed_orders(session, customer_ids: list[str], product_ids: list[str]) -> None:
    """Seed orders + order_items in bulk batches."""
    now = datetime.now(UTC)
    order_rows = []
    item_rows = []
    order_num = 1

    for cid in customer_ids:
        for _ in range(random.randint(1, 15)):
            order_id = str(uuid_utils.uuid7())
            n_items = random.randint(1, 5)
            total = Decimal("0")
            items = []
            for _ in range(n_items):
                qty = random.randint(1, 5)
                price = Decimal(str(round(random.uniform(50_000, 5_000_000), 2)))
                sub = price * qty
                total += sub
                items.append(
                    {
                        "id": str(uuid_utils.uuid7()),
                        "order_id": order_id,
                        "product_id": random.choice(product_ids),
                        "quantity": qty,
                        "unit_price": price,
                        "subtotal": sub,
                    }
                )
            order_rows.append(
                {
                    "id": order_id,
                    "customer_id": cid,
                    "order_number": f"ORD-{order_num:06d}",
                    "order_date": _rng_date(365, 0),
                    "total_amount": total,
                    "status": random.choice(ORDER_STATUSES),
                    "channel": random.choice(CHANNELS),
                    "notes": None,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            item_rows.extend(items)
            order_num += 1

    # Bulk insert orders
    for start in range(0, len(order_rows), BATCH_SIZE):
        batch = order_rows[start : start + BATCH_SIZE]
        await session.execute(insert(OrderModel.__table__), batch)

    # Bulk insert order_items
    for start in range(0, len(item_rows), BATCH_SIZE):
        batch = item_rows[start : start + BATCH_SIZE]
        await session.execute(insert(OrderItemModel.__table__), batch)

    await session.flush()


async def update_customer_stats(session) -> None:
    """Update customer aggregated stats from orders."""
    await session.execute(
        text(
            """
            UPDATE customers c
            SET
                total_orders = COALESCE(s.total_orders, 0),
                total_spent = COALESCE(s.total_spent, 0),
                avg_order_value = COALESCE(s.avg_order_value, 0),
                last_purchase_date = s.last_purchase_date
            FROM (
                SELECT
                    customer_id,
                    COUNT(*) AS total_orders,
                    SUM(total_amount) AS total_spent,
                    AVG(total_amount) AS avg_order_value,
                    MAX(order_date) AS last_purchase_date
                FROM orders
                WHERE status = 'COMPLETED'
                GROUP BY customer_id
            ) s
            WHERE c.id = s.customer_id
            """
        )
    )
    await session.flush()


async def main() -> None:
    print("Seeding (bulk mode)...")

    async with AsyncSessionFactory() as session:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        product_ids = await seed_products(session, 30)
        print(f"  Products: {len(product_ids)}")

        customer_ids = await seed_customers(session, 50)
        print(f"  Customers: {len(customer_ids)}")

        await seed_orders(session, customer_ids, product_ids)
        print("  Orders + items inserted")

        await update_customer_stats(session)
        print("  Customer stats updated")

        await session.commit()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
