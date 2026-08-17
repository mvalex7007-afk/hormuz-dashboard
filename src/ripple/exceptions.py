"""Domain exceptions for the ripple scaffold."""


class ImmutableLedgerError(RuntimeError):
    """Raised when an append-only ``signals`` prediction column is mutated."""
