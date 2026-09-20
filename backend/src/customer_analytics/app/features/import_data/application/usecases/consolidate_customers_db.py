"""DB-backed customer consolidation use case.

Reads customers/orders from the database, normalizes contact fields,
detects duplicates, links order statistics, and (optionally) persists
the merged result back to customer records.
"""

from __future__ import annotations

from abc import abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any

import structlog

from customer_analytics.app.features.customer.domain.repositories import (
    customer_unit_of_work,
)
from customer_analytics.app.features.import_data.application.services import (
    consolidation_service,
)
from customer_analytics.core.use_cases.use_case import BaseUseCase

logger = structlog.get_logger(__name__)

_PAGE_SIZE = 100


class DuplicateGroup:
    """A detected duplicate-customer group."""

    def __init__(
        self,
        dedup_key: str,
        primary_id: str | None,
        duplicate_ids: list[str],
        fields_filled: list[str],
    ):
        self.dedup_key = dedup_key
        self.primary_id = primary_id
        self.duplicate_ids = duplicate_ids
        self.fields_filled = fields_filled

    def to_dict(self) -> dict[str, Any]:
        return {
            "dedup_key": self.dedup_key,
            "primary_customer_id": self.primary_id,
            "duplicate_customer_ids": self.duplicate_ids,
            "fields_filled": self.fields_filled,
        }


class ConsolidationRunResult:
    """Summary of a DB-backed consolidation run."""

    def __init__(
        self,
        applied: bool,
        customers_scanned: int,
        duplicates_found: int,
        customers_normalized: int,
        stats_updated: int,
        groups: list[DuplicateGroup] | None = None,
    ):
        self.applied = applied
        self.customers_scanned = customers_scanned
        self.duplicates_found = duplicates_found
        self.customers_normalized = customers_normalized
        self.stats_updated = stats_updated
        self.groups = groups or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "applied": self.applied,
            "customers_scanned": self.customers_scanned,
            "duplicates_found": self.duplicates_found,
            "customers_normalized": self.customers_normalized,
            "stats_updated": self.stats_updated,
            "duplicate_groups": [g.to_dict() for g in self.groups],
        }


class ConsolidateCustomersDbUseCase(BaseUseCase[bool, ConsolidationRunResult]):
    """Consolidate database customer data use case interface.

    Args is ``apply``: False returns a dry-run report, True persists changes.
    """

    unit_of_work: customer_unit_of_work.CustomerUnitOfWork

    @abstractmethod
    async def __call__(self, args: bool) -> ConsolidationRunResult:
        raise NotImplementedError()


