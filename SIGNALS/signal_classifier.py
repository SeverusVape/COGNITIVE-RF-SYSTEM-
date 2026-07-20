import math
from numbers import Real

from SIGNALS.frequency_band import (
    classify_frequency_band
)
from UTILS.config import (
    SIGNAL_STRENGTH_MEDIUM_PROMINENCE_DB,
    SIGNAL_STRENGTH_STRONG_PROMINENCE_DB
)


# ==================================================
# SIGNAL CLASSIFIER
# ==================================================

def classify_signal(
        power,
        frequency=None,
        history_count=1
):
    strength = classify_strength(
        power
    )

    persistence = classify_persistence(
        history_count
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
        history_count
):
    if history_count >= 20:
        return "L"

    if history_count >= 10:
        return "P"

    if history_count >= 5:
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


def calculate_peak_prominence_db(
        peak_power_db,
        noise_floor_db
):
    for name, value in (
            ("Peak power", peak_power_db),
            ("Noise floor", noise_floor_db)
    ):
        if (
                isinstance(value, bool)
                or not isinstance(
                    value,
                    Real
                )
                or not math.isfinite(value)
        ):
            raise ValueError(
                f"{name} must be a finite number."
            )

    return float(
        peak_power_db
        - noise_floor_db
    )


def classify_relative_strength(
        peak_power_db,
        noise_floor_db
):
    prominence_db = calculate_peak_prominence_db(
        peak_power_db,
        noise_floor_db
    )

    if (
            prominence_db
            >= SIGNAL_STRENGTH_STRONG_PROMINENCE_DB
    ):
        return "S"

    if (
            prominence_db
            >= SIGNAL_STRENGTH_MEDIUM_PROMINENCE_DB
    ):
        return "M"

    return "W"
