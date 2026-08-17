"""Grok-backed corroborator seam (not implemented)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ripple.corroborate.base import Corroborator


class GrokCorroborator(Corroborator):
    """Placeholder for xAI Grok corroboration.

    Wired so later PRs can implement live calls without changing callers.
    """

    def corroborate(
        self,
        event: Mapping[str, Any],
        sources: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        """Raise until live Grok corroboration is implemented.

        Args:
            event: Detection context (unused in the scaffold).
            sources: Independent source payloads (unused in the scaffold).

        Raises:
            NotImplementedError: Always. This class is an integration seam.
        """
        raise NotImplementedError(
            "GrokCorroborator is a scaffold seam; "
            "live corroboration is not implemented."
        )
