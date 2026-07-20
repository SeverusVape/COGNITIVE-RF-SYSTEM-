from SIGNALS.frequency_band import (
    get_frequency_band_context
)


# ==================================================
# FEATURE BAND CONTEXT
# ==================================================
# This returns frequency-allocation context for stored features. It does not
# claim modulation recognition or verified transmitter identification.

def classify_signal_type(
        feature
):

    return get_frequency_band_context(
        feature.frequency
    ).name
