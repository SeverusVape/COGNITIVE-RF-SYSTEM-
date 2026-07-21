import time
import math

from collections import deque
from numbers import Real

from UTILS.config import (
    SIGNAL_CONTINUITY_GAP_SECONDS,
    SIGNAL_DUTY_CYCLE_WINDOW_SECONDS
)


# ==================================================
# SIGNAL HISTORY
# ==================================================

signal_history = {}
signal_first_seen = {}
signal_last_seen = {}

history_update_count = 0
seen_this_cycle = set()
duty_cycle_frames = deque()
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


def _prune_duty_cycle_frames(
        current_time,
        window_seconds
):
    while (
            duty_cycle_frames
            and current_time - duty_cycle_frames[0][0]
            > window_seconds
    ):
        duty_cycle_frames.popleft()


def record_duty_cycle_frame(
        frequencies,
        window_seconds=SIGNAL_DUTY_CYCLE_WINDOW_SECONDS
):
    if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, Real)
            or not math.isfinite(window_seconds)
            or window_seconds <= 0
    ):
        raise ValueError(
            "Duty-cycle window must be a finite, "
            "positive number."
        )

    normalized_frequencies = set()

    for frequency in frequencies:
        if (
                isinstance(frequency, bool)
                or not isinstance(frequency, Real)
                or not math.isfinite(frequency)
        ):
            raise ValueError(
                "Duty-cycle frequencies must be finite numbers."
            )

        normalized_frequencies.add(
            round(float(frequency), 1)
        )

    current_time = time.monotonic()

    duty_cycle_frames.append(
        (
            current_time,
            frozenset(normalized_frequencies)
        )
    )

    _prune_duty_cycle_frames(
        current_time,
        float(window_seconds)
    )


def get_duty_cycle_percent(
        frequency,
        window_seconds=SIGNAL_DUTY_CYCLE_WINDOW_SECONDS
):
    if (
            isinstance(frequency, bool)
            or not isinstance(frequency, Real)
            or not math.isfinite(frequency)
    ):
        raise ValueError(
            "Duty-cycle frequency must be a finite number."
        )

    if (
            isinstance(window_seconds, bool)
            or not isinstance(window_seconds, Real)
            or not math.isfinite(window_seconds)
            or window_seconds <= 0
    ):
        raise ValueError(
            "Duty-cycle window must be a finite, "
            "positive number."
        )

    current_time = time.monotonic()

    _prune_duty_cycle_frames(
        current_time,
        float(window_seconds)
    )

    if not duty_cycle_frames:
        return 0.0

    normalized_frequency = round(
        float(frequency),
        1
    )

    detected_frames = sum(
        normalized_frequency in frame_frequencies
        for _, frame_frequencies in duty_cycle_frames
    )

    return round(
        detected_frames
        / len(duty_cycle_frames)
        * 100,
        1
    )


def reset_duty_cycle_tracking():
    duty_cycle_frames.clear()

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
