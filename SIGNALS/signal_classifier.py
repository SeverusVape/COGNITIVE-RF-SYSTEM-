import math
from numbers import Real

from SIGNALS.frequency_band import (
    classify_frequency_band
)
from UTILS.config import (
    SIGNAL_PERSISTENCE_ACTIVE_SECONDS,
    SIGNAL_PERSISTENCE_LONG_SECONDS,
    SIGNAL_PERSISTENCE_PERSISTENT_SECONDS
)


# ==================================================
# SIGNAL CLASSIFIER
# ==================================================

def classify_signal(
        power,
        frequency=None,
        observed_seconds=0.0
):
    strength = classify_strength(
        power
    )

    persistence = classify_persistence(
        observed_seconds
    )

    band = classify_frequency_band(
        frequency
    )

    return (
        band,
        strength,
        persistence
    )


def classify_persistence(
        observed_seconds
):
    if (
            isinstance(observed_seconds, bool)
            or not isinstance(
                observed_seconds,
                Real
            )
            or not math.isfinite(observed_seconds)
            or observed_seconds < 0
    ):
        raise ValueError(
            "Observed duration must be a finite, "
            "non-negative number."
        )

    if observed_seconds >= SIGNAL_PERSISTENCE_LONG_SECONDS:
        return "L"

    if (
            observed_seconds
            >= SIGNAL_PERSISTENCE_PERSISTENT_SECONDS
    ):
        return "P"

    if observed_seconds >= SIGNAL_PERSISTENCE_ACTIVE_SECONDS:
        return "A"

    return "N"


def classify_strength(
        power
):

    if power > 60:
        return "S"

    elif power > 45:
        return "M"

    else:
        return "W"
