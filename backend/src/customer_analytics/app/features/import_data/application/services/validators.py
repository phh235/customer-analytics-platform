"""Data quality validators — Validate imported data."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportError,
)


def validate_required_fields(
    row: dict[str, Any],
    row_number: int,
    required_fields: list[str],
) -> list[ImportError]:
    """Validate that required fields are present and not empty.

    Args:
        row: Data row
        row_number: Row number in file
        required_fields: List of required field names

    Returns:
        List of validation errors
    """
    errors = []
    for field in required_fields:
        value = row.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            errors.append(
                ImportError(
                    row_number=row_number,
                    field=field,
                    message=f"Trường '{field}' là bắt buộc.",
                    severity="ERROR",
                    original_value=value,
                )
            )
    return errors


def validate_email(
    row: dict[str, Any],
    row_number: int,
    field: str = "email",
) -> list[ImportError]:
    """Validate email format.

    Args:
        row: Data row
        row_number: Row number in file
        field: Email field name

    Returns:
        List of validation errors
    """
    errors = []
    value = row.get(field)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return errors  # Empty is ok, use validate_required_fields for required

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, str(value).strip()):
        errors.append(
            ImportError(
                row_number=row_number,
                field=field,
                message=f"Email '{value}' không hợp lệ.",
                severity="ERROR",
                original_value=value,
            )
        )
    return errors


def validate_phone(
    row: dict[str, Any],
    row_number: int,
    field: str = "phone",
) -> list[ImportError]:
    """Validate phone number format.

    Args:
        row: Data row
        row_number: Row number in file
        field: Phone field name

    Returns:
        List of validation errors
    """
    errors = []
    value = row.get(field)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return errors

    # Remove spaces and dashes
    cleaned = str(value).strip().replace(" ", "").replace("-", "")

    # Vietnamese phone: 10-11 digits, starts with 0
    phone_regex = r"^0\d{9,10}$"
    if not re.match(phone_regex, cleaned):
        errors.append(
            ImportError(
                row_number=row_number,
                field=field,
                message=f"Số điện thoại '{value}' không hợp lệ. Phải là 10-11 chữ số, bắt đầu bằng 0.",
                severity="WARNING",
                original_value=value,
            )
        )
    return errors


def validate_date(
    row: dict[str, Any],
    row_number: int,
    field: str,
    formats: list[str] | None = None,
) -> list[ImportError]:
    """Validate date format.

    Args:
        row: Data row
        row_number: Row number in file
        field: Date field name
        formats: List of acceptable date formats

    Returns:
        List of validation errors
    """
    errors = []
    value = row.get(field)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return errors

    if formats is None:
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]

    # If it's already a datetime object, it's valid
    if isinstance(value, datetime):
        return errors

    # Accept ISO timestamps used by interaction exports as well as date-only values.
    try:
        datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        return errors
    except ValueError:
        pass

    # Try parsing with each date-only format.
    parsed = False
    for fmt in formats:
        try:
            datetime.strptime(str(value).strip(), fmt)
            parsed = True
            break
        except ValueError:
            continue
    if not parsed:
        errors.append(
            ImportError(
                row_number=row_number,
                field=field,
                message=f"Ngày '{value}' không hợp lệ. Định dạng: YYYY-MM-DD hoặc DD/MM/YYYY.",
                severity="ERROR",
                original_value=value,
            )
        )
    return errors


def validate_numeric(
    row: dict[str, Any],
    row_number: int,
    field: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> list[ImportError]:
    """Validate numeric value.

    Args:
        row: Data row
        row_number: Row number in file
        field: Field name
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        List of validation errors
    """
    errors = []
    value = row.get(field)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return errors

    try:
        num_value = float(value)
        if min_value is not None and num_value < min_value:
            errors.append(
                ImportError(
                    row_number=row_number,
                    field=field,
                    message=f"Giá trị '{value}' phải >= {min_value}.",
                    severity="ERROR",
                    original_value=value,
                )
            )
        if max_value is not None and num_value > max_value:
            errors.append(
                ImportError(
                    row_number=row_number,
                    field=field,
                    message=f"Giá trị '{value}' phải <= {max_value}.",
                    severity="ERROR",
                    original_value=value,
                )
            )
    except (ValueError, TypeError):
        errors.append(
            ImportError(
                row_number=row_number,
                field=field,
                message=f"Giá trị '{value}' phải là số.",
                severity="ERROR",
                original_value=value,
            )
        )
    return errors


def validate_status(
    row: dict[str, Any],
    row_number: int,
    field: str,
    allowed_values: list[str],
) -> list[ImportError]:
    """Validate status field against allowed values.

    Args:
        row: Data row
        row_number: Row number in file
        field: Field name
        allowed_values: List of allowed values

    Returns:
        List of validation errors
    """
    errors = []
    value = row.get(field)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return errors

    if str(value).strip().upper() not in [v.upper() for v in allowed_values]:
        errors.append(
            ImportError(
                row_number=row_number,
                field=field,
                message=f"Giá trị '{value}' không hợp lệ. Chỉ chấp nhận: {', '.join(allowed_values)}.",
                severity="ERROR",
                original_value=value,
            )
        )
    return errors


def check_duplicates(
    rows: list[dict[str, Any]],
    fields: list[str],
    entity_name: str = "Bản ghi",
) -> list[ImportError]:
    """Check for duplicate records based on key fields.

    Args:
        rows: List of data rows
        fields: Fields to check for uniqueness
        entity_name: Name of entity for error message

    Returns:
        List of duplicate errors
    """
    errors = []
    seen: dict[str, list[int]] = {}

    for i, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
        key_parts = []
        for field in fields:
            value = row.get(field)
            if value is not None:
                key_parts.append(str(value).strip().lower())

        if not key_parts:
            continue

        key = "|".join(key_parts)

        if key in seen:
            seen[key].append(i)
        else:
            seen[key] = [i]

    # Report duplicates
    for key, row_numbers in seen.items():
        if len(row_numbers) > 1:
            fields_str = ", ".join(fields)
            errors.append(
                ImportError(
                    row_number=row_numbers[0],
                    field=fields_str,
                    message=f"{entity_name} bị trùng lặp tại các dòng: {', '.join(map(str, row_numbers))}.",
                    severity="WARNING",
                    original_value=key,
                )
            )

    return errors


def validate_foreign_key(
    row: dict[str, Any],
    row_number: int,
    field: str,
    valid_ids: set[str],
    entity_name: str,
) -> list[ImportError]:
    """Validate foreign key exists in related table.

    Args:
        row: Data row
        row_number: Row number in file
        field: Field name
        valid_ids: Set of valid IDs
        entity_name: Name of related entity

    Returns:
        List of validation errors
    """
    errors = []
    value = row.get(field)

    if value is None or (isinstance(value, str) and value.strip() == ""):
        return errors

    if str(value).strip() not in valid_ids:
        errors.append(
            ImportError(
                row_number=row_number,
                field=field,
                message=f"{entity_name} '{value}' không tồn tại.",
                severity="ERROR",
                original_value=value,
            )
        )
    return errors
