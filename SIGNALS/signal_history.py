import time


# ==================================================
# SIGNAL HISTORY
# ==================================================

signal_history = {}
signal_first_seen = {}

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

    if frequency not in signal_first_seen:
        signal_first_seen[
            frequency
        ] = time.time()

    if frequency not in signal_history:

        signal_history[
            frequency
        ] = 1

    else:

        signal_history[
            frequency
        ] += 1

    age_seconds = int(
        time.time()
        -
        signal_first_seen[
            frequency
        ]
    )

    return (
        signal_history[
            frequency
        ],
        age_seconds
    )