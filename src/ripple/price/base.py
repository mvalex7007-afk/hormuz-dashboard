"""Abstract price-provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any

import pandas as pd


class PriceProvider(ABC):
    """Supply OHLCV observations for instruments.

    Implementations persist into ``price_bars``. This scaffold does not
    call any market-data vendor.
    """

    @abstractmethod
    def get_price(self, instrument: str, ts: datetime) -> Decimal | None:
        """Return the last close at or before ``ts`` (UTC), if known."""

    @abstractmethod
    def get_bar(self, instrument: str, ts: datetime) -> Mapping[str, Any] | None:
        """Return a single OHLCV mapping at ``ts`` (UTC), if known."""

    @abstractmethod
    def get_bars(
        self,
        instrument: str,
        start: datetime,
        end: datetime,
    ) -> Sequence[Mapping[str, Any]]:
        """Return bars in ``[start, end]`` (UTC, inclusive)."""


def bars_to_frame(bars: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Convert bar mappings to a :class:`pandas.DataFrame`.

    Scaffold helper for later detection / backtest code.
    """
    return pd.DataFrame(list(bars))
