"""Import job database model — SQLAlchemy model."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from customer_analytics.core.database import Base
from customer_analytics.core.database.mixins import (
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)


class ImportJobModel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Import job database model."""

    __tablename__ = "import_jobs"
    __table_args__ = {"extend_existing": True}

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    import_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # CUSTOMER/ORDER/ORDER_DETAIL/PRODUCT
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING", index=True
    )
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<ImportJobModel(id={self.id}, filename='{self.filename}', status='{self.status}')>"
