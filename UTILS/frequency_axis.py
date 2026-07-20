import numpy as np


def build_frequency_axis(
        num_samples,
        sample_rate,
        center_freq
):

    freqs = np.fft.fftshift(
        np.fft.fftfreq(
            num_samples,
            d=1 / sample_rate
        )
    )

    freqs = freqs + center_freq

    freqs_mhz = freqs / 1e6

    return freqs, freqs_mhz


def build_frequency_edges(
        frequencies
):
    if len(frequencies) < 2:
        raise ValueError(
            "At least two frequencies are required."
        )

    bin_width = (
        frequencies[1]
        - frequencies[0]
    )

    left_edge = (
        frequencies[0]
        - bin_width / 2
    )

    right_edge = (
        frequencies[-1]
        + bin_width / 2
    )

    return left_edge, right_edge
