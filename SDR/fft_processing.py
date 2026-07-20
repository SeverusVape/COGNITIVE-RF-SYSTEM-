import numpy as np


def apply_hann_window(samples):
    samples = np.asarray(
        samples
    )

    if samples.ndim != 1:
        raise ValueError(
            "FFT samples must be one-dimensional."
        )

    if len(samples) < 2:
        raise ValueError(
            "At least two FFT samples are required."
        )

    if not np.all(
            np.isfinite(samples)
    ):
        raise ValueError(
            "FFT samples must be finite."
        )

    window = np.hanning(
        len(samples)
    )

    coherent_gain = float(
        np.mean(window)
    )

    return (
        samples
        * window
        / coherent_gain
    )


def compute_fft(samples):

    fft_data = np.fft.fftshift(
        np.fft.fft(samples)
    )

    power_db = 20 * np.log10(
        np.abs(fft_data) + 1e-12
    )

    return power_db


def compute_windowed_fft(samples):
    return compute_fft(
        apply_hann_window(
            samples
        )
    )
