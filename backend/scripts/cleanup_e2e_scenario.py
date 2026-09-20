"""Delete only explicitly identified E2E scenario records.

Usage requires --confirm and exact IDs. Never run this against production data.
"""

from __future__ import annotations

import argparse
import asyncio
import uuid
from pathlib import Path

from sqlalchemy import delete

from customer_analytics.app.config import settings
from customer_analytics.app.features.analytics.infrastructure.models.model_registry import (  # noqa: E501
    ModelRegistryModel,
)
from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.import_data.infrastructure.models.import_job import (  # noqa: E501
    ImportJobModel,
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
from customer_analytics.core.database import AsyncSessionFactory


def _uuid_values(values: list[str]) -> list[uuid.UUID]:
    return [uuid.UUID(value) for value in values]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--customer-id", action="append", required=True)
    parser.add_argument("--product-id", action="append", required=True)
    parser.add_argument("--order-id", action="append", required=True)
    parser.add_argument("--interaction-id", action="append", required=True)
    parser.add_argument("--import-job-id", action="append", required=True)
    parser.add_argument("--model-version", action="append", required=True)
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm deletion after reviewing every supplied identifier.",
    )
    return parser


async def _cleanup(args: argparse.Namespace) -> None:
    customer_ids = _uuid_values(args.customer_id)
    product_ids = _uuid_values(args.product_id)
    order_ids = _uuid_values(args.order_id)
    interaction_ids = _uuid_values(args.interaction_id)
    import_job_ids = _uuid_values(args.import_job_id)
    model_versions = args.model_version

    if any(not version.startswith("e2e-") for version in model_versions):
        raise ValueError("Refusing to delete a model version without the e2e- prefix")

    async with AsyncSessionFactory() as session:
        async with session.begin():
            await session.execute(
                delete(OrderItemModel).where(OrderItemModel.order_id.in_(order_ids))
            )
            await session.execute(
                delete(OrderModel).where(OrderModel.id.in_(order_ids))
            )
            await session.execute(
                delete(CustomerInteractionModel).where(
                    CustomerInteractionModel.id.in_(interaction_ids)
                )
            )
            await session.execute(
                delete(ProductModel).where(ProductModel.id.in_(product_ids))
            )
            await session.execute(
                delete(CustomerModel).where(CustomerModel.id.in_(customer_ids))
            )
            await session.execute(
                delete(ImportJobModel).where(ImportJobModel.id.in_(import_job_ids))
            )
            await session.execute(
                delete(ModelRegistryModel).where(
                    ModelRegistryModel.version.in_(model_versions)
                )
            )

    storage_dir = Path(settings.MODEL_STORAGE_DIR).resolve()
    for version in model_versions:
        artifact = (storage_dir / f"{version}.json").resolve()
        if storage_dir not in artifact.parents:
            raise ValueError("Refusing to delete an artifact outside model storage")
        artifact.unlink(missing_ok=True)

    print(
        "Deleted explicitly identified E2E rows and artifacts: "
        f"{len(customer_ids)} customers, {len(product_ids)} products, "
        f"{len(order_ids)} orders, {len(import_job_ids)} import jobs, "
        f"{len(model_versions)} model versions."
    )


def main() -> None:
    args = _parser().parse_args()
    if not args.confirm:
        raise SystemExit("Refusing deletion without --confirm")
    asyncio.run(_cleanup(args))


if __name__ == "__main__":
    main()
