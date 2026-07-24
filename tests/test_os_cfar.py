import unittest

import numpy as np

from SDR.os_cfar import (
    OSCFARConfig,
    build_os_cfar_threshold,
    detect_peaks
)


class OSCFARConfigTests(unittest.TestCase):

    def test_default_rank_fits_reference_window(self):
        config = OSCFARConfig()

        self.assertLessEqual(
            config.rank,
            2 * config.reference_cells
        )

    def test_rejects_invalid_configuration(self):
        invalid_configurations = (
            {"reference_cells": 0},
            {"guard_cells": -1},
            {"rank": 0},
            {
                "reference_cells": 4,
                "rank": 9
            },
            {"threshold_scale": 0},
            {"threshold_scale": np.inf},
            {"minimum_peak_distance_khz": 0},
            {"maximum_peaks": 0},
            {"bandwidth_drop_db": 0}
        )

        for values in invalid_configurations:
            with self.subTest(values=values):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        **values
                    )


class OSCFARThresholdTests(unittest.TestCase):

    def setUp(self):
        self.freqs_mhz = np.linspace(
            99.9,
            100.1,
            201
        )

        self.config = OSCFARConfig(
            reference_cells=4,
            guard_cells=2,
            rank=6,
            threshold_scale=4.0,
            minimum_peak_distance_khz=2.0
        )

    def test_constant_reference_floor_produces_expected_threshold(
            self
    ):
        power_db = np.full(
            len(self.freqs_mhz),
            20.0
        )

        threshold = build_os_cfar_threshold(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        edge_bins = (
            self.config.reference_cells
            + self.config.guard_cells
        )

        expected_threshold = (
            20.0
            + 10 * np.log10(4.0)
        )

        np.testing.assert_allclose(
            threshold[
                edge_bins:-edge_bins
            ],
            expected_threshold
        )

        self.assertTrue(
            np.all(
                np.isinf(
                    threshold[:edge_bins]
                )
            )
        )

        self.assertTrue(
            np.all(
                np.isinf(
                    threshold[-edge_bins:]
                )
            )
        )

    def test_guard_cells_exclude_adjacent_signal_energy(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )

        center = len(power_db) // 2

        power_db[
            center - 2:center + 3
        ] = 60.0

        threshold = build_os_cfar_threshold(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertAlmostEqual(
            threshold[center],
            10.0 + 10 * np.log10(4.0)
        )

    def test_rank_controls_outlier_influence(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )

        center = len(power_db) // 2

        reference_outlier_index = (
            center
            - self.config.guard_cells
            - 1
        )

        power_db[
            reference_outlier_index
        ] = 50.0

        robust_config = OSCFARConfig(
            reference_cells=4,
            guard_cells=2,
            rank=7,
            threshold_scale=1.0,
            minimum_peak_distance_khz=2.0
        )

        maximum_rank_config = OSCFARConfig(
            reference_cells=4,
            guard_cells=2,
            rank=8,
            threshold_scale=1.0,
            minimum_peak_distance_khz=2.0
        )

        robust_threshold = build_os_cfar_threshold(
            power_db,
            self.freqs_mhz,
            config=robust_config
        )

        maximum_threshold = build_os_cfar_threshold(
            power_db,
            self.freqs_mhz,
            config=maximum_rank_config
        )

        self.assertEqual(
            robust_threshold[center],
            10.0
        )

        self.assertEqual(
            maximum_threshold[center],
            50.0
        )

    def test_rejects_spectrum_shorter_than_full_window(self):
        with self.assertRaises(ValueError):
            build_os_cfar_threshold(
                np.zeros(12),
                np.linspace(
                    100.0,
                    100.011,
                    12
                ),
                config=self.config
            )


class OSCFARDetectionTests(unittest.TestCase):

    def setUp(self):
        self.freqs_mhz = np.linspace(
            99.9,
            100.1,
            201
        )

        self.config = OSCFARConfig(
            reference_cells=8,
            guard_cells=2,
            rank=12,
            threshold_scale=2.0,
            minimum_peak_distance_khz=5.0,
            maximum_peaks=3
        )

    def test_detects_peak_and_preserves_public_result_shape(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )

        peak_index = len(power_db) // 2
        power_db[peak_index] = 30.0

        peaks, threshold = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            len(peaks),
            1
        )

        self.assertEqual(
            len(peaks[0]),
            3
        )

        self.assertAlmostEqual(
            peaks[0][0],
            self.freqs_mhz[peak_index]
        )

        self.assertEqual(
            threshold.shape,
            power_db.shape
        )

    def test_returns_only_configured_number_of_strongest_peaks(
            self
    ):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )

        peak_indices = (
            40,
            70,
            100,
            130
        )

        for power, index in enumerate(
                peak_indices,
                start=30
        ):
            power_db[index] = float(
                power
            )

        peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            [peak[1] for peak in peaks],
            [33.0, 32.0, 31.0]
        )

    def test_full_window_policy_excludes_edge_peak(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )

        power_db[2] = 50.0

        peaks, threshold = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            peaks,
            []
        )

        self.assertTrue(
            np.isinf(
                threshold[2]
            )
        )

    def test_accepts_descending_frequency_axis(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )

        peak_index = len(power_db) // 2
        power_db[peak_index] = 30.0

        peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz[::-1],
            config=self.config
        )

        self.assertEqual(
            len(peaks),
            1
        )

    def test_rejects_non_monotonic_frequency_axis(self):
        invalid_frequencies = self.freqs_mhz.copy()
        invalid_frequencies[20] = (
            invalid_frequencies[19]
        )

        with self.assertRaises(ValueError):
            detect_peaks(
                np.zeros(
                    len(invalid_frequencies)
                ),
                invalid_frequencies,
                config=self.config
            )


if __name__ == "__main__":
    unittest.main()
