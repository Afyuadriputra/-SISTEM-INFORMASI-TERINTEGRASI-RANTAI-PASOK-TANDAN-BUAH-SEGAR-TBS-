"""Async Alembic environment importing canonical metadata cleanly from app.core.database."""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core import audit as _audit_models  # noqa: F401
from app.core import idempotency as _idempotency_models  # noqa: F401
from app.core import system_rules as _system_rule_models  # noqa: F401
from app.core.config import get_settings
from app.core.database import Base
from app.modules.contracts.infrastructure import models as _contract_models  # noqa: F401
from app.modules.files.infrastructure import models as _file_models  # noqa: F401
from app.modules.finance.infrastructure import models as _finance_models  # noqa: F401
from app.modules.identity_access.infrastructure import models as _identity_models  # noqa: F401
from app.modules.logistics.infrastructure import models as _logistics_models  # noqa: F401
from app.modules.master_data.infrastructure import models as _master_data_models  # noqa: F401
from app.modules.mill_weighing.infrastructure import models as _mill_weighing_models  # noqa: F401
from app.modules.pricing.infrastructure import models as _pricing_models  # noqa: F401
from app.modules.public_portal.infrastructure import models as _public_models  # noqa: F401
from app.modules.reconciliation.infrastructure import models as _rec_models  # noqa: F401
from app.modules.tbs_receiving.infrastructure import models as _tbs_models  # noqa: F401

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    override = config.get_main_option("sqlalchemy.url")
    if override and not override.startswith("driver://"):
        return override
    return get_settings().async_database_url


def run_migrations_offline() -> None:
    """Run migrations in offline SQL generation mode."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations asynchronously using Psycopg 3 driver."""
    cfg_section = config.get_section(config.config_ini_section, {})
    cfg_section["sqlalchemy.url"] = get_database_url()
    connectable = async_engine_from_config(
        cfg_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
