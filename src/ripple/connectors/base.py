"""Abstract source-connector interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

import httpx

from ripple.config.settings import Settings, get_settings


class SourceConnector(ABC):
    """Fetch raw events from a registered source.

    Implementations must not mutate the ``signals`` ledger. This scaffold
    ships the interface only — no live HTTP calls are performed by default.
    """

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Stable id matching ``configs/source_registry.yaml``."""

    @property
    @abstractmethod
    def tier(self) -> str:
        """Trust tier: OFFICIAL, WIRE, outlet, aggregator, or social."""

    @abstractmethod
    async def fetch(self, since: datetime | None = None) -> Sequence[Mapping[str, Any]]:
        """Return raw payloads newer than ``since`` (UTC).

        Args:
            since: Exclusive lower bound in UTC. ``None`` means connector default.

        Returns:
            A sequence of JSON-serializable mappings. Each mapping should
            include enough metadata to populate ``sources_json`` tiers later.
        """


def create_http_client(
    settings: Settings | None = None,
    timeout: float | None = None,
) -> httpx.Client:
    """Build a shared httpx client.

    The scaffold never issues requests; this is the seam later connectors use.
    """
    cfg = settings or get_settings()
    seconds = timeout if timeout is not None else cfg.http_timeout_seconds
    return httpx.Client(timeout=seconds)
