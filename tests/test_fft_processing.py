import unittest

import numpy as np

from SDR.fft_processing import compute_fft
from SDR.fft_processing import (
    apply_hann_window,
    compute_windowed_fft
)


class FFTProcessingTests(unittest.TestCase):

    @staticmethod
    def _complex_tone(
            sample_count,
            tone_bin
    ):
        sample_indices = np.arange(
            sample_count
        )

        return np.exp(
            2j
            * np.pi
            * tone_bin
            * sample_indices
            / sample_count
        )

    def test_zero_input_produces_finite_output(self):
        power_db = compute_fft(
            np.zeros(
                16,
                dtype=complex
            )
        )

        self.assertEqual(
            len(power_db),
            16
        )
        self.assertTrue(
            np.all(
                np.isfinite(power_db)
            )
        )

    def test_complex_tone_appears_in_expected_shifted_bin(
            self
    ):
        sample_count = 32
        tone_bin = 5
        samples = self._complex_tone(
            sample_count,
            tone_bin
        )

        power_db = compute_fft(samples)

        self.assertEqual(
            int(
                np.argmax(power_db)
            ),
            sample_count // 2 + tone_bin
        )

    def test_window_preserves_bin_centered_tone_amplitude(
            self
    ):
        samples = self._complex_tone(
            1024,
            100
        )

        unwindowed_peak = float(
            np.max(
                compute_fft(samples)
            )
        )
        windowed_peak = float(
            np.max(
                compute_windowed_fft(
                    samples
                )
            )
        )

        self.assertAlmostEqual(
            windowed_peak,
            unwindowed_peak,
            places=6
        )

    def test_window_reduces_off_bin_spectral_leakage(
            self
    ):
        sample_count = 1024
        samples = self._complex_tone(
            sample_count,
            100.3
        )

        unwindowed = compute_fft(samples)
        windowed = compute_windowed_fft(
            samples
        )

        peak_index = int(
            np.argmax(windowed)
        )

        outside_main_lobe = np.ones(
            sample_count,
            dtype=bool
        )
        outside_main_lobe[
            peak_index - 3:peak_index + 4
        ] = False

        unwindowed_leakage = float(
            np.max(
                unwindowed[
                    outside_main_lobe
                ]
            )
        )
        windowed_leakage = float(
            np.max(
                windowed[
                    outside_main_lobe
                ]
            )
        )

        self.assertLess(
            windowed_leakage,
            unwindowed_leakage - 15.0
        )

    def test_window_rejects_invalid_samples(self):
        invalid_inputs = (
            np.array([]),
            np.array([1.0]),
            np.zeros((2, 2)),
            np.array([
                1.0,
                np.nan
            ])
        )

        for invalid_samples in invalid_inputs:
            with self.subTest(
                    shape=invalid_samples.shape
            ):
                with self.assertRaises(
                        ValueError
                ):
                    apply_hann_window(
                        invalid_samples
                    )


if __name__ == "__main__":
    unittest.main()
