"""Focused tests for authenticated product-view event recording."""

from __future__ import annotations

import uuid

import pytest

from customer_analytics.app.features.product.infrastructure.repositories.product_interaction_repository_impl import (  # noqa: E501
    ProductInteractionRepositoryImpl,
)


class _ScalarResult:
    def __init__(self, value: object) -> None:
        self._value = value
    def scalar_one_or_none(self) -> object:
        return self._value


    def scalars(self) -> _ScalarResult:
        return self

    def all(self) -> list[object]:
        return self._value if isinstance(self._value, list) else []


class _Customer:
    def __init__(self, customer_id: uuid.UUID) -> None:
        self.id = customer_id


class _Session:
    def __init__(self, values: list[object]) -> None:
        self._values = iter(values)
        self.added: list[object] = []

    async def execute(self, _statement: object) -> _ScalarResult:
        try:
            value = next(self._values)
        except StopIteration:
            value = None
        return _ScalarResult(value)

    def add(self, value: object) -> None:
        if getattr(value, "id", None) is None:
            value.id = uuid.uuid4()
        self.added.append(value)

    async def flush(self) -> None:
        return None


@pytest.mark.asyncio
async def test_record_product_view_persists_product_view_event() -> None:
    product_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    session = _Session([product_id, _Customer(customer_id)])

    event_id = await ProductInteractionRepositoryImpl(session).record_product_view(
        product_id,
        user_id=uuid.uuid4(),
        email="customer@example.com",
        full_name="Customer",
        customer_id=customer_id,
    )

    assert event_id
    assert len(session.added) == 1
    event = session.added[0]
    assert event.interaction_type == "product_view"
    assert event.product_id == product_id
    assert event.customer_id == customer_id
    assert event.channel == "web"
    assert event.is_mock_data is False


@pytest.mark.asyncio
async def test_record_product_view_provisions_unlinked_account() -> None:
    session = _Session([uuid.uuid4(), None, []])

    await ProductInteractionRepositoryImpl(session).record_product_view(
        uuid.uuid4(),
        user_id=uuid.uuid4(),
        email="new-customer@example.com",
        full_name="New Customer",
    )

    assert len(session.added) == 2
    assert session.added[0].customer_code == "KH-000001"
    assert session.added[0].email == "new-customer@example.com"
    assert session.added[1].interaction_type == "product_view"
    assert session.added[1].customer_id == session.added[0].id
