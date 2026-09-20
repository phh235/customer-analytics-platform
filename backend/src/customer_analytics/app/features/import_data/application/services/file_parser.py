"""File parser service — Parse CSV and XLSX files."""

from __future__ import annotations

import csv
import io
from typing import Any

from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


def parse_csv(file_content: bytes) -> tuple[list[str], list[dict[str, Any]]]:
    """Parse CSV file content and return headers and rows.

    Args:
        file_content: Raw file content as bytes

    Returns:
        Tuple of (headers, rows)
    """
    try:
        text = file_content.decode("utf-8-sig")  # Handle BOM
        reader = csv.DictReader(io.StringIO(text))

        if reader.fieldnames is None:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="File CSV không có header row.",
            )

        headers = list(reader.fieldnames)
        rows = [row for row in reader]

        return headers, rows

    except UnicodeDecodeError:
        raise AppException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="File không đúng định dạng UTF-8. Vui lòng lưu lại với encoding UTF-8.",
        ) from None
    except csv.Error as e:
        raise AppException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=f"Lỗi đọc file CSV: {e!s}",
        ) from e


def parse_xlsx(file_content: bytes) -> tuple[list[str], list[dict[str, Any]]]:
    """Parse XLSX file content and return headers and rows.

    Args:
        file_content: Raw file content as bytes

    Returns:
        Tuple of (headers, rows)
    """
    try:
        import openpyxl
    except ImportError:
        raise AppException(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Thư viện openpyxl chưa được cài đặt.",
        ) from None

    try:
        wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
        ws = wb.active

        if ws is None:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="File XLSX không có sheet nào.",
            )

        rows_data = list(ws.iter_rows(values_only=True))
        if not rows_data:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="File XLSX trống.",
            )

        # First row is headers
        headers = [
            str(h) if h is not None else f"Column_{i}"
            for i, h in enumerate(rows_data[0])
        ]

        # Convert remaining rows to dicts
        data_rows = []
        for row in rows_data[1:]:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers):
                    row_dict[headers[i]] = value
            data_rows.append(row_dict)

        wb.close()
        return headers, data_rows

    except Exception as e:
        if isinstance(e, AppException):
            raise
        raise AppException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=f"Lỗi đọc file XLSX: {e!s}",
        ) from e


def parse_file(
    file_content: bytes, filename: str
) -> tuple[list[str], list[dict[str, Any]]]:
    """Parse file based on extension.

    Args:
        file_content: Raw file content as bytes
        filename: Original filename

    Returns:
        Tuple of (headers, rows)
    """
    lower_filename = filename.lower()

    if lower_filename.endswith(".csv"):
        return parse_csv(file_content)
    elif lower_filename.endswith((".xlsx", ".xls")):
        return parse_xlsx(file_content)
    else:
        raise AppException(
            error_code=ErrorCode.VALIDATION_ERROR,
            message=f"Định dạng file không được hỗ trợ: {filename}. Chỉ chấp nhận CSV và XLSX.",
        )


# ── Column mapping suggestions ─────────────────────────────

CUSTOMER_COLUMN_MAPPING = {
    "customer_id": "customer_id",
    "ma_khach_hang": "customer_id",
    "makh": "customer_id",
    "id": "customer_id",
    "ho_ten": "name",
    "ten": "name",
    "name": "name",
    "full_name": "name",
    "hoten": "name",
    "email": "email",
    "e-mail": "email",
    "so_dien_thoai": "phone",
    "sdt": "phone",
    "phone": "phone",
    "dien_thoai": "phone",
    "gioi_tinh": "gender",
    "gender": "gender",
    "sex": "gender",
    "ngay_sinh": "date_of_birth",
    "date_of_birth": "date_of_birth",
    "dob": "date_of_birth",
    "ngay_tao": "customer_since",
    "customer_since": "customer_since",
    "created_at": "customer_since",
    "khu_vuc": "region",
    "region": "region",
    "city": "region",
    "address": "address",
    "dia_chi": "address",
}

ORDER_COLUMN_MAPPING = {
    "order_id": "order_id",
    "ma_don": "order_id",
    "madon": "order_id",
    "id": "order_id",
    "customer_id": "customer_id",
    "ma_khach_hang": "customer_id",
    "makh": "customer_id",
    "ngay_giao_dich": "order_date",
    "order_date": "order_date",
    "ngay_dat": "order_date",
    "tong_gia_tri": "total_amount",
    "total_amount": "total_amount",
    "thanhtien": "total_amount",
    "gia_tri": "total_amount",
    "trang_thai": "status",
    "status": "status",
    "kenh_ban_hang": "channel",
    "channel": "channel",
    "kenh": "channel",
}

ORDER_DETAIL_COLUMN_MAPPING = {
    "order_id": "order_id",
    "ma_don": "order_id",
    "product_id": "product_id",
    "ma_san_pham": "product_id",
    "masp": "product_id",
    "so_luong": "quantity",
    "quantity": "quantity",
    "sl": "quantity",
    "don_gia": "unit_price",
    "unit_price": "unit_price",
    "gia": "unit_price",
    "thanh_tien": "subtotal",
    "subtotal": "subtotal",
}

PRODUCT_COLUMN_MAPPING = {
    "product_id": "product_id",
    "ma_san_pham": "product_id",
    "masp": "product_id",
    "id": "product_id",
    "ten_san_pham": "name",
    "name": "name",
    "tensp": "name",
    "danh_muc": "category",
    "category": "category",
    "loai": "category",
    "gia_ban": "price",
    "price": "price",
    "gia": "price",
}
INTERACTION_COLUMN_MAPPING = {
    "interaction_id": "interaction_id",
    "ma_tuong_tac": "interaction_id",
    "interaction_code": "interaction_id",
    "customer_id": "customer_id",
    "ma_khach_hang": "customer_id",
    "makh": "customer_id",
    "product_id": "product_id",
    "ma_san_pham": "product_id",
    "masp": "product_id",
    "campaign_id": "campaign_id",
    "ma_chien_dich": "campaign_id",
    "interaction_type": "interaction_type",
    "loai_tuong_tac": "interaction_type",
    "type": "interaction_type",
    "interaction_timestamp": "interaction_timestamp",
    "thoi_gian": "interaction_timestamp",
    "timestamp": "interaction_timestamp",
    "channel": "channel",
    "kenh": "channel",
    "session_id": "session_id",
    "interaction_value": "interaction_value",
    "gia_tri_tuong_tac": "interaction_value",
    "interaction_result": "interaction_result",
    "ket_qua": "interaction_result",
    "is_mock_data": "is_mock_data",
}


IMPORT_TYPE_MAPPINGS = {
    "CUSTOMER": CUSTOMER_COLUMN_MAPPING,
    "ORDER": ORDER_COLUMN_MAPPING,
    "ORDER_DETAIL": ORDER_DETAIL_COLUMN_MAPPING,
    "PRODUCT": PRODUCT_COLUMN_MAPPING,
    "INTERACTION": INTERACTION_COLUMN_MAPPING,
}


def suggest_mapping(
    columns: list[str],
    import_type: str,
) -> dict[str, str]:
    """Suggest column mapping based on import type.

    Args:
        columns: Column names from file
        import_type: Import type (CUSTOMER, ORDER, etc.)

    Returns:
        Suggested mapping dict
    """
    mapping_template = IMPORT_TYPE_MAPPINGS.get(import_type, {})
    suggested = {}

    for col in columns:
        col_lower = col.lower().strip()
        if col_lower in mapping_template:
            suggested[col] = mapping_template[col_lower]

    return suggested
