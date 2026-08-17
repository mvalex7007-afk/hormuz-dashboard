"""Engine and session factories."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from ripple.config.settings import Settings, get_settings


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    """SQLite disables FK enforcement unless PRAGMA foreign_keys=ON."""

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(
        dbapi_connection: object,
        _connection_record: object,
    ) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_engine(settings: Settings | None = None) -> Engine:
    """Create a SQLAlchemy engine from settings.

    Args:
        settings: Optional settings override. Defaults to :func:`get_settings`.

    Returns:
        A future-style :class:`~sqlalchemy.Engine`.
    """
    cfg = settings or get_settings()
    engine = create_engine(cfg.database_url, future=True)
    if cfg.database_url.startswith("sqlite"):
        _enable_sqlite_foreign_keys(engine)
    return engine


def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a sessionmaker bound to ``engine``."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )
