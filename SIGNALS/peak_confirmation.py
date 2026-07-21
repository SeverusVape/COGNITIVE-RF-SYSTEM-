from collections import deque

import numpy as np


class PeakConfirmer:

    def __init__(
            self,
            required_hits=2,
            window_frames=3,
            tolerance_khz=25.0
    ):
        if (
                isinstance(required_hits, bool)
                or not isinstance(
                    required_hits,
                    int
                )
                or required_hits < 1
        ):
            raise ValueError(
                "Required hits must be a positive integer."
            )

        if (
                isinstance(window_frames, bool)
                or not isinstance(
                    window_frames,
                    int
                )
                or window_frames < required_hits
        ):
            raise ValueError(
                "Window frames must be an integer "
                "greater than or equal to required hits."
            )

        if (
                not np.isfinite(tolerance_khz)
                or tolerance_khz < 0
        ):
            raise ValueError(
                "Frequency tolerance must be non-negative."
            )

        self.required_hits = required_hits
        self.window_frames = window_frames
        self.tolerance_mhz = (
            tolerance_khz
            / 1000
        )

        self._frames = deque(
            maxlen=window_frames
        )

    @staticmethod
    def _validate_peaks(peaks):
        validated = []

        for peak in peaks:
            if len(peak) not in (3, 4):
                raise ValueError(
                    "Each peak must contain frequency, "
                    "power, bandwidth, and optional prominence."
                )

            if not np.all(
                    np.isfinite(
                        peak
                    )
            ):
                raise ValueError(
                    "Peak values must be finite."
                )

            validated.append(
                tuple(
                    float(value)
                    for value in peak
                )
            )

        return validated

    def update(self, peaks):
        current_peaks = self._validate_peaks(
            peaks
        )

        self._frames.append(
            current_peaks
        )

        confirmed = []

        for current_peak in current_peaks:
            current_frequency = current_peak[0]

            matching_frames = sum(
                any(
                    abs(
                        previous_peak[0]
                        - current_frequency
                    )
                    <= self.tolerance_mhz
                    for previous_peak in frame
                )
                for frame in self._frames
            )

            if matching_frames >= self.required_hits:
                confirmed.append(
                    current_peak
                )

        return confirmed

    def reset(self):
        self._frames.clear()
