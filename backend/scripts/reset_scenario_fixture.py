"""Reset business data and seed the deterministic Script_Duan scenario fixture."""

from __future__ import annotations

import argparse
import asyncio
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import insert, text

from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.order.infrastructure.models.order import (
    OrderItemModel,
    OrderModel,
)
from customer_analytics.app.features.product.infrastructure.models.product import (
    ProductModel,
)
from customer_analytics.app.features.reference_data.infrastructure.models import (
    CustomerInteractionModel,
)
from customer_analytics.core.database import AsyncSessionFactory, engine

CUSTOMER_IDS = {
    "KH0013": uuid.UUID("10000000-0000-4000-8000-000000000013"),
    "KH0045": uuid.UUID("10000000-0000-4000-8000-000000000045"),
    "KH0060": uuid.UUID("10000000-0000-4000-8000-000000000060"),
    "KH0021": uuid.UUID("10000000-0000-4000-8000-000000000021"),
    "KH0030": uuid.UUID("10000000-0000-4000-8000-000000000030"),
    "KH0040": uuid.UUID("10000000-0000-4000-8000-000000000040"),
}
CUSTOMER_NAMES = {
    "KH0013": "Nguyễn Thanh Hiếu",
    "KH0045": "Trần Minh Anh",
    "KH0060": "Lê Hoàng Nam",
    "KH0021": "Phạm Gia Hân",
    "KH0030": "Võ Quốc Phúc",
    "KH0040": "Đặng Thu Linh",
}
PRODUCT_IDS = {
    "P001": uuid.UUID("20000000-0000-4000-8000-000000000001"),
    "P002": uuid.UUID("20000000-0000-4000-8000-000000000002"),
    "P003": uuid.UUID("20000000-0000-4000-8000-000000000003"),
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Delete all business data and seed the deterministic fixture.",
    )
    return parser


def _customers(now: datetime) -> list[dict[str, object]]:
    return [
        {
            "id": customer_id,
            "customer_code": code,
            "source_customer_id": code,
            "name": CUSTOMER_NAMES[code],
            "email": f"{code.lower()}@scenario.test",
            "status": "ACTIVE",
            "customer_since": now,
            "total_orders": 0,
            "total_spent": Decimal("0"),
            "avg_order_value": Decimal("0"),
            "is_deleted": False,
        }
        for code, customer_id in CUSTOMER_IDS.items()
    ]


def _products() -> list[dict[str, object]]:
    return [
        {
            "id": PRODUCT_IDS["P001"],
            "source_product_id": "P001",
            "product_code": "P001",
            "sku": "SCENARIO-P001",
            "name": "Laptop scenario",
            "category": "Điện tử",
            "description": "Sản phẩm dùng cho kịch bản Script_Duan.",
            "price": Decimal("2300000"),
            "currency": "VND",
            "status": "ACTIVE",
            "is_deleted": False,
        },
        {
            "id": PRODUCT_IDS["P002"],
            "source_product_id": "P002",
            "product_code": "P002",
            "sku": "SCENARIO-P002",
            "name": "Tai nghe scenario",
            "category": "Phụ kiện",
            "description": "Sản phẩm dùng cho kịch bản Script_Duan.",
            "price": Decimal("500000"),
            "currency": "VND",
            "status": "ACTIVE",
            "is_deleted": False,
        },
        {
            "id": PRODUCT_IDS["P003"],
            "source_product_id": "P003",
            "product_code": "P003",
            "sku": "SCENARIO-P003",
            "name": "Đồ dùng cá nhân scenario",
            "category": "Đồ dùng cá nhân",
            "description": "Sản phẩm dùng cho kịch bản Script_Duan.",
            "price": Decimal("300000"),
            "currency": "VND",
            "status": "ACTIVE",
            "is_deleted": False,
        },
    ]


