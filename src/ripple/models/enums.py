"""String enums persisted as VARCHAR for Postgres and SQLite portability."""

from enum import StrEnum


class VerificationStatus(StrEnum):
    """Lifecycle of a ledger row. Outcomes never rewrite these values."""

    CANDIDATE = "candidate"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"


class Horizon(StrEnum):
    """Outcome evaluation windows."""

    H1 = "1h"
    D1 = "1d"
    W1 = "1w"


class OutcomeLabel(StrEnum):
    """Post-hoc label written only to ``signal_outcomes``."""

    TP = "TP"
    FP = "FP"
    TIMING = "timing"
    MISS = "miss"


class PredictedDirection(StrEnum):
    """Predicted move of the leading instrument."""

    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class SourceTier(StrEnum):
    """Source-registry tiers, highest trust first."""

    OFFICIAL = "OFFICIAL"
    WIRE = "WIRE"
    OUTLET = "outlet"
    AGGREGATOR = "aggregator"
    SOCIAL = "social"
