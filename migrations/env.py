"""Alembic environment. Database URL comes from pydantic-settings."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from ripple.config import get_settings
from ripple.db.base import Base
from ripple.models import PriceBar, Signal, SignalOutcome  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _sqlalchemy_url() -> str:
    """Resolve the database URL at runtime so tests can override it."""
    return get_settings().database_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL script emission)."""
    context.configure(
        url=_sqlalchemy_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""
    configuration = dict(config.get_section(config.config_ini_section, {}) or {})
    configuration["sqlalchemy.url"] = _sqlalchemy_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
