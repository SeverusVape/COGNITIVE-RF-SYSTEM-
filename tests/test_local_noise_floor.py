import unittest

import numpy as np

from SDR.detection import (
    build_local_detection_threshold,
    detect_peaks,
    estimate_local_noise_floor
)


class LocalNoiseFloorTests(unittest.TestCase):

    def test_local_threshold_adds_detection_margin(self):
        freqs_mhz = np.linspace(
            99.0,
            101.0,
            2001
        )
        power_db = np.full(
            len(freqs_mhz),
            20.0
        )

        threshold = build_local_detection_threshold(
            power_db,
            freqs_mhz,
            margin_db=8.0
        )

        np.testing.assert_allclose(
            threshold,
            28.0
        )

    def test_local_threshold_handles_uneven_baseline(
            self
    ):
        freqs_mhz = np.linspace(
            99.0,
            101.0,
            2001
        )
        baseline = (
            20.0
            + 20.0
            * (
                freqs_mhz - 100.0
            ) ** 2
        )
        power_db = baseline.copy()

        signal_index = int(
            np.argmin(
                np.abs(
                    freqs_mhz - 100.0
                )
            )
        )
        power_db[signal_index] += 15.0

        global_threshold = (
            np.mean(power_db)
            + 10.0
        )
        local_threshold = (
            build_local_detection_threshold(
                power_db,
                freqs_mhz,
                margin_db=10.0
            )
        )

        self.assertLess(
            power_db[signal_index],
            global_threshold
        )
        self.assertGreater(
            power_db[signal_index],
            local_threshold[signal_index]
        )

        peaks, detection_threshold = detect_peaks(
            power_db,
            freqs_mhz
        )

        self.assertEqual(
            detection_threshold.shape,
            power_db.shape
        )
        self.assertTrue(
            any(
                abs(
                    peak[0] - 100.0
                ) < 0.001
                for peak in peaks
            )
        )

    def test_local_threshold_rejects_invalid_margin(self):
        freqs_mhz = np.array([
            100.0,
            100.1,
            100.2
        ])
        power_db = np.array([
            20.0,
            21.0,
            22.0
        ])

        for invalid_margin in (
                -1,
                np.nan,
                np.inf
        ):
            with self.subTest(
                    invalid_margin=invalid_margin
            ):
                with self.assertRaises(
                        ValueError
                ):
                    build_local_detection_threshold(
                        power_db,
                        freqs_mhz,
                        margin_db=invalid_margin
                    )

    def test_constant_floor_is_preserved(self):
        freqs_mhz = np.linspace(
            99.0,
            101.0,
            2001
        )
        power_db = np.full(
            len(freqs_mhz),
            20.0
        )

        noise_floor = estimate_local_noise_floor(
            power_db,
            freqs_mhz
        )

        np.testing.assert_allclose(
            noise_floor,
            20.0
        )

    def test_slowly_curved_floor_is_tracked(self):
        freqs_mhz = np.linspace(
            99.0,
            101.0,
            2001
        )
        baseline = (
            20.0
            + 4.0
            * (
                freqs_mhz - 100.0
            ) ** 2
        )

        noise_floor = estimate_local_noise_floor(
            baseline,
            freqs_mhz
        )

        interior = slice(
            150,
            -150
        )

        self.assertLess(
            float(
                np.max(
                    np.abs(
                        noise_floor[interior]
                        - baseline[interior]
                    )
                )
            ),
            0.5
        )

    def test_narrow_peaks_do_not_raise_local_floor(self):
        freqs_mhz = np.linspace(
            99.0,
            101.0,
            2001
        )
        power_db = np.full(
            len(freqs_mhz),
            20.0
        )
        power_db[950:1051] = 60.0

        noise_floor = estimate_local_noise_floor(
            power_db,
            freqs_mhz
        )

        np.testing.assert_allclose(
            noise_floor[950:1051],
            20.0
        )

    def test_physical_window_is_resolution_independent(self):
        estimates = []

        for bin_count in (
                1001,
                2001
        ):
            freqs_mhz = np.linspace(
                99.0,
                101.0,
                bin_count
            )
            power_db = (
                20.0
                + 2.0
                * (
                    freqs_mhz - 100.0
                )
            )
            power_db[
                np.abs(
                    freqs_mhz - 100.25
                ) < 0.025
            ] += 30.0

            noise_floor = (
                estimate_local_noise_floor(
                    power_db,
                    freqs_mhz
                )
            )

            sample_indices = [
                int(
                    np.argmin(
                        np.abs(
                            freqs_mhz
                            - frequency
                        )
                    )
                )
                for frequency in (
                    99.5,
                    100.0,
                    100.5
                )
            ]

            estimates.append(
                noise_floor[
                    sample_indices
                ]
            )

        np.testing.assert_allclose(
            estimates[0],
            estimates[1],
            atol=0.01
        )

    def test_invalid_inputs_are_rejected(self):
        valid_power = np.array([
            20.0,
            21.0,
            22.0
        ])
        valid_frequencies = np.array([
            100.0,
            100.1,
            100.2
        ])

        invalid_calls = (
            (
                valid_power[:2],
                valid_frequencies,
                {}
            ),
            (
                np.array([
                    20.0,
                    np.nan,
                    22.0
                ]),
                valid_frequencies,
                {}
            ),
            (
                valid_power,
                np.array([
                    100.0,
                    100.0,
                    100.2
                ]),
                {}
            ),
            (
                valid_power,
                valid_frequencies,
                {
                    "window_khz": 0
                }
            ),
            (
                valid_power,
                valid_frequencies,
                {
                    "percentile": 101
                }
            )
        )

        for power_db, freqs_mhz, kwargs in invalid_calls:
            with self.subTest(
                    kwargs=kwargs
            ):
                with self.assertRaises(
                        ValueError
                ):
                    estimate_local_noise_floor(
                        power_db,
                        freqs_mhz,
                        **kwargs
                    )


if __name__ == "__main__":
    unittest.main()
