import unittest

from VALIDATION.scripts.run_detector_comparison import (
    REQUIRED_SCENARIOS,
    evaluate_gates,
    wilson_interval
)


def _summary_row(
        detector,
        scenario,
        recall=0.9,
        pd=0.9,
        pfa=0.1,
        p95_runtime=10.0
):
    return {
        "detector": detector,
        "scenario": scenario,
        "recall": recall,
        "probability_of_detection": pd,
        "frame_false_alarm_rate": pfa,
        "p95_runtime_ms": p95_runtime
    }


class DetectorComparisonStatisticsTests(unittest.TestCase):

    def test_wilson_interval_contains_observed_proportion(self):
        lower, upper = wilson_interval(
            50,
            100
        )

        self.assertLess(
            lower,
            0.5
        )
        self.assertGreater(
            upper,
            0.5
        )

    def test_wilson_interval_handles_empty_sample(self):
        self.assertEqual(
            wilson_interval(
                0,
                0
            ),
            (
                None,
                None
            )
        )

    def test_predeclared_gates_pass_controlled_candidate(self):
        rows = []

        for scenario in REQUIRED_SCENARIOS:
            rows.extend([
                _summary_row(
                    "adaptive",
                    scenario,
                    pfa=(
                        0.8
                        if scenario == "noise_only"
                        else 0.2
                    )
                ),
                _summary_row(
                    "os_cfar",
                    scenario,
                    pfa=(
                        0.2
                        if scenario == "noise_only"
                        else 0.1
                    ),
                    p95_runtime=20.0
                )
            ])

        gates = evaluate_gates(
            rows
        )

        self.assertEqual(
            len(gates),
            6
        )
        self.assertTrue(
            all(
                gate["passed"] == "true"
                for gate in gates
            )
        )

    def test_noise_gate_rejects_insufficient_reduction(self):
        rows = []

        for scenario in REQUIRED_SCENARIOS:
            rows.extend([
                _summary_row(
                    "adaptive",
                    scenario,
                    pfa=(
                        0.8
                        if scenario == "noise_only"
                        else 0.2
                    )
                ),
                _summary_row(
                    "os_cfar",
                    scenario,
                    pfa=(
                        0.7
                        if scenario == "noise_only"
                        else 0.1
                    )
                )
            ])

        gates = evaluate_gates(
            rows
        )

        noise_gate = next(
            gate
            for gate in gates
            if gate["gate_id"] == "G1"
        )

        self.assertEqual(
            noise_gate["passed"],
            "false"
        )


if __name__ == "__main__":
    unittest.main()