class ConsolidateCustomersDbUseCaseImpl(ConsolidateCustomersDbUseCase):
    """Consolidate database customer data use case implementation."""

    def __init__(
        self,
        customer_unit_of_work: customer_unit_of_work.CustomerUnitOfWork,
        order_repository: Any = None,
    ):
        self.unit_of_work = customer_unit_of_work
        self.order_repository = order_repository

    async def __call__(self, args: bool) -> ConsolidationRunResult:
        apply_changes = args

        customers = await self._fetch_all_customers()
        entities = {c.id_: c for c in customers if c.id_}

        # 1. Normalize contact fields
        normalized: dict[str, dict[str, str | None]] = {}
        for entity in customers:
            if not entity.id_:
                continue
            normalized[entity.id_] = {
                "email": consolidation_service.normalize_email(entity.email),
                "phone": consolidation_service.normalize_phone(entity.phone),
                "name": consolidation_service.normalize_name(entity.name),
            }

        # 2. Detect duplicate groups by email > phone > name+dob
        groups_map: dict[str, list[str]] = {}
        for entity in customers:
            if not entity.id_:
                continue
            key = self._dedup_key(entity, normalized[entity.id_])
            groups_map.setdefault(key, []).append(entity.id_)

        duplicate_groups: list[DuplicateGroup] = []
        for key, ids in groups_map.items():
            if len(ids) < 2:
                continue
            primary_id = min(
                ids,
                key=lambda cid: (
                    entities[cid].created_at or datetime.max.replace(tzinfo=None)
                ),
            )
            filled = self._merge_group_fields(entities, primary_id, ids)
            duplicate_groups.append(
                DuplicateGroup(
                    dedup_key=key.split(":", 1)[0] + ":" + key[key.index("|") + 1 :],
                    primary_id=primary_id,
                    duplicate_ids=[i for i in ids if i != primary_id],
                    fields_filled=filled,
                )
            )

        # 3. Compute per-customer diffs
        normalize_count = 0
        stats_count = 0
        pending_updates: list[Any] = []

        for entity in customers:
            if not entity.id_:
                continue
            new_values = normalized[entity.id_]
            changed_fields = {
                field: value
                for field, value in new_values.items()
                if value and getattr(entity, field) != value
            }
            if changed_fields:
                normalize_count += 1
                pending_updates.append(entity.update(**changed_fields))

            stats = await self._customer_stats(entity.id_)
            if stats is not None and self._stats_differ(entity, stats):
                stats_count += 1
                pending_updates.append(
                    entity.update_stats(
                        total_orders=int(stats["total_orders"]),
                        total_spent=Decimal(str(stats["total_spent"])),
                        avg_order_value=Decimal(str(stats["avg_order_value"])),
                        last_purchase_date=stats.get("last_purchase_date"),
                    )
                )

        # 4. Merge duplicate groups into their primary record
        for group in duplicate_groups:
            if group.primary_id is None:
                continue
            primary = entities[group.primary_id]
            merged_updates: dict[str, Any] = {}
            for dup_id in group.duplicate_ids:
                dup = entities[dup_id]
                for field in ("email", "phone", "address", "gender", "region"):
                    if getattr(primary, field) is None and getattr(dup, field):
                        merged_updates[field] = getattr(dup, field)
            # Deactivate merged duplicates instead of deleting history
            for dup_id in group.duplicate_ids:
                dup = entities[dup_id]
                if dup.status == "ACTIVE":
                    merged = dup.update(status="INACTIVE")
                    if apply_changes:
                        await self.unit_of_work.repository.update(merged)

            if merged_updates:
                group.fields_filled.extend(sorted(merged_updates.keys()))
                pending_updates.append(primary.update(**merged_updates))

        # 5. Persist when applying
        if apply_changes:
            for updated in pending_updates:
                await self.unit_of_work.repository.update(updated)
            await self.unit_of_work.commit()

        result = ConsolidationRunResult(
            applied=apply_changes,
            customers_scanned=len(customers),
            duplicates_found=len(duplicate_groups),
            customers_normalized=normalize_count,
            stats_updated=stats_count,
            groups=duplicate_groups,
        )

        logger.info(
            "consolidation_db_run",
            applied=apply_changes,
            scanned=result.customers_scanned,
            duplicates=result.duplicates_found,
            normalized=result.customers_normalized,
            stats_updated=result.stats_updated,
        )
        return result

    async def _fetch_all_customers(self) -> list[Any]:
        """Fetch every customer using paginated find_all."""
        customers: list[Any] = []
        skip = 0
        while True:
            page = await self.unit_of_work.repository.find_all(
                skip=skip, limit=_PAGE_SIZE
            )
            customers.extend(page)
            if len(page) < _PAGE_SIZE:
                return customers
            skip += _PAGE_SIZE

    async def _customer_stats(self, customer_id: str) -> dict[str, Any] | None:
        if self.order_repository is None:
            return None
        return await self.order_repository.get_customer_stats(customer_id)

    @staticmethod
    def _dedup_key(entity: Any, values: dict[str, str | None]) -> str:
        email = values.get("email")
        phone = values.get("phone")
        name = (values.get("name") or "").lower().strip()
        dob = str(entity.date_of_birth or "")
        if email:
            return f"email|{email}"
        if phone:
            return f"phone|{phone}"
        if name:
            return f"name|{name}|{dob}"
        return f"id|{entity.id_}"

    @staticmethod
    def _merge_group_fields(
        entities: dict[str, Any], primary_id: str, group_ids: list[str]
    ) -> list[str]:
        """Record which fields the merge can fill on the primary record."""
        primary = entities[primary_id]
        filled: set[str] = set()
        for other_id in group_ids:
            if other_id == primary_id:
                continue
            other = entities[other_id]
            for field in ("email", "phone", "address", "gender", "region"):
                if getattr(primary, field) is None and getattr(other, field):
                    filled.add(field)
        return sorted(filled)

    @staticmethod
    def _stats_differ(entity: Any, stats: dict[str, Any]) -> bool:
        stored_orders = int(entity.total_orders or 0)
        stored_spent = Decimal(str(entity.total_spent or 0))
        return stored_orders != int(stats["total_orders"]) or stored_spent != Decimal(
            str(stats["total_spent"])
        )
