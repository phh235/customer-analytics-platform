"""Check seed data in database."""
import asyncio
import sys

from sqlalchemy import text

from customer_analytics.core.database import AsyncSessionFactory, engine


async def check() -> None:
    """Check table counts."""
    async with AsyncSessionFactory() as session:
        tables = ["users", "customers", "orders", "order_items", "products"]
        for table in tables:
            r = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = r.scalar()
            print(f"{table}: {count}")

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(check())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
