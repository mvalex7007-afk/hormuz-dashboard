"""``signal_outcomes`` — maturity results kept off the immutable ledger."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ripple.db.base import Base

if TYPE_CHECKING:
    from ripple.models.signal import Signal


def _utc_now() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(UTC)


class SignalOutcome(Base):
    """Evaluated result of a signal at a single horizon.

    Written to a separate table so the original ``signals`` row stays immutable.
    """

    __tablename__ = "signal_outcomes"
    __table_args__ = (
        UniqueConstraint(
            "signal_id",
            "horizon",
            name="uq_signal_outcomes_signal_horizon",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    signal_id: Mapped[int] = mapped_column(
        ForeignKey("signals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    horizon: Mapped[str] = mapped_column(String(8), nullable=False)
    target_price_at_detection: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )
    target_price_at_horizon: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True,
    )
    pct_move: Mapped[Decimal | None] = mapped_column(Numeric(12, 6), nullable=True)
    label: Mapped[str | None] = mapped_column(String(16), nullable=True)
    matured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utc_now,
    )

    signal: Mapped[Signal] = relationship("Signal", back_populates="outcomes")

    def __repr__(self) -> str:
        return (
            f"SignalOutcome(id={self.id!r}, signal_id={self.signal_id!r}, "
            f"horizon={self.horizon!r}, label={self.label!r})"
        )
