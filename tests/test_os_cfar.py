import importlib
import unittest
from time import perf_counter

import numpy as np

import SDR.detection as adaptive_detection
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

    def test_reference_cells_validation(self):
        self.assertEqual(
            OSCFARConfig().reference_cells,
            32
        )

        for value in (
                0,
                -1,
                True,
                4.5,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        reference_cells=value
                    )

    def test_guard_cells_validation(self):
        self.assertEqual(
            OSCFARConfig(
                guard_cells=0
            ).guard_cells,
            0
        )
        self.assertEqual(
            OSCFARConfig(
                guard_cells=3
            ).guard_cells,
            3
        )

        for value in (
                -1,
                True,
                2.5,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        guard_cells=value
                    )

    def test_rank_validation(self):
        self.assertEqual(
            OSCFARConfig(
                reference_cells=4,
                rank=1
            ).rank,
            1
        )
        self.assertEqual(
            OSCFARConfig(
                reference_cells=4,
                rank=8
            ).rank,
            8
        )

        for value in (
                0,
                -1,
                9,
                True,
                2.5,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        reference_cells=4,
                        rank=value
                    )

    def test_maximum_peaks_validation(self):
        self.assertEqual(
            OSCFARConfig(
                maximum_peaks=1
            ).maximum_peaks,
            1
        )
        self.assertEqual(
            OSCFARConfig(
                maximum_peaks=5
            ).maximum_peaks,
            5
        )

        for value in (
                0,
                -1,
                True,
                2.5,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        maximum_peaks=value
                    )

    def test_threshold_scale_validation(self):
        self.assertEqual(
            OSCFARConfig(
                threshold_scale=2.5
            ).threshold_scale,
            2.5
        )

        for value in (
                0,
                -1,
                np.nan,
                np.inf,
                -np.inf,
                True,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        threshold_scale=value
                    )

    def test_minimum_peak_distance_validation(self):
        self.assertEqual(
            OSCFARConfig(
                minimum_peak_distance_khz=1.5
            ).minimum_peak_distance_khz,
            1.5
        )

        for value in (
                0,
                -1,
                np.nan,
                np.inf,
                -np.inf,
                True,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        minimum_peak_distance_khz=value
                    )

    def test_bandwidth_drop_validation(self):
        self.assertEqual(
            OSCFARConfig(
                bandwidth_drop_db=12.5
            ).bandwidth_drop_db,
            12.5
        )

        for value in (
                0,
                -1,
                np.nan,
                np.inf,
                -np.inf,
                True,
        ):
            with self.subTest(
                    value=value
            ):
                with self.assertRaises(
                        ValueError
                ):
                    OSCFARConfig(
                        bandwidth_drop_db=value
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

    def test_hand_calculated_threshold_uses_only_reference_cells(
            self
    ):
        config = OSCFARConfig(
            reference_cells=2,
            guard_cells=1,
            rank=3,
            threshold_scale=4.0,
            minimum_peak_distance_khz=1.0
        )
        power_db = np.array([
            1.0,
            2.0,
            11.0,
            21.0,
            900.0,
            800.0,
            700.0,
            31.0,
            41.0,
            9.0,
            8.0,
        ])
        freqs_mhz = np.linspace(
            100.000,
            100.010,
            len(power_db)
        )
        center = 5

        threshold = build_os_cfar_threshold(
            power_db,
            freqs_mhz,
            config=config
        )

        # References are [11, 21, 31, 41]. The one-based rank 3 is 31.
        expected = 31.0 + 10.0 * np.log10(4.0)

        self.assertAlmostEqual(
            threshold[center],
            expected
        )

    def test_cut_and_guard_cells_do_not_change_threshold(self):
        config = OSCFARConfig(
            reference_cells=2,
            guard_cells=1,
            rank=3,
            threshold_scale=1.0,
            minimum_peak_distance_khz=1.0
        )
        baseline = np.array([
            1.0,
            2.0,
            11.0,
            21.0,
            10.0,
            10.0,
            10.0,
            31.0,
            41.0,
            9.0,
            8.0,
        ])
        changed = baseline.copy()
        changed[4:7] = (
            500.0,
            600.0,
            700.0,
        )
        freqs_mhz = np.linspace(
            100.000,
            100.010,
            len(baseline)
        )

        baseline_threshold = build_os_cfar_threshold(
            baseline,
            freqs_mhz,
            config=config
        )
        changed_threshold = build_os_cfar_threshold(
            changed,
            freqs_mhz,
            config=config
        )

        self.assertEqual(
            baseline_threshold[5],
            changed_threshold[5]
        )
        self.assertEqual(
            changed_threshold[5],
            31.0
        )

    def test_threshold_shape_edges_and_input_immutability(self):
        power_db = np.linspace(
            10.0,
            20.0,
            len(self.freqs_mhz)
        )
        original_power = power_db.copy()
        original_frequencies = self.freqs_mhz.copy()

        threshold = build_os_cfar_threshold(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        edge_bins = (
            self.config.reference_cells
            + self.config.guard_cells
        )

        self.assertEqual(
            threshold.shape,
            power_db.shape
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
        np.testing.assert_array_equal(
            power_db,
            original_power
        )
        np.testing.assert_array_equal(
            self.freqs_mhz,
            original_frequencies
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

    def test_noise_only_controlled_spectrum_returns_no_peaks(self):
        peaks, threshold = detect_peaks(
            np.full(
                len(self.freqs_mhz),
                10.0
            ),
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            peaks,
            []
        )
        self.assertEqual(
            threshold.shape,
            self.freqs_mhz.shape
        )

    def test_multiple_separated_peaks_have_exact_frequency_and_power(
            self
    ):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[60] = 25.0
        power_db[140] = 35.0

        peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            len(peaks),
            2
        )
        self.assertEqual(
            peaks[0][0],
            self.freqs_mhz[140]
        )
        self.assertEqual(
            peaks[0][1],
            power_db[140]
        )
        self.assertEqual(
            peaks[1][0],
            self.freqs_mhz[60]
        )
        self.assertEqual(
            peaks[1][1],
            power_db[60]
        )

    def test_peak_below_threshold_is_rejected(self):
        config = OSCFARConfig(
            reference_cells=8,
            guard_cells=2,
            rank=12,
            threshold_scale=2.0,
            minimum_peak_distance_khz=1.0
        )
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[100] = 12.0

        peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=config
        )

        self.assertEqual(
            peaks,
            []
        )

    def test_peak_above_threshold_is_accepted(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[100] = 30.0

        peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            len(peaks),
            1
        )
        self.assertEqual(
            peaks[0][0],
            self.freqs_mhz[100]
        )
        self.assertEqual(
            peaks[0][1],
            30.0
        )

    def test_minimum_peak_distance_is_converted_to_bins(self):
        config = OSCFARConfig(
            reference_cells=8,
            guard_cells=2,
            rank=12,
            threshold_scale=2.0,
            minimum_peak_distance_khz=5.0
        )
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[100] = 30.0
        power_db[103] = 25.0

        peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=config
        )

        self.assertEqual(
            len(peaks),
            1
        )
        self.assertEqual(
            peaks[0][0],
            self.freqs_mhz[100]
        )

    def test_decreasing_axis_returns_frequency_at_selected_bin(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        peak_index = 100
        power_db[peak_index] = 30.0
        descending_frequencies = self.freqs_mhz[
            ::-1
        ]

        peaks, _ = detect_peaks(
            power_db,
            descending_frequencies,
            config=self.config
        )

        self.assertEqual(
            peaks[0][0],
            descending_frequencies[peak_index]
        )
        self.assertGreaterEqual(
            peaks[0][2],
            0.0
        )
        self.assertTrue(
            np.isfinite(
                peaks[0][2]
            )
        )

    def test_repeated_calls_are_deterministic_and_inputs_immutable(
            self
    ):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[60] = 30.0
        power_db[140] = 25.0
        original_power = power_db.copy()
        original_frequencies = self.freqs_mhz.copy()

        first_peaks, first_threshold = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )
        second_peaks, second_threshold = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )

        self.assertEqual(
            first_peaks,
            second_peaks
        )
        np.testing.assert_array_equal(
            first_threshold,
            second_threshold
        )
        np.testing.assert_array_equal(
            power_db,
            original_power
        )
        np.testing.assert_array_equal(
            self.freqs_mhz,
            original_frequencies
        )


