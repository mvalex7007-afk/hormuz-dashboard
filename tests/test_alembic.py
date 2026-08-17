"""Alembic upgrade / downgrade against an empty SQLite database."""

from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from ripple.config import reset_settings

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_alembic_upgrade_then_downgrade_on_empty_db(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``upgrade head`` then ``downgrade base`` leave an empty catalog."""
    db_path = tmp_path / "empty.db"
    url = f"sqlite:///{db_path.resolve().as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    reset_settings()

    cfg = Config(str(REPO_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(REPO_ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)

    command.upgrade(cfg, "head")
    engine = create_engine(url, future=True)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
    assert {"signals", "signal_outcomes", "price_bars"} <= tables

    command.downgrade(cfg, "base")
    engine = create_engine(url, future=True)
    try:
        remaining = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
    remaining.discard("alembic_version")
    assert remaining == set()
