"""Application configuration — Settings loaded from environment variables.

Source of truth: .env file (copy from .env.example)
Config.py only defines types and validation — no hardcoded defaults.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str
    APP_ENV: str
    APP_DEBUG: bool
    APP_VERSION: str

    # ── API ──────────────────────────────────────────────
    API_V1_PREFIX: str

    # ── CORS ─────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: list[str]

    # ── Database ─────────────────────────────────────────
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # ── Connection Pool ──────────────────────────────────
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_PRE_PING: bool
    DB_POOL_TIMEOUT: int
    DB_POOL_RECYCLE: int

    @property
    def database_url(self) -> str:
        """Build async connection string from parts.

        Format: postgresql+asyncpg://user:password@host:port/db
        """
        return str(
            MultiHostUrl.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    @property
    def database_url_sync(self) -> str:
        """Synchronous URL for Alembic (Alembic doesn't support async driver)."""
        return self.database_url.replace("+asyncpg", "")

    # ── JWT ──────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_TTL_MINUTES: int
    JWT_REFRESH_TOKEN_TTL_DAYS: int

    @property
    def jwt_access_token_ttl_seconds(self) -> int:
        return self.JWT_ACCESS_TOKEN_TTL_MINUTES * 60

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str

    # ── Validation ───────────────────────────────────────

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "test", "staging", "production"}
        if v not in allowed:
            msg = f"APP_ENV must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            msg = f"LOG_LEVEL must be one of {allowed}, got '{v}'"
            raise ValueError(msg)
        return v.upper()

    # ── Config ───────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # Fail early nếu config sai hoặc thiếu
        extra="forbid",
    )


# Singleton instance — import ở mọi nơi để đọc settings
settings = Settings()
