"""PostgreSQL async engine, bounded pool management, ORM Base, and session factory."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger("app.core.database")

POSTGRES_NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Canonical SQLAlchemy declarative base shared across domain infrastructure models."""

    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)


def build_async_engine(settings: Settings, *, dsn_override: str | None = None) -> AsyncEngine:
    """Create bounded async SQLAlchemy engine configured for Psycopg 3."""
    dsn = dsn_override if dsn_override is not None else settings.async_database_url
    return create_async_engine(
        dsn,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT_SECONDS,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": settings.DB_CONNECT_TIMEOUT_SECONDS,
            "options": f"-c statement_timeout={settings.DB_STATEMENT_TIMEOUT_MS}",
        },
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create non-expiring async session factory tied to the given engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


async def ping_database(engine: AsyncEngine) -> bool:
    """Verify live SQL connectivity via SELECT 1 with safe error redaction."""
    started = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.error(
            "postgres_readiness_failed",
            extra={
                "structured": {
                    "event": "dependency_check_failed",
                    "dependency": "postgresql",
                    "error_class": exc.__class__.__name__,
                    "duration_ms": elapsed_ms,
                }
            },
        )
        return False


@asynccontextmanager
async def session_scope(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Yield a transactional AsyncSession with explicit rollback on unhandled errors."""
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_database(engine: AsyncEngine) -> None:
    """Cleanly close pooled PostgreSQL connections on shutdown."""
    await engine.dispose()
