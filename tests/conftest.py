"""Shared fixtures. Tests use SQLite so they run without Postgres."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ripple.config import reset_settings
from ripple.models import Base


@pytest.fixture(autouse=True)
def _isolate_settings() -> Generator[None, None, None]:
    """Prevent settings cache from leaking across tests."""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    """In-memory SQLite engine with a shared connection pool."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    """ORM session bound to the in-memory engine after ``create_all``."""
    Base.metadata.create_all(engine)
    factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
    with factory() as db_session:
        yield db_session
