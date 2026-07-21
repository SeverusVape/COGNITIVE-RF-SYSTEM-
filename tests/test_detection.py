import unittest

import numpy as np

from SDR.detection import detect_peaks


class PeakDetectionTests(unittest.TestCase):

    @staticmethod
    def _spectrum(
            bin_width_mhz,
            peak_definitions
    ):
        freqs_mhz = np.arange(
            100.0,
            101.0 + bin_width_mhz / 2,
            bin_width_mhz
        )

        power_db = np.zeros(
            len(freqs_mhz)
        )

        for frequency, power in peak_definitions:
            index = int(
                np.argmin(
                    np.abs(
                        freqs_mhz - frequency
                    )
                )
            )
            power_db[index] = power

        return power_db, freqs_mhz

    def test_requires_at_least_two_frequency_bins(self):
        with self.assertRaises(ValueError):
            detect_peaks(
                np.array([20.0]),
                np.array([100.0])
            )

    def test_returns_only_three_strongest_peaks(self):
        power_db, freqs_mhz = self._spectrum(
            0.001,
            (
                (100.10, 20.0),
                (100.25, 30.0),
                (100.40, 40.0),
                (100.55, 50.0)
            )
        )

        peaks, _ = detect_peaks(
            power_db,
            freqs_mhz
        )

        self.assertEqual(
            [peak[1] for peak in peaks],
            [50.0, 40.0, 30.0]
        )

    def test_minimum_peak_spacing_is_resolution_independent(
            self
    ):
        peak_definitions = (
            (100.40, 40.0),
            (100.45, 30.0),
            (100.60, 35.0)
        )

        detected_frequencies = []

        for bin_width_mhz in (
                0.001,
                0.002
        ):
            power_db, freqs_mhz = self._spectrum(
                bin_width_mhz,
                peak_definitions
            )

            peaks, _ = detect_peaks(
                power_db,
                freqs_mhz
            )

            detected_frequencies.append(
                sorted(
                    round(peak[0], 3)
                    for peak in peaks
                )
            )

        self.assertEqual(
            detected_frequencies,
            [
                [100.4, 100.6],
                [100.4, 100.6]
            ]
        )

    def test_bandwidth_uses_frequency_bin_width(self):
        measured_bandwidths = []

        for bin_width_mhz in (
                0.001,
                0.002
        ):
            power_db, freqs_mhz = self._spectrum(
                bin_width_mhz,
                (
                    (100.50, 30.0),
                )
            )

            peak_index = int(
                np.argmax(power_db)
            )

            power_db[
                peak_index - 2:peak_index + 3
            ] = 20.0
            power_db[peak_index] = 30.0

            peaks, _ = detect_peaks(
                power_db,
                freqs_mhz
            )

            measured_bandwidths.append(
                peaks[0][2]
            )

        self.assertAlmostEqual(
            measured_bandwidths[1],
            measured_bandwidths[0] * 2,
            places=6
        )

    def test_peak_includes_local_prominence(self):
        power_db, freqs_mhz = self._spectrum(
            0.001,
            (
                (100.50, 30.0),
            )
        )

        peaks, _ = detect_peaks(
            power_db,
            freqs_mhz
        )

        self.assertEqual(
            len(peaks[0]),
            4
        )
        self.assertAlmostEqual(
            peaks[0][3],
            30.0
        )

    def test_peak_prominence_ignores_absolute_power_offset(self):
        power_db, freqs_mhz = self._spectrum(
            0.001,
            (
                (100.50, 30.0),
            )
        )

        original_peaks, _ = detect_peaks(
            power_db,
            freqs_mhz
        )
        shifted_peaks, _ = detect_peaks(
            power_db + 40.0,
            freqs_mhz
        )

        self.assertAlmostEqual(
            shifted_peaks[0][3],
            original_peaks[0][3]
        )


if __name__ == "__main__":
    unittest.main()
