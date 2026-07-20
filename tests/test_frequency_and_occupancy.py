import unittest

import numpy as np

from UTILS.frequency_axis import (
    build_frequency_axis,
    build_frequency_edges
)
from UTILS.occupancy import calculate_occupancy


class FrequencyAxisTests(unittest.TestCase):

    def test_frequency_axis_is_centered_and_evenly_spaced(self):
        freqs, freqs_mhz = build_frequency_axis(
            num_samples=8,
            sample_rate=8e6,
            center_freq=100e6
        )

        np.testing.assert_allclose(
            np.diff(freqs),
            np.full(7, 1e6)
        )
        self.assertEqual(freqs_mhz[4], 100.0)

    def test_frequency_edges_extend_half_a_bin(self):
        left, right = build_frequency_edges(
            np.array([
                99.0,
                99.5,
                100.0
            ])
        )

        self.assertEqual(left, 98.75)
        self.assertEqual(right, 100.25)

    def test_frequency_edges_require_two_bins(self):
        with self.assertRaises(ValueError):
            build_frequency_edges(
                np.array([100.0])
            )


class OccupancyTests(unittest.TestCase):

    def test_occupancy_counts_only_bins_above_threshold(self):
        occupancy, meter = calculate_occupancy(
            np.array([
                9.0,
                10.0,
                11.0,
                12.0
            ]),
            threshold=10.0
        )

        self.assertEqual(occupancy, 50.0)
        self.assertEqual(
            meter.count("■"),
            5
        )
        self.assertEqual(
            meter.count("░"),
            5
        )

    def test_occupancy_rejects_empty_fft_data(self):
        with self.assertRaises(ValueError):
            calculate_occupancy(
                np.array([]),
                threshold=10.0
            )


if __name__ == "__main__":
    unittest.main()
