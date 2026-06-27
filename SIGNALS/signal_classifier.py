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
        persistence = "L" # LONG TERM

    elif history_count >= 10:
        persistence = "P" # Persistent

    elif history_count >= 5:
        persistence = "A" # Active

    else:
        persistence = None

    band = None

    if frequency is not None:

        if 88 <= frequency <= 108:

            if power > 60:
                band = "BC-STR" # strong broadcast signal

            else:
                band = "BC" # broadcast signal

        elif 118 <= frequency <= 137:
            band = "AIRBND"

        elif 144 <= frequency <= 148:
            if frequency >= 146:
                band = "2m-RPT"
            else:
                band = "2m"

        elif 162.4 <= frequency <= 162.6:
            band = "NOAA" # likely NOAA weather channel

        elif 162 <= frequency <= 163:
            band = "WX" # weather-band area but not exact NOAA frequency

        elif 420 <= frequency <= 450:
            if frequency >= 440:
                band = "70cm-RPT" # likely repeater activity
            else:
                band = "70cm" # general 70cm activity

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