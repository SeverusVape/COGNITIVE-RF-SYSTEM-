import numpy as np

from scipy.ndimage import percentile_filter
from scipy.signal import find_peaks


def estimate_local_noise_floor(
        power_db,
        freqs_mhz,
        window_khz=250.0,
        percentile=30.0
):
    power_db = np.asarray(
        power_db,
        dtype=float
    )

    freqs_mhz = np.asarray(
        freqs_mhz,
        dtype=float
    )

    if power_db.ndim != 1:
        raise ValueError(
            "Power data must be one-dimensional."
        )

    if freqs_mhz.ndim != 1:
        raise ValueError(
            "Frequency data must be one-dimensional."
        )

    if len(power_db) != len(freqs_mhz):
        raise ValueError(
            "Power and frequency data must have equal lengths."
        )

    if len(freqs_mhz) < 2:
        raise ValueError(
            "At least two frequency bins are required."
        )

    if (
            not np.all(
                np.isfinite(power_db)
            )
            or not np.all(
                np.isfinite(freqs_mhz)
            )
    ):
        raise ValueError(
            "Power and frequency data must be finite."
        )

    if (
            not np.isfinite(window_khz)
            or window_khz <= 0
    ):
        raise ValueError(
            "Noise-floor window must be positive."
        )

    if (
            not np.isfinite(percentile)
            or percentile < 0
            or percentile > 100
    ):
        raise ValueError(
            "Noise-floor percentile must be between 0 and 100."
        )

    frequency_steps = np.diff(
        freqs_mhz
    )

    if (
            np.any(frequency_steps == 0)
            or not (
                np.all(frequency_steps > 0)
                or np.all(frequency_steps < 0)
            )
    ):
        raise ValueError(
            "Frequency data must be strictly monotonic."
        )

    bin_width_khz = float(
        np.median(
            np.abs(
                frequency_steps
            )
        )
        * 1000
    )

    window_bins = max(
        3,
        round(
            window_khz
            / bin_width_khz
        )
    )

    if window_bins % 2 == 0:
        window_bins += 1

    return percentile_filter(
        power_db,
        percentile=percentile,
        size=window_bins,
        mode="reflect"
    )


def build_local_detection_threshold(
        power_db,
        freqs_mhz,
        margin_db=10.0,
        window_khz=250.0,
        percentile=30.0
):
    if (
            not np.isfinite(margin_db)
            or margin_db < 0
    ):
        raise ValueError(
            "Detection margin must be non-negative."
        )

    noise_floor = estimate_local_noise_floor(
        power_db,
        freqs_mhz,
        window_khz=window_khz,
        percentile=percentile
    )

    return noise_floor + margin_db


def detect_peaks(
    power_db,
    freqs_mhz
):
    if len(freqs_mhz) < 2:
        raise ValueError(
            "At least two frequency bins are required."
        )

    bin_width_khz = abs(
        freqs_mhz[1]
        - freqs_mhz[0]
    ) * 1000

    minimum_peak_distance_khz = 75.0

    minimum_peak_distance_bins = max(
        1,
        round(
            minimum_peak_distance_khz
            / bin_width_khz
        )
    )

    threshold = build_local_detection_threshold(
        power_db,
        freqs_mhz
    )

    peaks, properties = find_peaks(
        power_db,
        height=threshold,
        distance=minimum_peak_distance_bins
    )

    peak_powers = properties[
        "peak_heights"
    ]

    sorted_indices = np.argsort(
        peak_powers
    )[::-1]

    top_peaks = peaks[
        sorted_indices[:3]
    ]

    results = []

    for peak in top_peaks:

        freq = freqs_mhz[peak]

        power = power_db[peak]
        bw_threshold = power - 15

        left = peak

        while (
                left > 0
                and power_db[left] > bw_threshold
        ):
            left -= 1

        right = peak

        while (
                right < len(power_db) - 1
                and power_db[right] > bw_threshold
        ):
            right += 1

        bandwidth_bins = right - left

        bandwidth_khz = (
                bandwidth_bins
                * bin_width_khz
        )

        results.append(
            (
                freq,
                power,
                bandwidth_khz
            )
        )

    return results, threshold
