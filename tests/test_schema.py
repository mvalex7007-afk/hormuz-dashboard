"""Schema creation tests."""

from __future__ import annotations

from sqlalchemy import Engine, inspect

from ripple.models import Base


def test_schema_creates_ledger_tables(engine: Engine) -> None:
    """``Base.metadata.create_all`` builds signals, outcomes, and price bars."""
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert {"signals", "signal_outcomes", "price_bars"} <= tables

    signal_cols = {column["name"] for column in inspector.get_columns("signals")}
    assert {
        "id",
        "created_at",
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
        "verification_status",
        "local_price_at_detection",
        "lead_lag_spread_at_detection",
        "notes",
    } <= signal_cols

    outcome_cols = {
        column["name"] for column in inspector.get_columns("signal_outcomes")
    }
    assert {
        "signal_id",
        "horizon",
        "target_price_at_detection",
        "target_price_at_horizon",
        "pct_move",
        "label",
        "matured_at",
    } <= outcome_cols

    bar_cols = {column["name"] for column in inspector.get_columns("price_bars")}
    assert {
        "instrument",
        "ts",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
    } <= bar_cols
