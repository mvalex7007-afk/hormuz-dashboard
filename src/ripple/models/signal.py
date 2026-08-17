"""Append-only ``signals`` ledger."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from ripple.db.base import Base
from ripple.models.enums import PredictedDirection, VerificationStatus

if TYPE_CHECKING:
    from ripple.models.outcome import SignalOutcome

PREDICTION_COLUMNS: frozenset[str] = frozenset(
    {
        "event_type",
        "region",
        "chokepoint_id",
        "raw_source",
        "detection_ts",
        "predicted_instrument",
        "predicted_direction",
        "confidence",
        "baseline_value",
        "observed_value",
        "spike_score",
        "sources_json",
        "corroboration_json",
        "local_price_at_detection",
        "lead_lag_spread_at_detection",
    }
)


def _utc_now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(UTC)


class Signal(Base):
    """A single detection written once to the append-only ledger.

    Prediction columns listed in :data:`PREDICTION_COLUMNS` cannot be updated.
    Maturity results belong in :class:`~ripple.models.outcome.SignalOutcome`.
    """

    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    region: Mapped[str] = mapped_column(String(32), nullable=False)
    chokepoint_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_source: Mapped[str] = mapped_column(String(256), nullable=False)
    detection_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    predicted_instrument: Mapped[str] = mapped_column(String(32), nullable=False)
    predicted_direction: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=PredictedDirection.NEUTRAL.value,
    )
    confidence: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    baseline_value: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    observed_value: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    spike_score: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    sources_json: Mapped[list[Any]] = mapped_column(JSON, nullable=False)
    corroboration_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )
    verification_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=VerificationStatus.CANDIDATE.value,
        index=True,
    )
    local_price_at_detection: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True,
    )
    lead_lag_spread_at_detection: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    outcomes: Mapped[list[SignalOutcome]] = relationship(
        "SignalOutcome",
        back_populates="signal",
    )

    def __repr__(self) -> str:
        return (
            f"Signal(id={self.id!r}, event_type={self.event_type!r}, "
            f"instrument={self.predicted_instrument!r})"
        )
