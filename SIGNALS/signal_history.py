# ==================================================
# SIGNAL HISTORY
# ==================================================

signal_history = {}

# ==================================================
# UPDATE HISTORY
# ==================================================

def update_signal_history(
        frequency
):

    frequency = round(
        frequency,
        1
    )

    if frequency not in signal_history:

        signal_history[
            frequency
        ] = 1

    else:

        signal_history[
            frequency
        ] += 1

    return signal_history[
        frequency
    ]