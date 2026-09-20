"""Application configuration — Settings loaded from environment variables.

Source of truth: .env file (copy from .env.example)
Config.py only defines types and validation — no hardcoded defaults.
"""

from __future__ import annotations

from typing import Literal

from pydantic import field_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str
    APP_ENV: str
    APP_DEBUG: bool
    APP_VERSION: str
    LOG_LEVEL: str

    # ── API ──────────────────────────────────────────────
    API_V1_PREFIX: str
    FRONTEND_URL: str
    IMPORT_STORAGE_DIR: str
    MODEL_STORAGE_DIR: str = "storage/models"
    # ── AI chat ───────────────────────────────────────────────
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "openai/gpt-oss-20b"
    GROQ_TIMEOUT_SECONDS: float = 30.0
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_COMPLETION_TOKENS: int = 1024
    GROQ_REASONING_FORMAT: Literal["hidden", "parsed", "raw"] = "hidden"
    GROQ_REASONING_EFFORT: Literal["none", "default", "low", "medium", "high"] = "low"
    # ── Controlled analytics gateway ───────────────────────
    AI_ANALYTICS_DATABASE_URL: str | None = None
    AI_ANALYTICS_STATEMENT_TIMEOUT_MS: int = 3000
    AI_ANALYTICS_MAX_RESULT_ROWS: int = 100
    AI_ANALYTICS_MAX_SQL_LENGTH: int = 10_000
    AI_ANALYTICS_MAX_JOINS: int = 5
    AI_ANALYTICS_MAX_QUERY_COST: float = 100_000.0

    # ── Business analytics ────────────────────────────────
    ANALYSIS_TIMEZONE: str = "Asia/Ho_Chi_Minh"
    VALID_ORDER_STATUSES: list[str] = [
        "PAID",
        "COMPLETED",
        "DELIVERED",
        "PARTIAL_REFUNDED",
    ]

    # ── CORS ─────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: list[str]
    BACKEND_CORS_ORIGIN_REGEX: str | None = None

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

    # ── Google OAuth2 ────────────────────────────────────
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # ── Email ─────────────────────────────────────────────
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str | None = None
    SMTP_FROM_NAME: str = "Customer Analytics"
    SMTP_USE_TLS: bool = True

    # ── Cloudinary ─────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None
    CLOUDINARY_PRODUCT_FOLDER: str = "customer-analytics/products"
    CLOUDINARY_CUSTOMER_FOLDER: str = "customer-analytics/customers"

    @property
    def cloudinary_is_configured(self) -> bool:
        """Return whether all Cloudinary credentials are available."""
        return all(
            (
                self.CLOUDINARY_CLOUD_NAME,
                self.CLOUDINARY_API_KEY,
                self.CLOUDINARY_API_SECRET,
            )
        )

    # ── Potential Score configuration ─────────────────────
    SCORE_WEIGHT_RECENCY: float = 0.35
    SCORE_WEIGHT_FREQUENCY: float = 0.30
    SCORE_WEIGHT_MONETARY: float = 0.20
    SCORE_WEIGHT_INTERACTION: float = 0.15
    SCORE_COMPONENT_MAX: int = 5
    SCORE_SCALE_MULTIPLIER: float = 20
    SCORING_CONFIGURATION_VERSION: str = "SCRIPT_DUAN_V4_EXCEL_PARITY"
    POTENTIAL_HIGH_THRESHOLD: int = 80
    POTENTIAL_THRESHOLD: int = 60

    # ── ML acceptance gates ───────────────────────────────
    ML_MIN_LIFT_TOP10: float = 2.0
    ML_MIN_PRECISION_TOP10_MULTIPLIER: float = 2.0
    ML_BASELINE_PR_AUC: float = 0.0
    ML_PRIORITY_PROBABILITY_THRESHOLD: float = 0.5

    @property
    def score_weights(self) -> dict[str, float]:
        """Return configured potential-score weights."""
        return {
            "recency": self.SCORE_WEIGHT_RECENCY,
            "frequency": self.SCORE_WEIGHT_FREQUENCY,
            "monetary": self.SCORE_WEIGHT_MONETARY,
            "interaction": self.SCORE_WEIGHT_INTERACTION,
        }

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

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def normalize_cors_origins(cls, origins: list[str]) -> list[str]:
        """Normalize configured origins to browser Origin header format."""
        return [origin.rstrip("/") for origin in origins]

    @field_validator(
        "SCORE_WEIGHT_RECENCY",
        "SCORE_WEIGHT_FREQUENCY",
        "SCORE_WEIGHT_MONETARY",
        "SCORE_WEIGHT_INTERACTION",
    )
    @classmethod
    def validate_score_weight(cls, v: float) -> float:
        if not 0 <= v <= 1:
            msg = f"Score weight must be between 0 and 1, got '{v}'"
            raise ValueError(msg)
        return v

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
