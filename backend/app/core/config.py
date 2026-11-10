"""Centralized application settings validated through Pydantic Settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and optional .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = "AgroNiaga TBS Supply Chain API"
    APP_ENV: Literal["development", "testing", "staging", "production"] = "development"
    APP_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_JSON: bool = True

    DATABASE_URL: SecretStr = SecretStr(
        "postgresql+psycopg://agroniaga_dev:change_me_local_only@127.0.0.1:5432/agroniaga_dev"
    )
    TEST_DATABASE_URL: SecretStr | None = None
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DB_POOL_TIMEOUT_SECONDS: int = Field(default=5, ge=1, le=60)
    DB_CONNECT_TIMEOUT_SECONDS: int = Field(default=5, ge=1, le=60)
    DB_STATEMENT_TIMEOUT_MS: int = Field(default=5000, ge=500, le=120000)

    REDIS_URL: SecretStr = SecretStr("redis://127.0.0.1:6379/0")
    TEST_REDIS_URL: SecretStr | None = None
    REDIS_CONNECT_TIMEOUT_SECONDS: float = Field(default=2.0, gt=0.1, le=30.0)
    REDIS_SOCKET_TIMEOUT_SECONDS: float = Field(default=2.0, gt=0.1, le=30.0)
    REDIS_MAX_CONNECTIONS: int = Field(default=20, ge=1, le=200)

    SESSION_COOKIE_NAME: str = "ts_agroniaga_session"
    SESSION_SECRET: SecretStr = SecretStr("local-dev-session-secret-replace-before-staging-32bytes")
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict"] = "lax"
    SESSION_TTL_SECONDS: int = Field(default=28800, ge=300, le=604800)
    LOGIN_RATE_LIMIT_MAX_ATTEMPTS: int = Field(default=5, ge=1, le=100)
    LOGIN_IP_RATE_LIMIT_MAX_ATTEMPTS: int = Field(default=30, ge=5, le=1000)
    LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60, ge=10, le=3600)

    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    REQUEST_TIMEOUT_SECONDS: int = Field(default=15, ge=1, le=120)
    FILE_STORAGE_DIR: str = "./var/evidence_files"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_scheme(cls, value: SecretStr) -> SecretStr:
        raw = value.get_secret_value()
        if not raw.startswith(("postgresql+psycopg://", "postgresql://")):
            raise ValueError("DATABASE_URL must use a PostgreSQL DSN")
        return value

    @field_validator("REDIS_URL")
    @classmethod
    def validate_redis_scheme(cls, value: SecretStr) -> SecretStr:
        raw = value.get_secret_value()
        if not raw.startswith(("redis://", "rediss://")):
            raise ValueError("REDIS_URL must use redis:// or rediss://")
        return value

    @field_validator("CORS_ALLOWED_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, origins: list[str]) -> list[str]:
        if "*" in origins:
            raise ValueError("Wildcard CORS origin '*' is forbidden with credentialed sessions")
        return origins

    @model_validator(mode="after")
    def validate_non_local_security(self) -> Settings:
        if self.APP_ENV in ("staging", "production"):
            secret = self.SESSION_SECRET.get_secret_value()
            if len(secret) < 32 or "local-dev-session-secret" in secret or "replace" in secret:
                raise ValueError(
                    "Strong unique SESSION_SECRET (>=32 chars) required in non-local env"
                )
            if not self.SESSION_COOKIE_SECURE:
                raise ValueError("SESSION_COOKIE_SECURE must be true in staging/production")
        return self

    @property
    def async_database_url(self) -> str:
        raw = self.DATABASE_URL.get_secret_value()
        if raw.startswith("postgresql://"):
            return raw.replace("postgresql://", "postgresql+psycopg://", 1)
        return raw


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached runtime settings instance."""
    return Settings()