class OSCFARInputValidationTests(unittest.TestCase):

    def setUp(self):
        self.config = OSCFARConfig(
            reference_cells=2,
            guard_cells=1,
            rank=3,
            threshold_scale=2.0,
            minimum_peak_distance_khz=1.0
        )
        self.power_db = np.full(
            21,
            10.0
        )
        self.freqs_mhz = np.linspace(
            100.000,
            100.020,
            21
        )

    def test_rejects_non_one_dimensional_arrays(self):
        invalid_cases = (
            (
                np.zeros((3, 7)),
                self.freqs_mhz,
                "Power data"
            ),
            (
                self.power_db,
                np.zeros((3, 7)),
                "Frequency data"
            ),
        )

        for power_db, freqs_mhz, message in invalid_cases:
            with self.subTest(
                    message=message
            ):
                with self.assertRaisesRegex(
                        ValueError,
                        message
                ):
                    detect_peaks(
                        power_db,
                        freqs_mhz,
                        config=self.config
                    )

    def test_rejects_mismatched_empty_and_one_bin_inputs(self):
        cases = (
            (
                np.zeros(20),
                self.freqs_mhz,
                "equal lengths"
            ),
            (
                np.array([]),
                np.array([]),
                "At least two"
            ),
            (
                np.array([10.0]),
                np.array([100.0]),
                "At least two"
            ),
        )

        for power_db, freqs_mhz, message in cases:
            with self.subTest(
                    message=message
            ):
                with self.assertRaisesRegex(
                        ValueError,
                        message
                ):
                    detect_peaks(
                        power_db,
                        freqs_mhz,
                        config=self.config
                    )

    def test_rejects_nonfinite_power_values(self):
        for value in (
                np.nan,
                np.inf,
                -np.inf,
        ):
            power_db = self.power_db.copy()
            power_db[10] = value

            with self.subTest(
                    value=value
            ):
                with self.assertRaisesRegex(
                        ValueError,
                        "finite"
                ):
                    detect_peaks(
                        power_db,
                        self.freqs_mhz,
                        config=self.config
                    )

    def test_rejects_nonfinite_frequency_values(self):
        for value in (
                np.nan,
                np.inf,
                -np.inf,
        ):
            freqs_mhz = self.freqs_mhz.copy()
            freqs_mhz[10] = value

            with self.subTest(
                    value=value
            ):
                with self.assertRaisesRegex(
                        ValueError,
                        "finite"
                ):
                    detect_peaks(
                        self.power_db,
                        freqs_mhz,
                        config=self.config
                    )

    def test_rejects_duplicate_and_non_monotonic_frequencies(self):
        duplicate = self.freqs_mhz.copy()
        duplicate[10] = duplicate[9]
        non_monotonic = self.freqs_mhz.copy()
        non_monotonic[10] = non_monotonic[8]

        for freqs_mhz in (
                duplicate,
                non_monotonic,
        ):
            with self.subTest(
                    freqs_mhz=freqs_mhz
            ):
                with self.assertRaisesRegex(
                        ValueError,
                        "strictly monotonic"
                ):
                    detect_peaks(
                        self.power_db,
                        freqs_mhz,
                        config=self.config
                    )

    def test_accepts_strictly_increasing_and_decreasing_axes(self):
        for freqs_mhz in (
                self.freqs_mhz,
                self.freqs_mhz[::-1],
        ):
            peaks, threshold = detect_peaks(
                self.power_db,
                freqs_mhz,
                config=self.config
            )

            self.assertEqual(
                peaks,
                []
            )
            self.assertEqual(
                threshold.shape,
                self.power_db.shape
            )

    def test_rejects_spectrum_shorter_than_configured_window(self):
        with self.assertRaisesRegex(
                ValueError,
                "too short"
        ):
            detect_peaks(
                np.zeros(6),
                np.linspace(
                    100.0,
                    100.005,
                    6
                ),
                config=self.config
            )

    def test_rejects_incorrect_config_type(self):
        with self.assertRaisesRegex(
                TypeError,
                "OSCFARConfig"
        ):
            detect_peaks(
                self.power_db,
                self.freqs_mhz,
                config={}
            )


