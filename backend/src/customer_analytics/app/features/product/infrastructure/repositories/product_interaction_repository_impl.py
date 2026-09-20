"""Persistence adapter for authenticated product-view events."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.identity.infrastructure.models.user import (
    UserModel,
)
from customer_analytics.app.features.product.infrastructure.models.product import (
    ProductModel,
)
from customer_analytics.app.features.reference_data.infrastructure.models import (
    CustomerInteractionModel,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.app.shared.reference_codes import next_reference_code


class ProductInteractionRepositoryImpl:
    """Persist product interaction events for a signed-in customer."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_product_view(
        self,
        product_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        email: str,
        full_name: str,
        customer_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        """Insert one product_view event and establish the account link."""
        product_result = await self._session.execute(
            select(ProductModel.id).where(
                ProductModel.id == product_id,
                ProductModel.is_deleted.is_(False),
                ProductModel.status == "ACTIVE",
            )
        )
        if product_result.scalar_one_or_none() is None:
            raise AppException(ErrorCode.NOT_FOUND, "Product not found")

        customer = None
        if customer_id is not None:
            customer_result = await self._session.execute(
                select(CustomerModel).where(
                    CustomerModel.id == customer_id,
                    CustomerModel.is_deleted.is_(False),
                )
            )
            customer = customer_result.scalar_one_or_none()
        if customer is None:
            customer_result = await self._session.execute(
                select(CustomerModel).where(
                    func.lower(CustomerModel.email) == email.lower(),
                    CustomerModel.is_deleted.is_(False),
                )
            )
            customer = customer_result.scalar_one_or_none()

        if customer is None:
            code_result = await self._session.execute(
                select(CustomerModel.customer_code)
            )
            customer = CustomerModel(
                customer_code=next_reference_code(
                    "KH", list(code_result.scalars().all())
                ),
                name=full_name[:100],
                email=email.lower(),
                status="ACTIVE",
                registered_at=datetime.now(UTC),
                customer_since=datetime.now(UTC),
            )
            self._session.add(customer)
            await self._session.flush()

        if customer_id != customer.id:
            await self._session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(customer_id=customer.id)
            )
            await self._session.flush()

        event_id = uuid.uuid4()
        self._session.add(
            CustomerInteractionModel(
                id=event_id,
                interaction_code=f"WEB_VIEW_{event_id}",
                customer_id=customer.id,
                product_id=product_id,
                interaction_type="product_view",
                interaction_timestamp=datetime.now(UTC),
                channel="web",
                interaction_value=Decimal("0"),
                is_mock_data=False,
            )
        )
        await self._session.flush()
        return event_id