def _orders() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    history: list[tuple[str, str, str, Decimal]] = []
    target_dates = [
        "2025-12-19",
        "2026-01-23",
        "2026-02-27",
        "2026-04-03",
        "2026-05-08",
        "2026-06-12",
        "2026-07-17",
        "2026-08-20",
    ]
    target_amounts = [Decimal("2300000")] * 7 + [Decimal("2400000")]
    history.extend(
        ("KH0013", value, "P001", amount)
        for value, amount in zip(target_dates, target_amounts, strict=True)
    )
    history.append(("KH0013", "2026-09-15", "P001", Decimal("2300000")))
    history.extend(
        ("KH0045", value, "P002", Decimal("500000"))
        for value in ["2026-01-10", "2026-03-10", "2026-05-10", "2026-07-10"]
    )
    history.extend(
        ("KH0060", value, "P001", Decimal("2300000"))
        for value in ["2026-02-01", "2026-04-01", "2026-06-01"]
    )
    history.append(("KH0060", "2026-09-20", "P001", Decimal("2300000")))
    history.extend(
        [
            ("KH0021", "2026-02-15", "P003", Decimal("300000")),
            ("KH0021", "2026-05-15", "P003", Decimal("300000")),
            ("KH0030", "2026-06-20", "P002", Decimal("500000")),
            ("KH0040", "2025-10-20", "P003", Decimal("300000")),
        ]
    )

    orders: list[dict[str, object]] = []
    items: list[dict[str, object]] = []
    for index, (customer_code, order_date, product_code, amount) in enumerate(
        history, start=1
    ):
        order_id = uuid.UUID(f"30000000-0000-4000-8000-{index:012d}")
        order_number = f"DH{index:05d}"
        parsed_date = datetime.combine(
            date.fromisoformat(order_date), datetime.min.time(), tzinfo=UTC
        )
        orders.append(
            {
                "id": order_id,
                "customer_id": CUSTOMER_IDS[customer_code],
                "source_order_id": order_number,
                "order_number": order_number,
                "order_date": parsed_date,
                "subtotal": amount,
                "total_amount": amount,
                "refund_amount": Decimal("0"),
                "net_amount": amount,
                "currency": "VND",
                "is_valid_for_rfm": True,
                "status": "DELIVERED",
                "channel": "ONLINE",
                "sales_channel": "ONLINE",
            }
        )
        items.append(
            {
                "id": uuid.UUID(f"40000000-0000-4000-8000-{index:012d}"),
                "order_id": order_id,
                "product_id": PRODUCT_IDS[product_code],
                "item_sequence": 1,
                "quantity": 1,
                "unit_price": amount,
                "subtotal": amount,
                "line_subtotal": amount,
                "line_amount": amount,
                "line_total": amount,
            }
        )
    return orders, items


def _interactions(now: datetime) -> list[dict[str, object]]:
    return [
        {
            "id": uuid.UUID("50000000-0000-4000-8000-000000000001"),
            "interaction_code": "INT001",
            "customer_id": CUSTOMER_IDS["KH0013"],
            "product_id": PRODUCT_IDS["P001"],
            "interaction_type": "CLICK",
            "interaction_timestamp": datetime(2026, 8, 20, 10, tzinfo=UTC),
            "channel": "WEB",
            "interaction_value": Decimal("40"),
            "is_mock_data": True,
        },
        {
            "id": uuid.UUID("50000000-0000-4000-8000-000000000002"),
            "interaction_code": "INT002",
            "customer_id": CUSTOMER_IDS["KH0013"],
            "product_id": PRODUCT_IDS["P001"],
            "interaction_type": "VIEW",
            "interaction_timestamp": datetime(2026, 8, 21, 10, tzinfo=UTC),
            "channel": "WEB",
            "interaction_value": Decimal("36"),
            "is_mock_data": True,
        },
        {
            "id": uuid.UUID("50000000-0000-4000-8000-000000000003"),
            "interaction_code": "INT003",
            "customer_id": CUSTOMER_IDS["KH0045"],
            "product_id": PRODUCT_IDS["P002"],
            "interaction_type": "VIEW",
            "interaction_timestamp": datetime(2026, 8, 10, 10, tzinfo=UTC),
            "channel": "WEB",
            "interaction_value": Decimal("20"),
            "is_mock_data": True,
        },
    ]


async def _reset() -> None:
    now = datetime.now(UTC)
    orders, order_items = _orders()
    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE customer_interactions, order_items, customers, "
                "products, orders, import_jobs, model_registry, analysis_runs "
                "RESTART IDENTITY CASCADE"
            )
        )

    async with AsyncSessionFactory() as session:
        await session.execute(insert(CustomerModel.__table__), _customers(now))
        await session.execute(insert(ProductModel.__table__), _products())
        await session.execute(insert(OrderModel.__table__), orders)
        await session.execute(insert(OrderItemModel.__table__), order_items)
        await session.execute(
            insert(CustomerInteractionModel.__table__), _interactions(now)
        )
        await session.commit()

    await engine.dispose()
    print(
        "Scenario fixture ready: 6 customers, 3 products, "
        f"{len(orders)} orders, {len(order_items)} order items, 3 interactions."
    )


def main() -> None:
    args = _parser().parse_args()
    if not args.confirm:
        raise SystemExit("Refusing to reset business data without --confirm")
    asyncio.run(_reset())


if __name__ == "__main__":
    main()
