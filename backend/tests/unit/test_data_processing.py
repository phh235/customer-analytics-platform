from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from customer_analytics.app.features.import_data.application.usecases.process_import import (  # noqa: E501
    _import_id,
)
from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportError,
    ImportJob,
)
from customer_analytics.app.features.import_data.domain.enums import (
    ImportStatus,
    ImportType,
)


def test_external_identifier_maps_to_stable_uuid() -> None:
    first = _import_id("C001", "customer")
    second = _import_id("C001", "customer")

    assert first == second
    assert _import_id("C001", "customer") != _import_id("C001", "order")


def test_import_job_reports_partial_completion() -> None:
    job = ImportJob(
        id_="job-1",
        filename="customers.csv",
        import_type=ImportType.CUSTOMER,
        total_rows=2,
        created_at=datetime.now(UTC),
    )
    job = job.add_error(
        ImportError(row_number=2, field="email", message="Invalid email")
    )
    job = job.increment_processed(success=False)
    job = job.increment_processed(success=True)

    completed = job.complete()

    assert completed.status == ImportStatus.PARTIALLY_COMPLETED
    assert completed.error_rows == 1
    assert completed.success_rows == 1


def test_import_job_fails_when_every_row_is_invalid() -> None:
    job = ImportJob(
        id_="job-2",
        filename="orders.csv",
        import_type=ImportType.ORDER,
        total_rows=1,
    )
    failed = (
        job.add_error(
            ImportError(row_number=2, field="customer_id", message="Missing customer")
        )
        .increment_processed(success=False)
        .fail("All rows are invalid")
    )

    assert failed.status == ImportStatus.FAILED
    assert failed.error_rows == 1


def test_decimal_calculation_preserves_money_precision() -> None:
    quantity = Decimal("3")
    unit_price = Decimal("12.50")

    assert quantity * unit_price == Decimal("37.50")
