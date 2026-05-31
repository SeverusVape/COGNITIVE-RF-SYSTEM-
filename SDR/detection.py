import numpy as np

from scipy.signal import find_peaks


def detect_peaks(
    power_db,
    freqs_mhz
):

    peaks, properties = find_peaks(
        power_db,
        height=45,
        distance=300
    )

    peak_powers = properties[
        "peak_heights"
    ]

    sorted_indices = np.argsort(
        peak_powers
    )[::-1]

    top_peaks = peaks[
        sorted_indices[:2]
    ]

    results = []

    for peak in top_peaks:

        freq = freqs_mhz[peak]

        power = power_db[peak]

        results.append(
            (freq, power)
        )

    return results