class OSCFARContractAndIsolationTests(unittest.TestCase):

    def setUp(self):
        self.freqs_mhz = np.linspace(
            99.9,
            100.1,
            201
        )
        self.power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        self.power_db[100] = 30.0
        self.config = OSCFARConfig(
            reference_cells=8,
            guard_cells=2,
            rank=12,
            threshold_scale=2.0,
            minimum_peak_distance_khz=5.0
        )

    def test_result_contract_matches_adaptive_detector_structure(self):
        os_peaks, os_threshold = detect_peaks(
            self.power_db,
            self.freqs_mhz,
            config=self.config
        )
        adaptive_peaks, adaptive_threshold = (
            adaptive_detection.detect_peaks(
                self.power_db,
                self.freqs_mhz
            )
        )

        self.assertIsInstance(
            os_peaks,
            type(adaptive_peaks)
        )
        self.assertEqual(
            os_threshold.shape,
            adaptive_threshold.shape
        )

        for result in os_peaks:
            self.assertEqual(
                len(result),
                3
            )

    def test_import_and_invocation_do_not_modify_adaptive_module(
            self
    ):
        public_state_before = {
            name: value
            for name, value in vars(
                adaptive_detection
            ).items()
            if not name.startswith("__")
        }

        importlib.import_module(
            "SDR.os_cfar"
        )
        detect_peaks(
            self.power_db,
            self.freqs_mhz,
            config=self.config
        )

        public_state_after = {
            name: value
            for name, value in vars(
                adaptive_detection
            ).items()
            if not name.startswith("__")
        }

        self.assertEqual(
            public_state_before.keys(),
            public_state_after.keys()
        )

        for name, value in public_state_before.items():
            self.assertIs(
                public_state_after[name],
                value
            )

    def test_realistic_fft_size_runtime_smoke(self):
        fft_size = 8192
        freqs_mhz = np.linspace(
            99.0,
            101.0,
            fft_size
        )
        sample_index = np.arange(
            fft_size,
            dtype=float
        )
        power_db = (
            20.0
            + 0.5
            * np.sin(
                2.0
                * np.pi
                * sample_index
                / 257.0
            )
        )
        power_db[fft_size // 2] = 45.0

        start_time = perf_counter()
        peaks, threshold = detect_peaks(
            power_db,
            freqs_mhz
        )
        runtime_ms = (
            perf_counter()
            - start_time
        ) * 1000.0

        self.assertGreaterEqual(
            len(peaks),
            1
        )
        self.assertEqual(
            threshold.shape,
            power_db.shape
        )
        self.assertTrue(
            np.isfinite(
                runtime_ms
            )
        )
        self.assertGreaterEqual(
            runtime_ms,
            0.0
        )


class OSCFARBandwidthRegressionTests(unittest.TestCase):

    def setUp(self):
        self.freqs_mhz = np.linspace(
            100.000,
            100.020,
            21
        )
        self.bin_width_khz = 1.0
        self.config = OSCFARConfig(
            reference_cells=1,
            guard_cells=0,
            rank=1,
            threshold_scale=1.0,
            minimum_peak_distance_khz=1.0,
            maximum_peaks=3,
            bandwidth_drop_db=15.0
        )

    def _detect_region(
            self,
            peak_index,
            region_start,
            region_stop,
            freqs_mhz=None
    ):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[
            region_start:region_stop
        ] = 20.0
        power_db[peak_index] = 30.0

        peaks, _ = detect_peaks(
            power_db,
            (
                self.freqs_mhz
                if freqs_mhz is None
                else freqs_mhz
            ),
            config=self.config
        )

        selected = next(
            peak
            for peak in peaks
            if peak[1] == 30.0
        )

        return selected

    def test_bandwidth_is_one_bin_for_isolated_peak(self):
        peak = self._detect_region(
            peak_index=10,
            region_start=10,
            region_stop=11
        )

        self.assertAlmostEqual(
            peak[2],
            self.bin_width_khz
        )

    def test_bandwidth_matches_exact_multi_bin_region(self):
        peak = self._detect_region(
            peak_index=10,
            region_start=9,
            region_stop=12
        )

        self.assertAlmostEqual(
            peak[2],
            3 * self.bin_width_khz
        )

    def test_bandwidth_drop_controls_included_bins(self):
        power_db = np.full(
            len(self.freqs_mhz),
            10.0
        )
        power_db[9:12] = (
            20.0,
            30.0,
            20.0,
        )
        narrow_config = OSCFARConfig(
            reference_cells=1,
            guard_cells=0,
            rank=1,
            threshold_scale=1.0,
            minimum_peak_distance_khz=1.0,
            bandwidth_drop_db=5.0
        )

        wide_peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=self.config
        )
        narrow_peaks, _ = detect_peaks(
            power_db,
            self.freqs_mhz,
            config=narrow_config
        )

        self.assertAlmostEqual(
            wide_peaks[0][2],
            3 * self.bin_width_khz
        )
        self.assertAlmostEqual(
            narrow_peaks[0][2],
            self.bin_width_khz
        )

    def test_bandwidth_counts_region_reaching_left_array_boundary(
            self
    ):
        peak = self._detect_region(
            peak_index=3,
            region_start=0,
            region_stop=4
        )

        self.assertAlmostEqual(
            peak[2],
            4 * self.bin_width_khz
        )

    def test_bandwidth_counts_region_reaching_right_array_boundary(
            self
    ):
        peak = self._detect_region(
            peak_index=17,
            region_start=17,
            region_stop=21
        )

        self.assertAlmostEqual(
            peak[2],
            4 * self.bin_width_khz
        )

    def test_bandwidth_is_consistent_for_decreasing_axis(self):
        increasing_peak = self._detect_region(
            peak_index=10,
            region_start=9,
            region_stop=12
        )
        decreasing_peak = self._detect_region(
            peak_index=10,
            region_start=9,
            region_stop=12,
            freqs_mhz=self.freqs_mhz[::-1]
        )

        self.assertAlmostEqual(
            increasing_peak[2],
            decreasing_peak[2]
        )
        self.assertTrue(
            np.isfinite(
                decreasing_peak[2]
            )
        )
        self.assertGreaterEqual(
            decreasing_peak[2],
            0.0
        )


if __name__ == "__main__":
    unittest.main()
