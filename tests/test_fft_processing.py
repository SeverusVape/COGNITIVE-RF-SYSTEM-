import unittest

import numpy as np

from SDR.fft_processing import compute_fft


class FFTProcessingTests(unittest.TestCase):

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
        sample_indices = np.arange(
            sample_count
        )

        samples = np.exp(
            2j
            * np.pi
            * tone_bin
            * sample_indices
            / sample_count
        )

        power_db = compute_fft(samples)

        self.assertEqual(
            int(
                np.argmax(power_db)
            ),
            sample_count // 2 + tone_bin
        )


if __name__ == "__main__":
    unittest.main()
