from SIGNALS.frequency_band import (
    classify_frequency_band
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
