"""Process import use case — Process imported data and save to database."""

from __future__ import annotations

import uuid
from abc import abstractmethod
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.import_data.application.dto.import_models import (
    ImportJobReadModel,
)
from customer_analytics.app.features.import_data.application.services.data_quality_service import (
    map_row_data,
    validate_import_data,
)
from customer_analytics.app.features.import_data.application.services.dataset_contract import (
    parse_dataset_workbook,
)
from customer_analytics.app.features.import_data.application.services.dataset_workbook_importer import (
    import_dataset_workbook,
)
from customer_analytics.app.features.import_data.application.services.file_parser import (
    parse_file,
)
from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportJob,
)
from customer_analytics.app.features.import_data.domain.enums import ImportStatus
from customer_analytics.app.features.import_data.domain.repositories.import_job_repository import (
    ImportJobRepository,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException
from customer_analytics.core.use_cases.use_case import BaseUseCase

IMPORT_ID_NAMESPACE = uuid.UUID("3f5a6d1f-9b48-4f54-8b2b-5ac8b0ad7a11")


def _import_id(value: Any, entity_type: str) -> str:
    """Map external source identifiers to stable UUIDs for relational storage."""
    if value is None or value == "":
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(str(value)))
    except ValueError:
        return str(uuid.uuid5(IMPORT_ID_NAMESPACE, f"{entity_type}:{value}"))


class ProcessImportUseCase(BaseUseCase[tuple[str, dict[str, str]], ImportJobReadModel]):
    """Process import use case interface."""

    @abstractmethod
    async def __call__(self, args: tuple[str, dict[str, str]]) -> ImportJobReadModel:
        raise NotImplementedError()


