import numpy as np

from scipy.signal import find_peaks


def detect_peaks(
    power_db,
    freqs_mhz
):
    threshold = np.mean(power_db) + 10

    peaks, properties = find_peaks(
        power_db,
        height=threshold,
        distance=300
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
                bandwidth_bins * 0.25
        )

        results.append(
            (
                freq,
                power,
                bandwidth_khz
            )
        )

    return results, threshold