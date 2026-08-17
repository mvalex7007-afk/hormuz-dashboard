"""Typer CLI: ``ripple ingest|detect|mature|backtest``."""

from __future__ import annotations

import typer

from ripple import __version__
from ripple.config import configure_logging, get_settings
from ripple.connectors import run_ingest
from ripple.detect import run_backtest, run_detect, run_mature

app = typer.Typer(
    name="ripple",
    help="Hormuz-Dashboard / ripple - early-warning market-signal service.",
    no_args_is_help=True,
)


@app.callback()
def _main() -> None:
    """Load settings (warns on missing optional keys; never crashes)."""
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def ingest() -> None:
    """Ingest raw source events (scaffold no-op)."""
    run_ingest()
    typer.echo("ingest: scaffold no-op")


@app.command()
def detect() -> None:
    """Detect candidate signals (scaffold no-op)."""
    run_detect()
    typer.echo("detect: scaffold no-op")


@app.command()
def mature() -> None:
    """Mature signal outcomes at 1h / 1d / 1w (scaffold no-op)."""
    run_mature()
    typer.echo("mature: scaffold no-op")


@app.command()
def backtest() -> None:
    """Replay detections against stored bars (scaffold no-op)."""
    run_backtest()
    typer.echo("backtest: scaffold no-op")


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
