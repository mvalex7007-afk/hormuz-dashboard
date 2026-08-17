"""YAML config loaders for the source registry and chokepoint map."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from ripple.config.settings import Settings, get_settings


def _read_yaml(path: Path) -> dict[str, Any]:
    """Load a mapping from ``path``.

    Args:
        path: Filesystem path to a YAML document.

    Returns:
        The decoded mapping.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If the document is not a mapping.
    """
    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a mapping in {path}, got {type(payload)!r}")
    return cast(dict[str, Any], payload)


def load_source_registry(
    path: str | Path | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Load ``configs/source_registry.yaml`` (or an override path)."""
    cfg = settings or get_settings()
    resolved = Path(path) if path is not None else Path(cfg.source_registry_path)
    return _read_yaml(resolved)


def load_chokepoints(
    path: str | Path | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Load ``configs/chokepoints.yaml`` (or an override path)."""
    cfg = settings or get_settings()
    resolved = Path(path) if path is not None else Path(cfg.chokepoints_path)
    return _read_yaml(resolved)
