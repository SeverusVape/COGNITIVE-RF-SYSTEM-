# ==================================================
# FUTURE COGNITIVE CLASSIFIER
# ==================================================
# Reserved for advanced classification using:
# - bandwidth
# - persistence
# - occupancy
# - signal history
#
# Currently not used by production UI.



def classify_signal_type(
        feature
):

    freq = feature.frequency

    if 88 <= freq <= 108:
        return "FM Broadcast"

    if 118 <= freq <= 137:
        return "Airband"

    if 144 <= freq <= 148:
        return "Amateur 2m"

    if 162.4 <= freq <= 162.6:
        return "NOAA Weather"

    if 420 <= freq <= 450:
        return "Amateur 70cm"

    if 462 <= freq <= 467:
        return "GMRS"

    return "Unknown"