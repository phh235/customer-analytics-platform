"""Application dependencies — FastAPI dependency injection."""

from __future__ import annotations

from functools import lru_cache

from customer_analytics.app.config import Settings


@lru_cache
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
