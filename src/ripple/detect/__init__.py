"""Detection, maturity, and backtest entrypoints."""

from ripple.detect.backtest import run_backtest
from ripple.detect.engine import run_detect
from ripple.detect.mature import run_mature

__all__ = ["run_backtest", "run_detect", "run_mature"]
