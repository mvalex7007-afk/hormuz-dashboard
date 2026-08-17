"""CLI help and command wiring."""

from __future__ import annotations

from typer.testing import CliRunner

from ripple.cli.main import app

runner = CliRunner()


def test_cli_help() -> None:
    """``ripple --help`` lists the scaffold commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    stdout = result.stdout
    assert "ingest" in stdout
    assert "detect" in stdout
    assert "mature" in stdout
    assert "backtest" in stdout


def test_cli_commands_are_noops() -> None:
    """Scaffold commands exit 0 without touching live data."""
    for name in ("ingest", "detect", "mature", "backtest"):
        result = runner.invoke(app, [name])
        assert result.exit_code == 0, result.output
        assert "scaffold no-op" in result.stdout
