from dataclasses import dataclass
from SIGNALS.signal_type_classifier import (
    classify_signal_type
)

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

class FeatureStore:
    def __init__(self):
        self.features = {}

    def update(self, feature):
        self.features[feature.frequency] = feature

    def get(self, frequency):
        return self.features.get(frequency)

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
    persistence
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
            persistence=persistence
        )
    )

    print(
        f"{frequency:.3f} MHz -> {signal_type}"
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
        signal_type=signal_type
    )