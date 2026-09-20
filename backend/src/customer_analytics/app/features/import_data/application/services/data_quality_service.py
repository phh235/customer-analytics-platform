"""Data quality service — Orchestrate validation for imported data."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from customer_analytics.app.features.import_data.application.services.validators import (  # noqa: E501
    check_duplicates,
    validate_date,
    validate_email,
    validate_foreign_key,
    validate_numeric,
    validate_phone,
    validate_required_fields,
    validate_status,
)
from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportError,
)

# ── Field definitions per import type ──────────────────────

CUSTOMER_FIELDS = {
    "required": ["name"],
    "optional": [
        "customer_id",
        "email",
        "phone",
        "gender",
        "date_of_birth",
        "region",
        "address",
        "customer_since",
    ],
    "unique_keys": ["customer_id"],
    "email_fields": ["email"],
    "phone_fields": ["phone"],
    "date_fields": ["date_of_birth", "customer_since"],
}

ORDER_FIELDS = {
    "required": ["order_id", "customer_id", "order_date", "total_amount"],
    "optional": ["status", "channel", "refund_amount"],
    "unique_keys": ["order_id"],
    "date_fields": ["order_date"],
    "numeric_fields": ["total_amount", "refund_amount"],
    "status_fields": {
        "status": [
            "PAID",
            "COMPLETED",
            "DELIVERED",
            "PARTIAL_REFUNDED",
            "CANCELLED",
            "FAILED",
            "REFUNDED",
        ]
    },
}
ORDER_DETAIL_FIELDS = {
    "required": ["order_id", "product_id", "quantity", "unit_price"],
    "optional": ["subtotal"],
    "numeric_fields": ["quantity", "unit_price", "subtotal"],
}
INTERACTION_FIELDS = {
    "required": [
        "interaction_id",
        "customer_id",
        "product_id",
        "interaction_type",
        "interaction_timestamp",
    ],
    "optional": [
        "campaign_id",
        "channel",
        "session_id",
        "interaction_value",
        "interaction_result",
        "is_mock_data",
    ],
    "unique_keys": ["interaction_id"],
    "date_fields": ["interaction_timestamp"],
    "numeric_fields": ["interaction_value"],
}


PRODUCT_FIELDS = {
    "required": ["name", "category", "price"],
    "optional": ["product_id", "status"],
    "unique_keys": ["product_id"],
    "numeric_fields": ["price"],
    "status_fields": {"status": ["ACTIVE", "INACTIVE"]},
}

IMPORT_TYPE_FIELDS = {
    "CUSTOMER": CUSTOMER_FIELDS,
    "ORDER": ORDER_FIELDS,
    "ORDER_DETAIL": ORDER_DETAIL_FIELDS,
    "PRODUCT": PRODUCT_FIELDS,
    "INTERACTION": INTERACTION_FIELDS,
}


def validate_refund_amount(
    row: dict[str, Any],
    row_number: int,
) -> list[ImportError]:
    """Reject refunds greater than the imported order total."""
    total_value = row.get("total_amount")
    refund_value = row.get("refund_amount", 0)
    if total_value in (None, "") or refund_value in (None, ""):
        return []
    try:
        if Decimal(str(refund_value)) > Decimal(str(total_value)):
            return [
                ImportError(
                    row_number=row_number,
                    field="refund_amount",
                    message="refund_amount cannot exceed total_amount.",
                    severity="ERROR",
                    original_value=refund_value,
                )
            ]
    except (ArithmeticError, ValueError):
        return []
    return []


def validate_import_data(
    rows: list[dict[str, Any]],
    import_type: str,
    foreign_key_checks: dict[str, set[str]] | None = None,
) -> list[ImportError]:
    """Validate all rows for a given import type.

    Args:
        rows: List of data rows
        import_type: Import type (CUSTOMER, ORDER, etc.)
        foreign_key_checks: Optional dict of field -> valid IDs for FK validation

    Returns:
        List of all validation errors
    """
    all_errors: list[ImportError] = []
    field_config = IMPORT_TYPE_FIELDS.get(import_type)

    if not field_config:
        return [
            ImportError(
                row_number=0,
                field="import_type",
                message=f"Loại import '{import_type}' không được hỗ trợ.",
                severity="ERROR",
            )
        ]

    # Check for duplicates
    unique_keys = field_config.get("unique_keys", [])
    if unique_keys:
        all_errors.extend(check_duplicates(rows, unique_keys, entity_name=import_type))

    # Validate each row
    for i, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
        # Required fields
        all_errors.extend(
            validate_required_fields(row, i, field_config.get("required", []))
        )

        # Email validation
        for email_field in field_config.get("email_fields", []):
            all_errors.extend(validate_email(row, i, email_field))

        # Phone validation
        for phone_field in field_config.get("phone_fields", []):
            all_errors.extend(validate_phone(row, i, phone_field))

        # Date validation
        for date_field in field_config.get("date_fields", []):
            all_errors.extend(validate_date(row, i, date_field))

        # Numeric validation
        for num_field in field_config.get("numeric_fields", []):
            all_errors.extend(validate_numeric(row, i, num_field, min_value=0))
        if import_type == "ORDER":
            all_errors.extend(validate_refund_amount(row, i))

        # Status validation
        for status_field, allowed_values in field_config.get(
            "status_fields", {}
        ).items():
            all_errors.extend(validate_status(row, i, status_field, allowed_values))

        # Foreign key validation
        if foreign_key_checks:
            for fk_field, valid_ids in foreign_key_checks.items():
                if fk_field in row and row[fk_field]:
                    all_errors.extend(
                        validate_foreign_key(
                            row, i, fk_field, valid_ids, entity_name=fk_field
                        )
                    )

    return all_errors


def map_row_data(
    row: dict[str, Any],
    column_mapping: dict[str, str],
) -> dict[str, Any]:
    """Map file columns to system fields using column mapping.

    Args:
        row: Original row data
        column_mapping: Mapping from file columns to system fields

    Returns:
        Mapped row data
    """
    mapped = {}
    for file_col, system_field in column_mapping.items():
        if file_col in row:
            value = row[file_col]
            # Clean string values
            if isinstance(value, str):
                value = value.strip()
            mapped[system_field] = value
    return mapped
