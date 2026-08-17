"""ORM event listeners that enforce the append-only signals ledger."""

from __future__ import annotations

from sqlalchemy import event, inspect
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper

from ripple.exceptions import ImmutableLedgerError
from ripple.models.signal import PREDICTION_COLUMNS, Signal


@event.listens_for(Signal, "before_update")
def reject_prediction_column_updates(
    _mapper: Mapper[Signal],
    _connection: Connection,
    target: Signal,
) -> None:
    """Reject UPDATEs that touch prediction columns on ``signals``.

    The ledger is append-only. Outcomes live in ``signal_outcomes`` so the
    original prediction is never rewritten. ``verification_status`` and
    ``notes`` remain mutable for workflow annotation.
    """
    state = inspect(target)
    changed = [
        column
        for column in PREDICTION_COLUMNS
        if state.attrs[column].history.has_changes()
    ]
    if changed:
        raise ImmutableLedgerError(
            "signals is an append-only ledger; "
            f"cannot update prediction columns: {', '.join(sorted(changed))}"
        )
