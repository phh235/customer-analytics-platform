"""Persistence adapter for imported customer interactions."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.reference_data.infrastructure.models import (
    CustomerInteractionModel,
)


class CustomerInteractionRepositoryImpl:
    """Persist customer interaction rows during an import transaction."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, row: dict[str, Any]) -> None:
        """Insert one validated interaction row."""
        self._session.add(
            CustomerInteractionModel(
                id=uuid.UUID(str(row["id"])),
                interaction_code=row.get("interaction_code"),
                customer_id=uuid.UUID(str(row["customer_id"])),
                product_id=uuid.UUID(str(row["product_id"])),
                campaign_id=(
                    uuid.UUID(str(row["campaign_id"]))
                    if row.get("campaign_id")
                    else None
                ),
                interaction_type=str(row["interaction_type"]),
                interaction_timestamp=row["interaction_timestamp"],
                channel=row.get("channel"),
                session_id=row.get("session_id"),
                interaction_value=Decimal(str(row.get("interaction_value", 0))),
                interaction_result=row.get("interaction_result"),
                is_mock_data=bool(row.get("is_mock_data", False)),
            )
        )
        await self._session.flush()
