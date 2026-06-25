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

    if history_count >= 20:
        persistence = "L"

    elif history_count >= 10:
        persistence = "P"

    elif history_count >= 5:
        persistence = "A"

    else:
        persistence = None

    band = None

    if frequency is not None:

        if 88 <= frequency <= 108:

            if power > 60:
                band = "BC"

            else:
                band = "FM"

        elif 118 <= frequency <= 137:
            band = "AIRBND"

        elif 144 <= frequency <= 148:
            band = "2m"

        elif 162 <= frequency <= 163:
            band = "NOAA"

        elif 420 <= frequency <= 450:
            band = "70cm"

        elif 462 <= frequency <= 468:
            band = "GMRS"

    if band is None:
        band = "Unknown"

    return (
        band,
        strength,
        persistence
    )

def classify_strength(
        power
):

    if power > 60:
        return "S"

    elif power > 45:
        return "M"

    else:
        return "W"