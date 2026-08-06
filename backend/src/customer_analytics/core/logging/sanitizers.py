"""
Sanitizers cho structured logging — che dữ liệu nhạy cảm trước khi log.

Che giá trị nếu key chứa: password, secret, token, key, credential.
Không bao giờ log password, token, hoặc JWT secret.
"""

from __future__ import annotations

import logging
from typing import Any

SENSITIVE_KEYS: set[str] = {
    "password",
    "secret",
    "token",
    "authorization",
    "key",
    "credential",
}


def _sanitize_sensitive_data(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Processor để che dữ liệu nhạy cảm trước khi log."""
    for key in list(event_dict.keys()):
        key_lower = key.lower()
        if any(s in key_lower for s in SENSITIVE_KEYS):
            event_dict[key] = "***"
    return event_dict