class ProcessImportUseCaseImpl(ProcessImportUseCase):
    """Process import use case implementation."""

    def __init__(
        self,
        repository: ImportJobRepository,
        customer_repository=None,
        order_repository=None,
        product_repository=None,
        interaction_repository=None,
        session: AsyncSession | None = None,
    ):
        self.repository = repository
        self.customer_repository = customer_repository
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.interaction_repository = interaction_repository
        self.session = session

    async def __call__(self, args: tuple[str, dict[str, str]]) -> ImportJobReadModel:
        job_id, column_mapping = args

        # Tìm import job và chỉ cho xử lý job đang ở trạng thái PENDING.
        job = await self.repository.find_by_id(job_id)
        if job is None:
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message=f"Import job '{job_id}' không tồn tại.",
            )

        if job.status != ImportStatus.PENDING:
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message=f"Import job đã ở trạng thái '{job.status.value}'. Chỉ có thể xử lý job ở trạng thái PENDING.",
            )

        # Lưu mapping và chuyển job sang bước kiểm tra dữ liệu.
        job = job.start_validation()
        job.mapping = column_mapping
        await self.repository.update(job)

        if not job.storage_key:
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message="Import job không có file nguồn để xử lý.",
            )

        from pathlib import Path

        from customer_analytics.app.config import settings

        source_path = Path(settings.IMPORT_STORAGE_DIR) / job.storage_key
        if not source_path.is_file():
            raise AppException(
                error_code=ErrorCode.NOT_FOUND,
                message="Không tìm thấy file nguồn của import job.",
            )
        source_content = source_path.read_bytes()
        if job.import_type.value == "DATASET":
            if self.session is None:
                raise AppException(
                    error_code=ErrorCode.INVALID_OPERATION,
                    message="DATASET import cần AsyncSession.",
                )
            workbook = parse_dataset_workbook(source_content)
            job.mapping = column_mapping
            await self.repository.update(job)
            job = await import_dataset_workbook(self.session, workbook, job)
            await self.repository.update(job)
            return ImportJobReadModel.from_entity(job)

        # Đọc file, đổi tên cột theo mapping rồi kiểm tra dữ liệu.
        _, rows = parse_file(source_content, job.filename)
        mapped_rows = [map_row_data(row, column_mapping) for row in rows]
        validation_errors = validate_import_data(mapped_rows, job.import_type.value)
        validation_errors.extend(
            await self._validate_persistent_relationships(
                mapped_rows, job.import_type.value
            )
        )

        if validation_errors:
            # Add validation errors to job.
            for error in validation_errors:
                job = job.add_error(error)

            # If all rows have errors, fail the job.
            if job.error_rows >= job.total_rows:
                job = job.fail("Tất cả các dòng đều có lỗi.")
                await self.repository.update(job)
                return ImportJobReadModel.from_entity(job)

        # Start processing.
        job = job.start_processing()
        await self.repository.update(job)

        # Process rows based on import type.
        try:
            if job.import_type.value == "CUSTOMER":
                job = await self._process_customers(mapped_rows, job)
            elif job.import_type.value == "ORDER":
                job = await self._process_orders(mapped_rows, job)
            elif job.import_type.value == "ORDER_DETAIL":
                job = await self._process_order_details(mapped_rows, job)
            elif job.import_type.value == "PRODUCT":
                job = await self._process_products(mapped_rows, job)
            elif job.import_type.value == "INTERACTION":
                job = await self._process_interactions(mapped_rows, job)
        except Exception as e:
            job = job.fail(f"Lỗi xử lý: {e!s}")
            await self.repository.update(job)
            return ImportJobReadModel.from_entity(job)

        # Complete job.
        job = job.complete()
        await self.repository.update(job)

        return ImportJobReadModel.from_entity(job)

    async def _validate_persistent_relationships(
        self, rows: list[dict[str, Any]], import_type: str
    ) -> list[Any]:
        """Validate foreign keys against persisted customer/order/product data."""
        from customer_analytics.app.features.import_data.domain.entities.import_job import (
            ImportError,
        )

        errors: list[ImportError] = []
        if import_type == "ORDER" and self.customer_repository:
            for index, row in enumerate(rows, start=2):
                customer_id = _import_id(row.get("customer_id"), "customer")
                if await self.customer_repository.find_by_id(customer_id) is None:
                    errors.append(
                        ImportError(
                            index,
                            "customer_id",
                            f"Customer '{row.get('customer_id')}' không tồn tại",
                        )
                    )
        elif (
            import_type == "ORDER_DETAIL"
            and self.order_repository
            and self.product_repository
        ):
            for index, row in enumerate(rows, start=2):
                order = await self.order_repository.find_by_order_number(
                    str(row.get("order_id"))
                )
                product = await self.product_repository.find_by_id(
                    _import_id(row.get("product_id"), "product")
                )
                if order is None:
                    errors.append(ImportError(index, "order_id", "Order không tồn tại"))
                if product is None:
                    errors.append(
                        ImportError(index, "product_id", "Product không tồn tại")
                    )
        elif (
            import_type == "INTERACTION"
            and self.customer_repository
            and self.product_repository
        ):
            for index, row in enumerate(rows, start=2):
                customer = await self.customer_repository.find_by_id(
                    _import_id(row.get("customer_id"), "customer")
                )
                product = await self.product_repository.find_by_id(
                    _import_id(row.get("product_id"), "product")
                )
                if customer is None:
                    errors.append(
                        ImportError(index, "customer_id", "Customer không tồn tại")
                    )
                if product is None:
                    errors.append(
                        ImportError(index, "product_id", "Product không tồn tại")
                    )
        return errors

    async def _process_customers(
        self, rows: list[dict[str, Any]], job: ImportJob
    ) -> ImportJob:
        """Process customer rows."""
        from customer_analytics.app.features.customer.domain.entities.customer_entity import (
            CustomerEntity,
        )

        for i, row in enumerate(rows, start=2):
            try:
                # Skip rows with errors
                has_error = any(
                    e.row_number == i and e.severity == "ERROR" for e in job.errors
                )
                if has_error:
                    job = job.increment_processed(success=False)
                    continue

                # Create customer entity
                customer = CustomerEntity(
                    id_=_import_id(row.get("customer_id"), "customer"),
                    name=row.get("name", ""),
                    email=row.get("email"),
                    phone=row.get("phone"),
                    address=row.get("address"),
                    gender=row.get("gender"),
                    region=row.get("region"),
                )

                # Save to database
                if self.customer_repository:
                    await self.customer_repository.create(customer)

                job = job.increment_processed(success=True)

            except Exception as e:
                from customer_analytics.app.features.import_data.domain.entities.import_job import (
                    ImportError,
                )

                error = ImportError(
                    row_number=i,
                    field="system",
                    message=f"Lỗi lưu dữ liệu: {e!s}",
                    severity="ERROR",
                )
                job = job.add_error(error)
                job = job.increment_processed(success=False)

        return job

    async def _process_orders(
        self, rows: list[dict[str, Any]], job: ImportJob
    ) -> ImportJob:
        """Process order rows."""
        from customer_analytics.app.features.order.domain.entities.order_entity import (
            OrderEntity,
        )

        for i, row in enumerate(rows, start=2):
            try:
                has_error = any(
                    e.row_number == i and e.severity == "ERROR" for e in job.errors
                )
                if has_error:
                    job = job.increment_processed(success=False)
                    continue

                # Parse order date
                order_date = row.get("order_date")
                if isinstance(order_date, str):
                    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                        try:
                            order_date = datetime.strptime(order_date, fmt)
                            break
                        except ValueError:
                            continue

                order = OrderEntity(
                    id_=_import_id(row.get("order_id"), "order"),
                    customer_id=_import_id(row.get("customer_id"), "customer"),
                    order_number=str(
                        row.get("order_id", f"ORD-{uuid.uuid4().hex[:8]}")
                    ),
                    order_date=order_date or datetime.now(UTC),
                    total_amount=Decimal(str(row.get("total_amount", 0))),
                    refund_amount=Decimal(str(row.get("refund_amount", 0))),
                    status=str(row.get("status", "COMPLETED")),
                    channel=row.get("channel"),
                )

                if self.order_repository:
                    await self.order_repository.create(order)

                job = job.increment_processed(success=True)

            except Exception as e:
                from customer_analytics.app.features.import_data.domain.entities.import_job import (
                    ImportError,
                )

                error = ImportError(
                    row_number=i,
                    field="system",
                    message=f"Lỗi lưu dữ liệu: {e!s}",
                    severity="ERROR",
                )
                job = job.add_error(error)
                job = job.increment_processed(success=False)

        return job

    async def _process_order_details(
        self, rows: list[dict[str, Any]], job: ImportJob
    ) -> ImportJob:
        """Process order detail rows."""
        from customer_analytics.app.features.order.domain.entities.order_entity import (
            OrderItemEntity,
        )

        if self.order_repository is None:
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message="Order repository chưa được cấu hình cho import detail.",
            )

        for i, row in enumerate(rows, start=2):
            try:
                has_error = any(
                    e.row_number == i and e.severity == "ERROR" for e in job.errors
                )
                if has_error:
                    job = job.increment_processed(success=False)
                    continue

                order = await self.order_repository.find_by_order_number(
                    row["order_id"]
                )
                if order is None:
                    raise ValueError(f"Order '{row['order_id']}' không tồn tại")
                item = OrderItemEntity(
                    id_=None,
                    order_id=str(order.id_),
                    product_id=_import_id(row["product_id"], "product"),
                    quantity=int(row["quantity"]),
                    unit_price=Decimal(str(row["unit_price"])),
                    subtotal=Decimal(
                        str(
                            row.get("subtotal")
                            or Decimal(str(row["quantity"]))
                            * Decimal(str(row["unit_price"]))
                        )
                    ),
                )
                order.items.append(item)
                await self.order_repository.update(order)
                job = job.increment_processed(success=True)

            except Exception as e:
                from customer_analytics.app.features.import_data.domain.entities.import_job import (
                    ImportError,
                )

                error = ImportError(
                    row_number=i,
                    field="system",
                    message=f"Lỗi xử lý chi tiết đơn hàng: {e!s}",
                    severity="ERROR",
                )
                job = job.add_error(error)
                job = job.increment_processed(success=False)

        return job

    async def _process_products(
        self, rows: list[dict[str, Any]], job: ImportJob
    ) -> ImportJob:
        """Process product rows."""
        from customer_analytics.app.features.product.domain.entities.product_entity import (
            ProductEntity,
        )

        for i, row in enumerate(rows, start=2):
            try:
                has_error = any(
                    e.row_number == i and e.severity == "ERROR" for e in job.errors
                )
                if has_error:
                    job = job.increment_processed(success=False)
                    continue

                product = ProductEntity(
                    id_=_import_id(row.get("product_id"), "product"),
                    name=row.get("name", ""),
                    category=row.get("category", ""),
                    price=Decimal(str(row.get("price", 0))),
                    status=row.get("status", "ACTIVE"),
                )

                if self.product_repository:
                    await self.product_repository.create(product)

                job = job.increment_processed(success=True)

            except Exception as e:
                from customer_analytics.app.features.import_data.domain.entities.import_job import (
                    ImportError,
                )

                error = ImportError(
                    row_number=i,
                    field="system",
                    message=f"Lỗi lưu dữ liệu: {e!s}",
                    severity="ERROR",
                )
                job = job.add_error(error)
                job = job.increment_processed(success=False)

        return job

    async def _process_interactions(
        self, rows: list[dict[str, Any]], job: ImportJob
    ) -> ImportJob:
        """Process customer interaction rows."""
        if self.interaction_repository is None:
            raise AppException(
                error_code=ErrorCode.INVALID_OPERATION,
                message="Interaction repository chưa được cấu hình cho import.",
            )

        for i, row in enumerate(rows, start=2):
            try:
                has_error = any(
                    e.row_number == i and e.severity == "ERROR" for e in job.errors
                )
                if has_error:
                    job = job.increment_processed(success=False)
                    continue

                timestamp = row["interaction_timestamp"]
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=UTC)

                is_mock_data = row.get("is_mock_data", False)
                if isinstance(is_mock_data, str):
                    is_mock_data = is_mock_data.strip().lower() in {
                        "1",
                        "true",
                        "yes",
                        "y",
                    }
                await self.interaction_repository.create(
                    {
                        "id": _import_id(row["interaction_id"], "interaction"),
                        "interaction_code": str(row["interaction_id"]),
                        "customer_id": _import_id(row["customer_id"], "customer"),
                        "product_id": _import_id(row["product_id"], "product"),
                        "campaign_id": row.get("campaign_id"),
                        "interaction_type": row["interaction_type"],
                        "interaction_timestamp": timestamp,
                        "channel": row.get("channel"),
                        "session_id": row.get("session_id"),
                        "interaction_value": row.get("interaction_value", 0),
                        "interaction_result": row.get("interaction_result"),
                        "is_mock_data": is_mock_data,
                    }
                )
                job = job.increment_processed(success=True)
            except Exception as e:
                from customer_analytics.app.features.import_data.domain.entities.import_job import (
                    ImportError,
                )

                error = ImportError(
                    row_number=i,
                    field="system",
                    message=f"Lỗi lưu tương tác: {e!s}",
                    severity="ERROR",
                )
                job = job.add_error(error)
                job = job.increment_processed(success=False)

        return job
