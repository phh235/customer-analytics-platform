"""Identity domain exceptions.

All exceptions use AppException + ErrorCode from shared layer.
"""

from __future__ import annotations

# Re-export AppException for convenience
from customer_analytics.app.shared.exceptions import AppException

__all__ = ["AppException"]
