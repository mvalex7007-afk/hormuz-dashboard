"""Abstract verifier interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any


class Verifier(ABC):
    """Assign ``verification_status`` for a candidate signal.

    Verifiers may update ``verification_status`` and ``notes`` only. They must
    not rewrite prediction columns on the append-only ledger.
    """

    @abstractmethod
    def verify(
        self,
        signal: Mapping[str, Any],
        sources: Sequence[Mapping[str, Any]],
    ) -> str:
        """Return ``candidate``, ``verified``, or ``unverified``.

        Args:
            signal: Ledger fields for the candidate (read-only view).
            sources: Source payloads with ``tier`` metadata.

        Returns:
            A :class:`~ripple.models.enums.VerificationStatus` value.
        """
