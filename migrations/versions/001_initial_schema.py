"""Initial schema: signals, signal_outcomes, price_bars.

Revision ID: 001_initial
Revises:
Create Date: 2026-08-17
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the append-only ledger, outcomes, and price bars."""
    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("region", sa.String(length=32), nullable=False),
        sa.Column("chokepoint_id", sa.String(length=64), nullable=False),
        sa.Column("raw_source", sa.String(length=256), nullable=False),
        sa.Column("detection_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("predicted_instrument", sa.String(length=32), nullable=False),
        sa.Column("predicted_direction", sa.String(length=16), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=8, scale=4), nullable=False),
        sa.Column("baseline_value", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("observed_value", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("spike_score", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("sources_json", sa.JSON(), nullable=False),
        sa.Column("corroboration_json", sa.JSON(), nullable=True),
        sa.Column("verification_status", sa.String(length=32), nullable=False),
        sa.Column("local_price_at_detection", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("lead_lag_spread_at_detection", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_signals_chokepoint_id", "signals", ["chokepoint_id"])
    op.create_index("ix_signals_detection_ts", "signals", ["detection_ts"])
    op.create_index("ix_signals_verification_status", "signals", ["verification_status"])

    op.create_table(
        "signal_outcomes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=False),
        sa.Column("horizon", sa.String(length=8), nullable=False),
        sa.Column("target_price_at_detection", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("target_price_at_horizon", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("pct_move", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("label", sa.String(length=16), nullable=True),
        sa.Column("matured_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("signal_id", "horizon", name="uq_signal_outcomes_signal_horizon"),
    )
    op.create_index("ix_signal_outcomes_signal_id", "signal_outcomes", ["signal_id"])

    op.create_table(
        "price_bars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instrument", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("high", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("low", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("close", sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column("volume", sa.Numeric(precision=24, scale=6), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "instrument",
            "ts",
            "source",
            name="uq_price_bars_instrument_ts_source",
        ),
    )
    op.create_index("ix_price_bars_instrument", "price_bars", ["instrument"])
    op.create_index("ix_price_bars_ts", "price_bars", ["ts"])


def downgrade() -> None:
    """Drop tables in reverse dependency order."""
    op.drop_index("ix_price_bars_ts", table_name="price_bars")
    op.drop_index("ix_price_bars_instrument", table_name="price_bars")
    op.drop_table("price_bars")

    op.drop_index("ix_signal_outcomes_signal_id", table_name="signal_outcomes")
    op.drop_table("signal_outcomes")

    op.drop_index("ix_signals_verification_status", table_name="signals")
    op.drop_index("ix_signals_detection_ts", table_name="signals")
    op.drop_index("ix_signals_chokepoint_id", table_name="signals")
    op.drop_table("signals")
