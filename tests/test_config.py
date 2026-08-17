"""Settings load without optional keys (cloud VMs boot without ``.env``)."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from ripple.config import OPTIONAL_ENV_KEYS, get_settings, reset_settings


def test_config_loads_with_missing_optional_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Missing optional keys warn; the process still starts."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    for key in OPTIONAL_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    reset_settings()
    caplog.set_level(logging.WARNING, logger="ripple.config")
    settings = get_settings()

    assert settings.grok_api_key is None
    assert settings.finnhub_api_key is None
    assert settings.database_url.startswith("postgresql+psycopg://")
    warned = " ".join(record.getMessage() for record in caplog.records)
    assert "GROK_API_KEY" in warned
    assert "FINNHUB_API_KEY" in warned
