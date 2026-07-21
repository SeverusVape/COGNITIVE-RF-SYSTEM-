# IMPORTS =======================================
import time
import math

from dataclasses import dataclass
from collections import deque
from numbers import Real
from statistics import median

from SIGNALS.signal_type_classifier import (
    classify_signal_type
)
from UTILS.config import (
    BANDWIDTH_STABILITY_MIN_SAMPLES,
    FREQUENCY_STABILITY_MIN_SAMPLES,
    FREQUENCY_STABILITY_REFERENCE_KHZ
)
# ================================================

@dataclass
class SignalFeatures:
    frequency: float
    peak_power: float
    average_power: float
    bandwidth_khz: float
    occupancy_percent: float
    age_seconds: float
    strength: str
    persistence: str
    signal_type: str = "Unknown"
    last_seen: float = 0.0
    bandwidth_stability: float | None = None
    bandwidth_observations: int = 0
    frequency_drift_khz: float | None = None
    frequency_stability: float | None = None
    frequency_observations: int = 0
    duty_cycle_percent: float = 0.0


def calculate_bandwidth_stability(
        bandwidth_values,
        minimum_samples=BANDWIDTH_STABILITY_MIN_SAMPLES
):
    if (
            isinstance(minimum_samples, bool)
            or not isinstance(minimum_samples, int)
            or minimum_samples < 2
    ):
        raise ValueError(
            "Minimum bandwidth samples must be an integer "
            "greater than or equal to two."
        )

    values = list(
        bandwidth_values
    )

    for value in values:
        if (
                isinstance(value, bool)
                or not isinstance(value, Real)
                or not math.isfinite(value)
                or value < 0
        ):
            raise ValueError(
                "Bandwidth values must be finite, "
                "non-negative numbers."
            )

    if len(values) < minimum_samples:
        return None

    median_bandwidth = float(
        median(values)
    )

    if median_bandwidth == 0:
        return (
            1.0
            if all(value == 0 for value in values)
            else 0.0
        )

    median_deviation = float(
        median(
            abs(value - median_bandwidth)
            for value in values
        )
    )

    return max(
        0.0,
        1.0
        - min(
            median_deviation
            / median_bandwidth,
            1.0
        )
    )


def calculate_frequency_stability(
        frequency_values,
        minimum_samples=FREQUENCY_STABILITY_MIN_SAMPLES,
        reference_khz=FREQUENCY_STABILITY_REFERENCE_KHZ
):
    if (
            isinstance(minimum_samples, bool)
            or not isinstance(minimum_samples, int)
            or minimum_samples < 2
    ):
        raise ValueError(
            "Minimum frequency samples must be an integer "
            "greater than or equal to two."
        )

    if (
            isinstance(reference_khz, bool)
            or not isinstance(reference_khz, Real)
            or not math.isfinite(reference_khz)
            or reference_khz <= 0
    ):
        raise ValueError(
            "Frequency stability reference must be a finite, "
            "positive number."
        )

    values = list(
        frequency_values
    )

    for value in values:
        if (
                isinstance(value, bool)
                or not isinstance(value, Real)
                or not math.isfinite(value)
                or value <= 0
        ):
            raise ValueError(
                "Frequency values must be finite, "
                "positive numbers."
            )

    if len(values) < minimum_samples:
        return None

    median_frequency = float(
        median(values)
    )

    drift_khz = float(
        median(
            abs(value - median_frequency)
            for value in values
        )
        * 1000
    )

    stability = max(
        0.0,
        1.0
        - min(
            drift_khz
            / reference_khz,
            1.0
        )
    )

    return (
        round(drift_khz, 6),
        round(stability, 6)
    )

class FeatureStore:
    def __init__(self):
        self.features = {}
        self.bandwidth_history = {}
        self.frequency_history = {}

    def update(self, feature):
        feature.last_seen = time.monotonic()

        freq_key = round(
            feature.frequency,
            2
        )

        if freq_key not in self.bandwidth_history:
            self.bandwidth_history[freq_key] = deque(
                maxlen=20
            )

        if freq_key not in self.frequency_history:
            self.frequency_history[freq_key] = deque(
                maxlen=20
            )

        self.bandwidth_history[
            freq_key
        ].append(
            feature.bandwidth_khz
        )

        self.frequency_history[
            freq_key
        ].append(
            feature.frequency
        )

        history = self.bandwidth_history[
            freq_key
        ]

        feature.bandwidth_khz = max(
            history
        )

        feature.bandwidth_observations = len(
            history
        )

        feature.bandwidth_stability = (
            calculate_bandwidth_stability(
                history
            )
        )

        frequency_history = self.frequency_history[
            freq_key
        ]

        feature.frequency_observations = len(
            frequency_history
        )

        frequency_stability = calculate_frequency_stability(
            frequency_history
        )

        if frequency_stability is not None:
            (
                feature.frequency_drift_khz,
                feature.frequency_stability
            ) = frequency_stability

        self.features[
            freq_key
        ] = feature

    def get(self, frequency):
        freq_key = round(
            frequency,
            2
        )

        return self.features.get(
            freq_key
        )

    def get_seconds_since_seen(
            self,
            frequency
    ):
        feature = self.get(
            frequency
        )

        if feature is None:
            return None

        return max(
            0.0,
            time.monotonic()
            - feature.last_seen
        )

    def prune_stale(
            self,
            max_age_seconds
    ):
        if max_age_seconds < 0:
            raise ValueError(
                "Maximum feature age cannot be negative."
            )

        current_time = time.monotonic()

        stale_keys = [
            frequency
            for frequency, feature in self.features.items()
            if (
                    current_time
                    - feature.last_seen
                    > max_age_seconds
            )
        ]

        for frequency in stale_keys:
            self.features.pop(
                frequency,
                None
            )

            self.bandwidth_history.pop(
                frequency,
                None
            )

            self.frequency_history.pop(
                frequency,
                None
            )

        return len(
            stale_keys
        )

    def get_all(self):
        return self.features


def extract_features(
    frequency,
    peak_power,
    average_power,
    bandwidth_khz,
    occupancy_percent,
    age_seconds,
    strength,
    persistence,
    duty_cycle_percent=0.0
):
    signal_type = classify_signal_type(
        SignalFeatures(
            frequency=frequency,
            peak_power=peak_power,
            average_power=average_power,
            bandwidth_khz=bandwidth_khz,
            occupancy_percent=occupancy_percent,
            age_seconds=age_seconds,
            strength=strength,
            persistence=persistence,
            duty_cycle_percent=duty_cycle_percent
        )
    )

    return SignalFeatures(
        frequency=frequency,
        peak_power=peak_power,
        average_power=average_power,
        bandwidth_khz=bandwidth_khz,
        occupancy_percent=occupancy_percent,
        age_seconds=age_seconds,
        strength=strength,
        persistence=persistence,
        signal_type=signal_type,
        duty_cycle_percent=duty_cycle_percent
    )
