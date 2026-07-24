import unittest

import numpy as np

from VALIDATION.detector_evaluation import (
    DetectorAdapter,
    REQUIRED_SCENARIOS,
    SyntheticTrial,
    build_detector_adapters,
    build_phase3_trials,
    evaluate_detectors,
    evaluate_trial,
    match_detections,
    summarize_results
)


class DetectorEvaluationScenarioTests(unittest.TestCase):

    def test_builder_covers_every_required_scenario(self):
        trials = build_phase3_trials(
            trials_per_scenario=1,
            fft_size=1024
        )

        self.assertEqual(
            {
                trial.scenario
                for trial in trials
            },
            set(
                REQUIRED_SCENARIOS
            )
        )

    def test_trial_generation_is_deterministic(self):
        first = build_phase3_trials(
            trials_per_scenario=1,
            base_seed=1234,
            fft_size=1024
        )

        second = build_phase3_trials(
            trials_per_scenario=1,
            base_seed=1234,
            fft_size=1024
        )

        self.assertEqual(
            len(first),
            len(second)
        )

        for first_trial, second_trial in zip(
                first,
                second
        ):
            self.assertEqual(
                first_trial.scenario,
                second_trial.scenario
            )

            self.assertEqual(
                first_trial.expected_frequencies_mhz,
                second_trial.expected_frequencies_mhz
            )

            np.testing.assert_array_equal(
                first_trial.power_db,
                second_trial.power_db
            )

            self.assertFalse(
                first_trial.power_db.flags.writeable
            )

            self.assertFalse(
                first_trial.freqs_mhz.flags.writeable
            )

    def test_rejects_invalid_trial_count(self):
        for invalid_count in (
                0,
                -1,
                True,
                1.5
        ):
            with self.subTest(
                    invalid_count=invalid_count
            ):
                with self.assertRaises(
                        ValueError
                ):
                    build_phase3_trials(
                        trials_per_scenario=invalid_count
                    )


class DetectionMatchingTests(unittest.TestCase):

    def test_matching_is_one_to_one(self):
        match = match_detections(
            (
                100.000,
                100.001
            ),
            (
                (
                    100.0004,
                    20.0,
                    1.0
                ),
            ),
            tolerance_hz=1_000.0
        )

        self.assertEqual(
            match["true_positive_count"],
            1
        )

        self.assertEqual(
            match["false_positive_count"],
            0
        )

        self.assertEqual(
            match["false_negative_count"],
            1
        )

    def test_unmatched_detection_is_false_positive(self):
        match = match_detections(
            (100.0,),
            (
                (
                    100.0,
                    20.0,
                    1.0
                ),
                (
                    100.1,
                    20.0,
                    1.0
                )
            ),
            tolerance_hz=500.0
        )

        self.assertEqual(
            match["true_positive_count"],
            1
        )

        self.assertEqual(
            match["false_positive_count"],
            1
        )


class DetectorEvaluationMetricTests(unittest.TestCase):

    @staticmethod
    def _trial(
            expected=(100.0,)
    ):
        return SyntheticTrial(
            scenario="single_carrier",
            trial_index=1,
            random_seed=1,
            power_db=np.zeros(21),
            freqs_mhz=np.linspace(
                99.99,
                100.01,
                21
            ),
            expected_frequencies_mhz=expected
        )

    def test_trial_records_detection_and_runtime_metrics(self):
        def detector(
                power_db,
                freqs_mhz
        ):
            return (
                [
                    (
                        100.0,
                        20.0,
                        1.0
                    )
                ],
                np.ones_like(
                    power_db
                )
            )

        result = evaluate_trial(
            self._trial(),
            DetectorAdapter(
                "controlled",
                detector
            ),
            tolerance_hz=500.0
        )

        self.assertEqual(
            result.true_positive_count,
            1
        )

        self.assertEqual(
            result.false_positive_count,
            0
        )

        self.assertGreaterEqual(
            result.runtime_ms,
            0.0
        )

        self.assertEqual(
            result.finite_threshold_median_db,
            1.0
        )

    def test_summary_calculates_required_metrics(self):
        def detector(
                power_db,
                freqs_mhz
        ):
            return (
                [
                    (
                        100.0,
                        20.0,
                        1.0
                    ),
                    (
                        100.005,
                        15.0,
                        1.0
                    )
                ],
                np.ones_like(
                    power_db
                )
            )

        detector_adapter = DetectorAdapter(
            "controlled",
            detector
        )

        results = (
            evaluate_trial(
                self._trial(),
                detector_adapter,
                tolerance_hz=500.0
            ),
            evaluate_trial(
                SyntheticTrial(
                    scenario="noise_only",
                    trial_index=2,
                    random_seed=2,
                    power_db=np.zeros(21),
                    freqs_mhz=np.linspace(
                        99.99,
                        100.01,
                        21
                    ),
                    expected_frequencies_mhz=()
                ),
                detector_adapter,
                tolerance_hz=500.0
            )
        )

        summaries = summarize_results(
            results
        )

        single_summary = next(
            summary
            for summary in summaries
            if summary["scenario"] == "single_carrier"
        )

        noise_summary = next(
            summary
            for summary in summaries
            if summary["scenario"] == "noise_only"
        )

        self.assertEqual(
            single_summary["probability_of_detection"],
            1.0
        )

        self.assertEqual(
            single_summary["precision"],
            0.5
        )

        self.assertEqual(
            single_summary["recall"],
            1.0
        )

        self.assertEqual(
            noise_summary["frame_false_alarm_rate"],
            1.0
        )

        self.assertIn(
            "p95_runtime_ms",
            single_summary
        )

        self.assertIn(
            "frequency_error_standard_deviation_hz",
            single_summary
        )


class RealDetectorHarnessTests(unittest.TestCase):

    def test_both_detectors_execute_identical_scenarios(self):
        trials = build_phase3_trials(
            trials_per_scenario=1
        )

        detectors = build_detector_adapters()

        results = evaluate_detectors(
            trials,
            detectors=detectors
        )

        self.assertEqual(
            len(results),
            len(trials) * len(detectors)
        )

        evaluated_pairs = {
            (
                result.detector,
                result.scenario
            )
            for result in results
        }

        expected_pairs = {
            (
                detector.name,
                scenario
            )
            for detector in detectors
            for scenario in REQUIRED_SCENARIOS
        }

        self.assertEqual(
            evaluated_pairs,
            expected_pairs
        )

        for result in results:
            self.assertGreaterEqual(
                result.runtime_ms,
                0.0
            )

            self.assertTrue(
                np.isfinite(
                    result.finite_threshold_median_db
                )
            )


if __name__ == "__main__":
    unittest.main()
