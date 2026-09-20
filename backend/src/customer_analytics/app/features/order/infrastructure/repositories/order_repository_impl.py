"""Order repository implementation — SQLAlchemy implementation."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.features.order.domain.entities.order_entity import (
    OrderEntity,
    OrderItemEntity,
)
from customer_analytics.app.features.order.domain.repositories.order_repository import (
    OrderRepository,
)
from customer_analytics.app.features.order.infrastructure.models.order import (
    OrderItemModel,
    OrderModel,
)


class OrderRepositoryImpl(OrderRepository):
    """Order repository using SQLAlchemy async session."""

    def __init__(
        self,
        session: AsyncSession,
        current_user: UserEntity | None = None,
    ) -> None:
        self._session = session
        self._current_user = current_user

    def _scope_conditions(self) -> tuple[Any, ...]:
        """Return SQLAlchemy predicates for the authenticated order scope."""
        user = self._current_user
        if user is None or user.role_code == "ADMIN":
            return ()
        return (
            CustomerModel.assigned_user_id
            == (uuid.UUID(user.id_) if user.id_ else None),
        )

    def _order_list_conditions(
        self,
        customer_id: str | None,
        status: str | None,
        search: str | None,
    ) -> tuple[Any, ...]:
        """Build shared scope and search predicates for order list queries."""
        conditions = list(self._scope_conditions())
        if customer_id:
            conditions.append(OrderModel.customer_id == customer_id)
        if status:
            conditions.append(OrderModel.status == status)
        if search and search.strip():
            pattern = f"%{search.strip()}%"
            conditions.append(
                or_(
                    OrderModel.order_number.ilike(pattern),
                    CustomerModel.name.ilike(pattern),
                    CustomerModel.customer_code.ilike(pattern),
                    CustomerModel.email.ilike(pattern),
                    CustomerModel.phone.ilike(pattern),
                )
            )
        return tuple(conditions)

    def _to_entity(self, model: OrderModel) -> OrderEntity:
        items = [
            OrderItemEntity(
                id_=str(item.id),
                order_id=str(item.order_id),
                product_id=str(item.product_id),
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=Decimal(str(item.subtotal)),
            )
            for item in model.items
        ]
        return OrderEntity(
            id_=str(model.id),
            customer_id=str(model.customer_id),
            order_number=model.order_number,
            order_date=model.order_date,
            total_amount=Decimal(str(model.total_amount)),
            refund_amount=Decimal(str(model.refund_amount)),
            status=model.status,
            channel=model.channel,
            notes=model.notes,
            items=items,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: OrderEntity) -> OrderModel:
        return OrderModel(
            id=entity.id_,
            customer_id=entity.customer_id,
            order_number=entity.order_number,
            order_date=entity.order_date,
            total_amount=entity.total_amount,
            refund_amount=entity.refund_amount,
            net_amount=entity.net_amount,
            status=entity.status,
            channel=entity.channel,
            notes=entity.notes,
        )

    async def create(self, entity: OrderEntity) -> OrderEntity:
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()

        # Create order items
        for item in entity.items:
            item_model = OrderItemModel(
                order_id=model.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            self._session.add(item_model)

        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_by_id(self, id_: str) -> OrderEntity | None:
        stmt = (
            select(OrderModel)
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == id_, *self._scope_conditions())
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_customer_id(
        self, customer_id: str, skip: int = 0, limit: int = 100
    ) -> list[OrderEntity]:
        stmt = (
            select(OrderModel)
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .options(selectinload(OrderModel.items))
            .where(
                OrderModel.customer_id == customer_id,
                *self._scope_conditions(),
            )
            .order_by(OrderModel.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_by_order_number(self, order_number: str) -> OrderEntity | None:
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.order_number == order_number)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def count_by_customer_id(self, customer_id: str) -> int:
        stmt = (
            select(func.count())
            .select_from(OrderModel)
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .where(
                OrderModel.customer_id == customer_id,
                *self._scope_conditions(),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_customer_stats(
        self, customer_id: str
    ) -> dict[str, int | float] | None:
        """Get aggregated stats for a customer."""
        stmt = (
            select(
                func.count(OrderModel.id).label("total_orders"),
                func.coalesce(func.sum(OrderModel.net_amount), 0).label("total_spent"),
                func.coalesce(func.avg(OrderModel.net_amount), 0).label(
                    "avg_order_value"
                ),
                func.max(OrderModel.order_date).label("last_purchase_date"),
            )
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .where(
                OrderModel.customer_id == customer_id,
                OrderModel.status == "COMPLETED",
                *self._scope_conditions(),
            )
        )
        result = await self._session.execute(stmt)
        row = result.one_or_none()
        if row is None or row.total_orders == 0:
            return None

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        customer_id: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> list[OrderEntity]:
        stmt = (
            select(OrderModel)
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .options(selectinload(OrderModel.items))
            .where(*self._order_list_conditions(customer_id, status, search))
            .order_by(OrderModel.order_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def update(self, entity: OrderEntity) -> OrderEntity:
        if entity.id_ is None:
            raise ValueError("Cannot update order without ID")
        result = await self._session.execute(
            select(OrderModel)
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == entity.id_, *self._scope_conditions())
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Order with ID {entity.id_} not found")
        model.status = entity.status
        model.refund_amount = entity.refund_amount
        model.net_amount = entity.net_amount
        model.notes = entity.notes
        existing_item_ids = {item.id for item in model.items}
        for item in entity.items:
            if item.id_ is not None and uuid.UUID(item.id_) in existing_item_ids:
                continue
            self._session.add(
                OrderItemModel(
                    order_id=model.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.subtotal,
                )
            )
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id_: str) -> None:
        result = await self._session.execute(
            select(OrderModel)
            .join(CustomerModel, CustomerModel.id == OrderModel.customer_id)
            .where(OrderModel.id == id_, *self._scope_conditions())
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
