"""Shared pytest fixtures configuring Windows Selector loop and isolated test settings."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = REPO_ROOT / "contracts"


@pytest.fixture
def contracts_dir() -> Path:
    """Return path to canonical M0.1 contracts directory."""
    return CONTRACTS_DIR


def _load_backend_env_settings():
    from app.core.config import Settings
    from pydantic_settings import SettingsConfigDict

    class _BackendEnvSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=BACKEND_ROOT / ".env",
            env_file_encoding="utf-8",
            extra="ignore",
            case_sensitive=True,
        )

    return _BackendEnvSettings()


@pytest.fixture
def test_db_url() -> str | None:
    """Return explicit TEST_DATABASE_URL from env or backend/.env without dev DB fallback."""
    if env_val := os.environ.get("TEST_DATABASE_URL"):
        return env_val
    settings = _load_backend_env_settings()
    return settings.TEST_DATABASE_URL.get_secret_value() if settings.TEST_DATABASE_URL else None


@pytest.fixture
def test_redis_url() -> str | None:
    """Return explicit TEST_REDIS_URL or REDIS_URL from env or backend/.env."""
    if env_val := os.environ.get("TEST_REDIS_URL") or os.environ.get("REDIS_URL"):
        return env_val
    settings = _load_backend_env_settings()
    if settings.TEST_REDIS_URL is not None:
        return settings.TEST_REDIS_URL.get_secret_value()
    return settings.REDIS_URL.get_secret_value()
