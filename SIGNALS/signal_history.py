import time


# ==================================================
# SIGNAL HISTORY
# ==================================================

signal_history = {}
signal_first_seen = {}

history_update_count = 0

# ==================================================
# UPDATE HISTORY
# ==================================================

def update_signal_history(
        frequency
):
    global history_update_count
    history_update_count += 1

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

def get_history_update_count():
    return history_update_count

def get_occupancy_percent(
        frequency
):

    frequency = round(
        frequency,
        1
    )

    if frequency not in signal_history:
        return 0.0

    if history_update_count == 0:
        return 0.0

    return round(
        (
            signal_history[
                frequency
            ]
            /
            history_update_count
        )
        * 100,
        1
    )