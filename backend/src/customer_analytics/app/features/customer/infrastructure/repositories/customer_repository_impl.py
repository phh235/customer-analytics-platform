"""Customer repository implementation — SQLAlchemy implementation."""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.customer.domain.entities.customer_entity import (
    CustomerEntity,
)
from customer_analytics.app.features.customer.domain.repositories.customer_repository import (  # noqa: E501
    CustomerRepository,
)
from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.identity.domain.entities.user_entity import (
    UserEntity,
)
from customer_analytics.app.shared.reference_codes import next_reference_code


class CustomerRepositoryImpl(CustomerRepository):
    """Customer repository using SQLAlchemy async session."""

    def __init__(
        self,
        session: AsyncSession,
        current_user: UserEntity | None = None,
    ) -> None:
        self._session = session
        self._current_user = current_user

    def _scope_clause(self):
        """Return the row scope for the authenticated user."""
        if self._current_user is None or self._current_user.role_code == "ADMIN":
            return None
        user_id = self._current_user.id_
        if user_id is None:
            return CustomerModel.id.is_(None)
        return CustomerModel.assigned_user_id == uuid.UUID(user_id)

    def _scoped(self, stmt):
        """Apply authenticated data scope to a customer query."""
        clause = self._scope_clause()
        return stmt.where(clause) if clause is not None else stmt

    async def _to_entity(self, model: CustomerModel) -> CustomerEntity:
        """Convert database model to domain entity."""
        return CustomerEntity(
            customer_code=model.customer_code,
            id_=str(model.id),
            name=model.name,
            image_url=model.image_url,
            email=model.email,
            phone=model.phone,
            address=model.address,
            status=model.status,
            gender=model.gender,
            date_of_birth=model.date_of_birth,
            region=model.region,
            customer_since=model.customer_since,
            assigned_user_id=(
                str(model.assigned_user_id) if model.assigned_user_id else None
            ),
            team_id=str(model.team_id) if model.team_id else None,
            total_orders=model.total_orders,
            total_spent=Decimal(str(model.total_spent)),
            avg_order_value=Decimal(str(model.avg_order_value)),
            last_purchase_date=model.last_purchase_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: CustomerEntity) -> CustomerModel:
        """Convert domain entity to database model."""
        current_user = self._current_user
        assigned_user_id = entity.assigned_user_id
        team_id = entity.team_id
        if current_user is not None and current_user.role_code != "ADMIN":
            assigned_user_id = assigned_user_id or current_user.id_
        if current_user is not None:
            team_id = team_id or current_user.team_id
        return CustomerModel(
            customer_code=entity.customer_code,
            id=entity.id_,
            name=entity.name,
            image_url=entity.image_url,
            email=entity.email,
            phone=entity.phone,
            address=entity.address,
            status=entity.status,
            gender=entity.gender,
            date_of_birth=entity.date_of_birth,
            region=entity.region,
            customer_since=entity.customer_since,
            assigned_user_id=(
                uuid.UUID(assigned_user_id) if assigned_user_id else None
            ),
            team_id=uuid.UUID(team_id) if team_id else None,
            total_orders=entity.total_orders,
            total_spent=entity.total_spent,
            avg_order_value=entity.avg_order_value,
            last_purchase_date=entity.last_purchase_date,
        )

    async def next_customer_code(self) -> str:
        """Generate the next customer-facing reference code."""
        result = await self._session.execute(select(CustomerModel.customer_code))
        return next_reference_code("KH", list(result.scalars().all()))


    async def create(self, entity: CustomerEntity) -> CustomerEntity:
        """Create a new customer."""
        if entity.customer_code is None:
            entity.customer_code = await self.next_customer_code()
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return await self._to_entity(model)

    async def find_by_id(self, id_: str) -> CustomerEntity | None:
        """Find a customer by ID."""
        result = await self._session.execute(
            self._scoped(select(CustomerModel).where(CustomerModel.id == id_))
        )
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model else None

    async def find_by_email(self, email: str) -> CustomerEntity | None:
        """Find a customer by email."""
        result = await self._session.execute(
            select(CustomerModel).where(
                func.lower(CustomerModel.email) == email.lower()
            )
        )
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model else None

    async def find_by_phone(self, phone: str) -> CustomerEntity | None:
        """Find a customer by phone."""
        result = await self._session.execute(
            select(CustomerModel).where(CustomerModel.phone == phone)
        )
        model = result.scalar_one_or_none()
        return await self._to_entity(model) if model else None

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        status: str | None = None,
        region: str | None = None,
    ) -> list[CustomerEntity]:
        """Find all customers with pagination, search, and filters."""
        stmt = self._scoped(
            select(CustomerModel).order_by(CustomerModel.created_at.desc())
        )

        if search:
            stmt = stmt.where(
                func.lower(CustomerModel.name).contains(search.lower())
                | func.lower(CustomerModel.email).contains(search.lower())
                | CustomerModel.phone.contains(search)
            )

        if status:
            stmt = stmt.where(CustomerModel.status == status)

        if region:
            stmt = stmt.where(CustomerModel.region == region)

        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [await self._to_entity(m) for m in models]

    async def count_customers(
        self,
        search: str | None = None,
        status: str | None = None,
        region: str | None = None,
    ) -> int:
        """Count total customers with filters."""
        stmt = self._scoped(select(func.count()).select_from(CustomerModel))

        if search:
            stmt = stmt.where(
                func.lower(CustomerModel.name).contains(search.lower())
                | func.lower(CustomerModel.email).contains(search.lower())
                | CustomerModel.phone.contains(search)
            )

        if status:
            stmt = stmt.where(CustomerModel.status == status)

        if region:
            stmt = stmt.where(CustomerModel.region == region)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update(self, entity: CustomerEntity) -> CustomerEntity:
        """Update an existing customer."""
        if entity.id_ is None:
            raise ValueError("Cannot update customer without ID")

        result = await self._session.execute(
            self._scoped(select(CustomerModel).where(CustomerModel.id == entity.id_))
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Customer with ID {entity.id_} not found")
        model.name = entity.name
        model.customer_code = entity.customer_code
        model.image_url = entity.image_url
        model.email = entity.email
        model.phone = entity.phone
        model.address = entity.address
        model.status = entity.status
        model.gender = entity.gender
        model.date_of_birth = entity.date_of_birth
        model.assigned_user_id = (
            uuid.UUID(entity.assigned_user_id) if entity.assigned_user_id else None
        )
        model.team_id = uuid.UUID(entity.team_id) if entity.team_id else None
        model.region = entity.region
        model.customer_since = entity.customer_since
        model.total_orders = entity.total_orders
        model.total_spent = entity.total_spent
        model.avg_order_value = entity.avg_order_value
        model.last_purchase_date = entity.last_purchase_date

        await self._session.flush()
        await self._session.refresh(model)
        return await self._to_entity(model)

    async def delete(self, id_: str) -> None:
        """Delete a customer (hard delete)."""
        result = await self._session.execute(
            self._scoped(select(CustomerModel).where(CustomerModel.id == id_))
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
