"""OHLCV ``price_bars`` used for detection baselines and outcome maturity."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ripple.db.base import Base


class PriceBar(Base):
    """A single OHLCV bar for an instrument.

    ``ts`` is stored timezone-aware and must be UTC.
    """

    __tablename__ = "price_bars"
    __table_args__ = (
        UniqueConstraint(
            "instrument",
            "ts",
            "source",
            name="uq_price_bars_instrument_ts_source",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instrument: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    open: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(24, 6), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)

    def __repr__(self) -> str:
        return (
            f"PriceBar(instrument={self.instrument!r}, "
            f"ts={self.ts!r}, close={self.close!r})"
        )
