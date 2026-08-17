"""Abstract corroborator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any


class Corroborator(ABC):
    """Cross-check a detection against independent sources.

    The result is stored on insert as ``corroboration_json``. Later updates
    to that column are rejected by the ledger listener.
    """

    @abstractmethod
    def corroborate(
        self,
        event: Mapping[str, Any],
        sources: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        """Return a JSON-serializable corroboration mapping.

        Args:
            event: Detection context (event type, region, chokepoint).
            sources: Independent source payloads, each with a ``tier``.

        Returns:
            A mapping suitable for ``signals.corroboration_json``.
        """
