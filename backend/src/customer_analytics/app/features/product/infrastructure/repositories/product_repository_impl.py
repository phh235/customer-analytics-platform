"""Product repository implementation — SQLAlchemy implementation."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.product.domain.entities.product_entity import (
    ProductEntity,
)
from customer_analytics.app.features.product.infrastructure.models.product import (
    ProductModel,
)
from customer_analytics.app.shared.reference_codes import next_reference_code


class ProductRepositoryImpl:
    """Product repository using SQLAlchemy async session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: ProductModel) -> ProductEntity:
        return ProductEntity(
            product_code=model.product_code,
            id_=str(model.id),
            name=model.name,
            category=model.category,
            price=Decimal(str(model.price)),
            status=model.status,
            sku=model.sku,
            description=model.description,
            image_url=model.image_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: ProductEntity) -> ProductModel:
        return ProductModel(
            product_code=entity.product_code,
            id=entity.id_,
            name=entity.name,
            sku=entity.sku,
            category=entity.category,
            description=entity.description,
            image_url=entity.image_url,
            price=entity.price,
            status=entity.status,
        )

    async def create(self, entity: ProductEntity) -> ProductEntity:
        if entity.product_code is None:
            entity.product_code = await self.next_product_code()
        model = self._to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def next_product_code(self) -> str:
        """Generate the next product-facing reference code."""
        result = await self._session.execute(select(ProductModel.product_code))
        return next_reference_code("SP", list(result.scalars().all()))

    async def find_by_id(self, id_: str) -> ProductEntity | None:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == id_)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_by_name(self, name: str) -> ProductEntity | None:
        result = await self._session.execute(
            select(ProductModel).where(func.lower(ProductModel.name) == name.lower())
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
    ) -> list[ProductEntity]:
        stmt = select(ProductModel).order_by(ProductModel.created_at.desc())
        if category:
            stmt = stmt.where(ProductModel.category == category)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def find_page(
        self,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
    ) -> tuple[list[ProductEntity], int]:
        """Load one page and its total from a single database round-trip."""
        stmt = select(
            ProductModel,
            func.count().over().label("total"),
        ).order_by(ProductModel.created_at.desc())
        if category:
            stmt = stmt.where(ProductModel.category == category)
        result = await self._session.execute(stmt.offset(skip).limit(limit))
        rows = result.all()
        if not rows:
            return [], await self.count(category=category)
        return [self._to_entity(row[0]) for row in rows], int(rows[0][1])

    async def count(self, category: str | None = None) -> int:
        """Count products without loading full rows into memory."""
        stmt = select(func.count()).select_from(ProductModel)
        if category:
            stmt = stmt.where(ProductModel.category == category)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def find_related(
        self, category: str, exclude_id: str, limit: int = 4
    ) -> list[ProductEntity]:
        """Find related products in the same category."""
        stmt = (
            select(ProductModel)
            .where(
                ProductModel.category == category,
                ProductModel.id != exclude_id,
            )
            .order_by(ProductModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def update(self, entity: ProductEntity) -> ProductEntity:
        if entity.id_ is None:
            raise ValueError("Cannot update product without ID")
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == entity.id_)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Product with ID {entity.id_} not found")
        model.product_code = entity.product_code
        model.name = entity.name
        model.sku = entity.sku
        model.category = entity.category
        model.description = entity.description
        model.image_url = entity.image_url
        model.price = entity.price
        model.status = entity.status
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, id_: str) -> None:
        result = await self._session.execute(
            select(ProductModel).where(ProductModel.id == id_)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.flush()
