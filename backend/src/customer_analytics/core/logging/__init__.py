"""
Structured logging configuration using structlog.

- Development: colorful console output with readable format
- Production: JSON output for log aggregation systems

Request ID is automatically bound to all log entries via middleware.
Sensitive data (passwords, tokens) is never logged.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.processors import JSONRenderer

from customer_analytics.app.config import settings
from customer_analytics.core.logging.sanitizers import (
    _sanitize_sensitive_data,
)


def configure_logging() -> None:
    """Cấu hình structlog và standard logging.

    Gọi một lần khi ứng dụng khởi động.
    """
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        _sanitize_sensitive_data,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.set_exc_info,
    ]

    if settings.APP_ENV == "production":
        # Production: JSON output
        processors = shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[_sanitize_sensitive_data, JSONRenderer()],  # type: ignore[list-item]
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    else:
        # Development: colorful console
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=processors,
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)

    # Cấu hình root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Cấu hình structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:
    """Lấy logger instance với structlog.

    Usage:
        logger = get_logger(__name__)
        logger.info("user_login", email="user@example.com")
        logger.error("db_connection_failed", host=settings.POSTGRES_HOST)
    """
    return structlog.get_logger(name or __name__)
