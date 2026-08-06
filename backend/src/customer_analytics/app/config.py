"""Application configuration — Settings loaded from environment variables."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "customer-analytics"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_VERSION: str = "0.1.0"

    # ── API ──────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ─────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:4000",
        "http://127.0.0.1:4000",
        "https://customer-analytics-app.vercel.app",
    ]

    # ── Database ─────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "customer_analytics"
    POSTGRES_USER: str = "customer_analytics"
    POSTGRES_PASSWORD: str = "change_me"

    # ── Connection Pool ──────────────────────────────────
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_PRE_PING: bool = True
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

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
    JWT_SECRET_KEY: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_TTL_MINUTES: int = 15
    JWT_REFRESH_TOKEN_TTL_DAYS: int = 7

    @property
    def jwt_access_token_ttl_seconds(self) -> int:
        return self.JWT_ACCESS_TOKEN_TTL_MINUTES * 60

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ── Validation helpers ───────────────────────────────

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
        # Không cho phép field lạ — fail early nếu config sai
        extra="forbid",
    )


# Singleton instance — import ở mọi nơi để đọc settings
settings = Settings()
