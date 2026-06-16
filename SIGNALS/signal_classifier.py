# ==================================================
# SIGNAL CLASSIFIER
# ==================================================

def classify_signal(
        power,
        frequency=None
):

    if power > 60:
        strength = "S"

    elif power > 45:
        strength = "M"

    else:
        strength = "W"

    band = None

    if frequency is not None:

        if 88 <= frequency <= 108:
            band = "FM Broadcast"

        elif 118 <= frequency <= 137:
            band = "Aircraft"

        elif 144 <= frequency <= 148:
            band = "2m Amateur"

        elif 162 <= frequency <= 163:
            band = "NOAA Weather"

        elif 420 <= frequency <= 450:
            band = "70cm Amateur"

        elif 462 <= frequency <= 468:
            band = "GMRS"

    if band is not None:
        return f"{band} [{strength}]"

    return f"Unknown RF [{strength}]"