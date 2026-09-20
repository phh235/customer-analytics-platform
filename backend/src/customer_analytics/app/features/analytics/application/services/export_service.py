"""Export service — Build CSV/XLSX payloads for analytics exports."""

from __future__ import annotations

import csv
import io
from collections.abc import Sequence
from typing import Any

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def build_csv(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Build a CSV document from headers and row values."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(list(headers))
    for row in rows:
        writer.writerow(list(row))
    return output.getvalue()


def build_xlsx(
    sheet_name: str,
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
) -> bytes:
    """Build an XLSX workbook as bytes from headers and row values."""
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise AppException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            "Thư viện openpyxl chưa được cài đặt.",
        ) from exc

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name[:31]  # Excel sheet name limit
    sheet.append(list(headers))
    for row in rows:
        sheet.append(list(row))
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
