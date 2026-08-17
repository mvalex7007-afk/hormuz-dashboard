"""The signals ledger rejects updates to prediction columns."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from ripple.exceptions import ImmutableLedgerError
from ripple.models import Signal, VerificationStatus


def _candidate(session: Session) -> Signal:
    """Insert a minimal candidate signal and return the persistent instance."""
    signal = Signal(
        event_type="earthquake",
        region="TW",
        chokepoint_id="taiwan_tsmc",
        raw_source="cwa_earthquake",
        detection_ts=datetime(2026, 8, 16, 12, 0, tzinfo=UTC),
        predicted_instrument="2330.TW",
        predicted_direction="down",
        confidence=Decimal("0.7200"),
        baseline_value=Decimal("980.000000"),
        observed_value=Decimal("965.000000"),
        spike_score=Decimal("1.850000"),
        sources_json=[
            {
                "id": "cwa_earthquake",
                "tier": "OFFICIAL",
                "url": "https://www.cwa.gov.tw/V8/E/E/index.html",
            }
        ],
        corroboration_json=None,
        verification_status=VerificationStatus.CANDIDATE.value,
        local_price_at_detection=Decimal("965.000000"),
        lead_lag_spread_at_detection=Decimal("0.012000"),
        notes=None,
    )
    session.add(signal)
    session.commit()
    return signal


def test_ledger_rejects_prediction_column_updates(session: Session) -> None:
    """Updating ``predicted_direction`` (a prediction column) is rejected."""
    signal = _candidate(session)
    signal.predicted_direction = "up"
    with pytest.raises(ImmutableLedgerError, match="predicted_direction"):
        session.commit()
    session.rollback()


def test_ledger_rejects_confidence_update(session: Session) -> None:
    """Updating ``confidence`` is rejected."""
    signal = _candidate(session)
    signal.confidence = Decimal("0.9900")
    with pytest.raises(ImmutableLedgerError, match="confidence"):
        session.commit()
    session.rollback()


def test_notes_and_verification_status_remain_mutable(session: Session) -> None:
    """Workflow fields are not prediction columns and may be updated."""
    signal = _candidate(session)
    signal.verification_status = VerificationStatus.VERIFIED.value
    signal.notes = "verified against CWA official page"
    session.commit()
    session.refresh(signal)
    assert signal.verification_status == VerificationStatus.VERIFIED.value
    assert signal.notes is not None
