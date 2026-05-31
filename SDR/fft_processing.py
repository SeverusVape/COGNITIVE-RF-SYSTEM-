import numpy as np


def compute_fft(samples):

    fft_data = np.fft.fftshift(
        np.fft.fft(samples)
    )

    power_db = 20 * np.log10(
        np.abs(fft_data) + 1e-12
    )

    return power_db