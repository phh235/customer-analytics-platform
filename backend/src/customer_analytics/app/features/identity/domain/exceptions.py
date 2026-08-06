"""Identity domain exceptions — Deprecated.

All exceptions now use AppException + ErrorCode from shared layer.
This file is kept for backward compatibility only.
"""

from __future__ import annotations

# Re-export AppException for backward compatibility
from customer_analytics.app.shared.exceptions import AppException

# Legacy aliases (deprecated — use AppException directly)
UserNotFoundError = AppException
InvalidCredentialsError = AppException
UserDisabledError = AppException
UserLockedError = AppException
EmailAlreadyExistsError = AppException
RoleNotFoundError = AppException
InsufficientPermissionsError = AppException
RefreshTokenError = AppException
RefreshTokenReuseError = AppException
CannotDisableSelfError = AppException
IdentityError = AppException
