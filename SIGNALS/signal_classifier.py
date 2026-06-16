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
    persistent = (
            history_count >= 10
    )

    band = None

    if frequency is not None:

        if 88 <= frequency <= 108:

            if power > 60:
                return "Broadcast Station [S]"

            elif power > 45:
                return "FM Broadcast [M]"

            else:
                return "FM Broadcast [W]"

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

        if persistent:
            return (
                f"{band} "
                f"[{strength}] "
                f"(Persistent)"
            )

        return f"{band} [{strength}]"

    if persistent:
        return (
            f"Unknown RF "
            f"[{strength}] "
            f"(Persistent)"
        )

    return f"Unknown RF [{strength}]"


def classify_strength(
        power
):

    if power > 60:
        return "S"

    elif power > 45:
        return "M"

    else:
        return "W"