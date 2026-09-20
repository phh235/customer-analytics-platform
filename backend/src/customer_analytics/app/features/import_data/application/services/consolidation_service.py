"""Customer consolidation service — Merge and deduplicate customer data."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ConsolidatedCustomer:
    """Consolidated customer data."""

    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str | None = None,
        phone: str | None = None,
        address: str | None = None,
        gender: str | None = None,
        date_of_birth: Any = None,
        region: str | None = None,
        customer_since: datetime | None = None,
        total_orders: int = 0,
        total_spent: Decimal = Decimal("0"),
        avg_order_value: Decimal = Decimal("0"),
        last_purchase_date: datetime | None = None,
        order_ids: list[str] | None = None,
        sources: list[str] | None = None,
    ):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.gender = gender
        self.date_of_birth = date_of_birth
        self.region = region
        self.customer_since = customer_since
        self.total_orders = total_orders
        self.total_spent = total_spent
        self.avg_order_value = avg_order_value
        self.last_purchase_date = last_purchase_date
        self.order_ids = order_ids or []
        self.sources = sources or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "region": self.region,
            "customer_since": self.customer_since,
            "total_orders": self.total_orders,
            "total_spent": float(self.total_spent),
            "avg_order_value": float(self.avg_order_value),
            "last_purchase_date": self.last_purchase_date,
            "order_ids": self.order_ids,
            "sources": self.sources,
        }


class ConsolidationResult:
    """Result of customer consolidation."""

    def __init__(
        self,
        total_customers: int,
        consolidated_customers: int,
        duplicates_found: int,
        orders_linked: int,
        customers: list[ConsolidatedCustomer] | None = None,
    ):
        self.total_customers = total_customers
        self.consolidated_customers = consolidated_customers
        self.duplicates_found = duplicates_found
        self.orders_linked = orders_linked
        self.customers = customers or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_customers": self.total_customers,
            "consolidated_customers": self.consolidated_customers,
            "duplicates_found": self.duplicates_found,
            "orders_linked": self.orders_linked,
            "customers": [c.to_dict() for c in self.customers],
        }


def normalize_email(email: str | None) -> str | None:
    """Normalize email address.

    - Lowercase
    - Strip whitespace
    - Remove dots in Gmail local part
    """
    if not email:
        return None

    email = email.strip().lower()

    # Gmail: remove dots from local part
    if "@" in email:
        local, domain = email.rsplit("@", 1)
        if domain in ("gmail.com", "googlemail.com"):
            local = local.replace(".", "")
            email = f"{local}@{domain}"

    return email


def normalize_phone(phone: str | None) -> str | None:
    """Normalize phone number.

    - Remove spaces, dashes, dots
    - Ensure starts with 0
    """
    if not phone:
        return None

    # Remove common separators
    cleaned = re.sub(r"[\s\-\.\(\)]", "", phone.strip())

    # Ensure starts with 0
    if not cleaned.startswith("0") and len(cleaned) >= 10:
        cleaned = "0" + cleaned

    return cleaned


def normalize_name(name: str | None) -> str | None:
    """Normalize customer name.

    - Strip whitespace
    - Normalize multiple spaces
    """
    if not name:
        return None

    # Strip and normalize spaces
    cleaned = " ".join(name.strip().split())
    return cleaned


class CustomerConsolidationService:
    """Service for consolidating customer data."""

    def __init__(self, customer_repository, order_repository=None):
        self.customer_repository = customer_repository
        self.order_repository = order_repository

    async def consolidate(
        self,
        customers: list[dict[str, Any]],
        orders: list[dict[str, Any]] | None = None,
    ) -> ConsolidationResult:
        """Consolidate customer data from multiple sources.

        Args:
            customers: List of customer records
            orders: Optional list of order records to link

        Returns:
            ConsolidationResult with consolidated customers
        """
        logger.info(
            "customer_consolidation_started",
            customer_count=len(customers),
            order_count=len(orders) if orders else 0,
        )

        # Step 1: Normalize customer data
        normalized_customers = []
        for customer in customers:
            normalized = self._normalize_customer(customer)
            normalized_customers.append(normalized)

        # Step 2: Detect duplicates
        customer_map, duplicates_found = self._detect_duplicates(normalized_customers)

        # Step 3: Link orders to customers
        orders_linked = 0
        if orders:
            orders_linked = self._link_orders(customer_map, orders)

        # Step 4: Calculate aggregated statistics
        consolidated_customers = []
        for _customer_id, customer_data in customer_map.items():
            consolidated = self._aggregate_customer_data(customer_data)
            consolidated_customers.append(consolidated)

        result = ConsolidationResult(
            total_customers=len(customers),
            consolidated_customers=len(consolidated_customers),
            duplicates_found=duplicates_found,
            orders_linked=orders_linked,
            customers=consolidated_customers,
        )

        logger.info(
            "customer_consolidation_completed",
            total_customers=result.total_customers,
            consolidated_customers=result.consolidated_customers,
            duplicates_found=result.duplicates_found,
            orders_linked=result.orders_linked,
        )

        return result

    def _normalize_customer(self, customer: dict[str, Any]) -> dict[str, Any]:
        """Normalize a single customer record."""
        normalized = customer.copy()

        # Normalize email
        if "email" in normalized:
            normalized["email"] = normalize_email(normalized["email"])

        # Normalize phone
        if "phone" in normalized:
            normalized["phone"] = normalize_phone(normalized["phone"])

        # Normalize name
        if "name" in normalized:
            normalized["name"] = normalize_name(normalized["name"])

        return normalized

    def _detect_duplicates(
        self,
        customers: list[dict[str, Any]],
    ) -> tuple[dict[str, list[dict[str, Any]]], int]:
        """Detect and merge duplicate customers.

        Returns:
            Tuple of (customer_map, duplicates_found)
        """
        customer_map: dict[str, list[dict[str, Any]]] = {}
        duplicates_found = 0

        for customer in customers:
            # Generate dedup key based on email, phone, or name+dob
            dedup_key = self._generate_dedup_key(customer)

            if dedup_key in customer_map:
                customer_map[dedup_key].append(customer)
                duplicates_found += 1
            else:
                customer_map[dedup_key] = [customer]

        return customer_map, duplicates_found

    def _generate_dedup_key(self, customer: dict[str, Any]) -> str:
        """Generate a deduplication key for a customer.

        Priority: email > phone > name+dob
        """
        # Try email first
        email = customer.get("email")
        if email:
            return f"email:{email.lower().strip()}"

        # Try phone
        phone = customer.get("phone")
        if phone:
            normalized_phone = normalize_phone(phone)
            if normalized_phone:
                return f"phone:{normalized_phone}"

        # Fallback to name + date_of_birth
        name = customer.get("name", "").lower().strip()
        dob = customer.get("date_of_birth", "")
        if name:
            return f"name:{name}:{dob}"

        # Last resort: use customer_id if provided
        customer_id = customer.get("customer_id")
        if customer_id:
            return f"id:{customer_id}"

        # Generate a key from all available data
        return f"hash:{hash(str(sorted(customer.items())))}"

    def _link_orders(
        self,
        customer_map: dict[str, list[dict[str, Any]]],
        orders: list[dict[str, Any]],
    ) -> int:
        """Link orders to customers."""
        orders_linked = 0

        # Build customer_id to dedup_key mapping
        id_to_key: dict[str, str] = {}
        for dedup_key, records in customer_map.items():
            for record in records:
                customer_id = record.get("customer_id")
                if customer_id:
                    id_to_key[str(customer_id)] = dedup_key

        # Link orders
        for order in orders:
            customer_id = str(order.get("customer_id", ""))
            if customer_id in id_to_key:
                dedup_key = id_to_key[customer_id]
                # Add order to first record with this customer_id
                for record in customer_map[dedup_key]:
                    if str(record.get("customer_id")) == customer_id:
                        if "_linked_orders" not in record:
                            record["_linked_orders"] = []
                        record["_linked_orders"].append(order)
                        orders_linked += 1
                        break

        return orders_linked

    def _aggregate_customer_data(
        self,
        records: list[dict[str, Any]],
    ) -> ConsolidatedCustomer:
        """Aggregate multiple customer records into one."""
        if not records:
            raise ValueError("No records to aggregate")

        # Use the most complete record as base
        base = max(records, key=lambda r: sum(1 for v in r.values() if v))

        # Get customer_id from any record
        customer_id = ""
        for record in records:
            if record.get("customer_id"):
                customer_id = str(record["customer_id"])
                break

        # Aggregate order data
        all_orders = []
        for record in records:
            all_orders.extend(record.get("_linked_orders", []))

        total_orders = len(all_orders)
        total_spent = Decimal("0")
        last_purchase_date = None

        if all_orders:
            for order in all_orders:
                amount = order.get("total_amount", 0)
                total_spent += Decimal(str(amount))

                order_date = order.get("order_date")
                if order_date:
                    if isinstance(order_date, str):
                        try:
                            order_date = datetime.fromisoformat(order_date)
                        except ValueError:
                            pass
                    if isinstance(order_date, datetime):
                        if (
                            last_purchase_date is None
                            or order_date > last_purchase_date
                        ):
                            last_purchase_date = order_date

        avg_order_value = (
            total_spent / total_orders if total_orders > 0 else Decimal("0")
        )

        return ConsolidatedCustomer(
            customer_id=customer_id,
            name=base.get("name", ""),
            email=base.get("email"),
            phone=base.get("phone"),
            address=base.get("address"),
            gender=base.get("gender"),
            date_of_birth=base.get("date_of_birth"),
            region=base.get("region"),
            customer_since=base.get("customer_since"),
            total_orders=total_orders,
            total_spent=total_spent,
            avg_order_value=avg_order_value,
            last_purchase_date=last_purchase_date,
            order_ids=[str(o.get("order_id")) for o in all_orders if o.get("order_id")],
            sources=[f"record_{i}" for i in range(len(records))],
        )
