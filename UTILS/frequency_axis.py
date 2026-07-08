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