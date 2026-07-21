import time

from UTILS.config import SIGNAL_CONTINUITY_GAP_SECONDS


# ==================================================
# SIGNAL HISTORY
# ==================================================

signal_history = {}
signal_first_seen = {}
signal_last_seen = {}

history_update_count = 0
seen_this_cycle = set()
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

    current_time = time.monotonic()
    previous_last_seen = signal_last_seen.get(
        frequency
    )

    if (
            previous_last_seen is None
            or current_time - previous_last_seen
            > SIGNAL_CONTINUITY_GAP_SECONDS
    ):
        signal_first_seen[
            frequency
        ] = current_time

    signal_last_seen[
        frequency
    ] = current_time

    if frequency in seen_this_cycle:
        age_seconds = int(
            current_time
            -
            signal_first_seen.get(
                frequency,
                current_time
            )
        )

        return (
            signal_history.get(
                frequency,
                0
            ),
            age_seconds
        )

    seen_this_cycle.add(
        frequency
    )

    if frequency not in signal_history:

        signal_history[
            frequency
        ] = 1

    else:

        signal_history[
            frequency
        ] += 1

    age_seconds = int(
        current_time
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

def get_seconds_since_seen(
        frequency
):
    frequency = round(
        frequency,
        1
    )

    last_seen = signal_last_seen.get(
        frequency
    )

    if last_seen is None:
        return None

    return max(
        0.0,
        time.monotonic()
        - last_seen
    )

def prune_stale_history(
        max_age_seconds
):
    if max_age_seconds < 0:
        raise ValueError(
            "Maximum signal history age cannot be negative."
        )

    current_time = time.monotonic()

    stale_frequencies = [
        frequency
        for frequency, last_seen in signal_last_seen.items()
        if (
                current_time
                - last_seen
                > max_age_seconds
        )
    ]

    for frequency in stale_frequencies:
        signal_history.pop(
            frequency,
            None
        )

        signal_first_seen.pop(
            frequency,
            None
        )

        signal_last_seen.pop(
            frequency,
            None
        )

        seen_this_cycle.discard(
            frequency
        )

    return len(
        stale_frequencies
    )

def increment_history_update_count():
    global history_update_count
    history_update_count += 1

def get_history_update_count():
    return history_update_count

def reset_cycle_tracking():
    seen_this_cycle.clear()

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
