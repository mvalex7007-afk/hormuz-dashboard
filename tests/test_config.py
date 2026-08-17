"""Settings load without optional keys (cloud VMs boot without ``.env``)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ripple.config import OPTIONAL_ENV_KEYS, Settings, get_settings, reset_settings


def test_config_loads_with_missing_optional_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing optional keys do not prevent startup."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    for key in OPTIONAL_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    reset_settings()
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.grok_api_key is None
    assert settings.finnhub_api_key is None
    assert settings.database_url.startswith("postgresql+psycopg://")
    missing = settings.missing_optional_keys()
    assert "GROK_API_KEY" in missing
    assert "FINNHUB_API_KEY" in missing
