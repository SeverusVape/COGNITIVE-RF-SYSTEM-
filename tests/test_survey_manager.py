import unittest

from SURVEY.survey_manager import (
    build_diagnostic_evidence_text,
    build_progress_bar,
    build_results_html,
    generate_frequencies,
    rank_frequencies
)


class SurveyManagerTests(unittest.TestCase):

    def test_frequency_generation_includes_stop(self):
        self.assertEqual(
            generate_frequencies(
                88.0,
                89.0,
                0.3
            ),
            [
                88.0,
                88.3,
                88.6,
                88.9,
                89.0
            ]
        )

    def test_frequency_generation_avoids_float_drift(self):
        frequencies = generate_frequencies(
            88.0,
            92.0,
            0.2
        )

        self.assertEqual(len(frequencies), 21)
        self.assertEqual(frequencies[-1], 92.0)
        self.assertEqual(
            len(frequencies),
            len(set(frequencies))
        )

    def test_frequency_ranking_is_most_active_first(self):
        self.assertEqual(
            rank_frequencies({
                88.0: 5.0,
                89.0: 20.0,
                90.0: 10.0
            }),
            [
                (89.0, 20.0),
                (90.0, 10.0),
                (88.0, 5.0)
            ]
        )

    def test_progress_bar_has_fixed_width(self):
        for percentage, filled in (
                (0, 0),
                (50, 10),
                (100, 20)
        ):
            with self.subTest(
                    percentage=percentage
            ):
                bar = build_progress_bar(
                    percentage
                )

                self.assertEqual(len(bar), 20)
                self.assertEqual(
                    bar.count("▮"),
                    filled
                )

    def test_diagnostic_evidence_text_uses_shared_statuses(
            self
    ):
        self.assertEqual(
            build_diagnostic_evidence_text(0),
            "No recent signal evidence"
        )
        self.assertEqual(
            build_diagnostic_evidence_text(3),
            "Provisional (3 observations)"
        )
        self.assertEqual(
            build_diagnostic_evidence_text(5),
            "Established (5 observations)"
        )
        self.assertEqual(
            build_diagnostic_evidence_text(
                1,
                include_observation_word=False
            ),
            "Provisional (1)"
        )

    def test_diagnostic_evidence_text_rejects_invalid_count(
            self
    ):
        for invalid_count in (
                -1,
                1.5,
                True,
                "3"
        ):
            with self.subTest(
                    invalid_count=invalid_count
            ):
                with self.assertRaises(ValueError):
                    build_diagnostic_evidence_text(
                        invalid_count
                    )

    def test_results_text_labels_decision_confidence(
            self
    ):
        results_html = build_results_html(
            sorted_results=[
                (100.0, 10.0),
                (101.0, 20.0)
            ],
            points_scanned=2,
            average_occupancy=15.0,
            recommendation={
                "title": "SMART RECOMMENDATION",
                "frequency": 100.0,
                "occupancy": 10.0,
                "score": 70.0,
                "reason": [
                    "Highest overall score"
                ],
                "runner_up_frequency": 101.0,
                "runner_up_score": 65.0,
                "score_margin": 5.0,
                "decision_confidence": "MODERATE"
            }
        )

        self.assertIn(
            "Confidence (score separation)",
            results_html
        )

        self.assertIn(
            "MODERATE",
            results_html
        )

        self.assertIn(
            "<table",
            results_html
        )

        self.assertNotIn(
            "==========",
            results_html
        )

    def test_results_html_applies_shared_theme(
            self
    ):
        results_html = build_results_html(
            sorted_results=[
                (100.0, 10.0),
                (101.0, 20.0)
            ],
            points_scanned=2,
            average_occupancy=15.0,
            recommendation={
                "title": "SMART RECOMMENDATION",
                "frequency": 100.0,
                "occupancy": 10.0,
                "score": 70.0,
                "reason": [
                    "Highest overall score"
                ],
                "runner_up_frequency": 101.0,
                "runner_up_score": 65.0,
                "score_margin": 5.0,
                "decision_confidence": "MODERATE"
            }
        )

        self.assertNotIn(
            "{{",
            results_html
        )

        self.assertIn(
            'bgcolor="#1d2329"',
            results_html
        )

        self.assertIn(
            "#fbbf24",
            results_html
        )

    def test_results_html_uses_three_column_card_layout(
            self
    ):
        results_html = build_results_html(
            sorted_results=[
                (100.0, 10.0)
            ],
            points_scanned=1,
            average_occupancy=10.0,
            recommendation={
                "title": "SMART RECOMMENDATION",
                "frequency": 100.0,
                "occupancy": 10.0,
                "score": 70.0,
                "reason": [],
                "score_details": {
                    "occupancy_score": 45.0,
                    "power_score": 15.0,
                    "persistence_score": 5.0,
                    "age_score": 2.0,
                    "strength_score": 3.0,
                    "max_power": 50.0,
                    "average_power": 25.0
                }
            }
        )

        self.assertIn(
            'width="32%" valign="top"',
            results_html
        )
        self.assertIn(
            'width="33%" valign="top"',
            results_html
        )
        self.assertIn(
            'width="35%" valign="top"',
            results_html
        )

    def test_results_html_uses_secondary_detail_row(
            self
    ):
        results_html = build_results_html(
            sorted_results=[
                (100.0, 10.0)
            ],
            points_scanned=1,
            average_occupancy=10.0,
            recommendation={
                "title": "SMART RECOMMENDATION",
                "frequency": 100.0,
                "occupancy": 10.0,
                "score": 70.0,
                "reason": []
            }
        )

        self.assertIn(
            'width="36%" valign="top"',
            results_html
        )
        self.assertIn(
            'width="64%" valign="top"',
            results_html
        )

    def test_results_html_shows_observational_diagnostics(
            self
    ):
        results_html = build_results_html(
            sorted_results=[
                (100.0, 10.0),
                (101.0, 20.0)
            ],
            points_scanned=2,
            average_occupancy=15.0,
            recommendation={
                "title": "SMART RECOMMENDATION",
                "frequency": 100.0,
                "occupancy": 10.0,
                "score": 70.0,
                "reason": [
                    "Highest overall score"
                ]
            },
            diagnostic_snapshot={
                "bandwidth_stability": 0.67,
                "bandwidth_observations": 3,
                "frequency_stability": 0.9,
                "frequency_observations": 3,
                "frequency_drift_khz": 2.5,
                "duty_cycle_percent": 60.0
            }
        )

        self.assertIn(
            "Signal Diagnostics",
            results_html
        )
        self.assertIn("67.0%", results_html)
        self.assertIn("90.0%", results_html)
        self.assertIn("2.5 kHz", results_html)
        self.assertIn("60.0%", results_html)
        self.assertIn(
            "Provisional (3 observations)",
            results_html
        )
        self.assertIn(
            "Observed Signal Behavior",
            results_html
        )
        self.assertIn(
            "Stable",
            results_html
        )
        self.assertIn(
            "Moderately stable",
            results_html
        )
        self.assertIn(
            "Intermittent",
            results_html
        )
        self.assertIn(
            "not modulation or service identity",
            results_html
        )
        self.assertIn(
            "Diagnostic only",
            results_html
        )

    def test_results_html_compares_candidate_diagnostic_coverage(
            self
    ):
        snapshot = {
            "bandwidth_stability": 0.67,
            "bandwidth_observations": 6,
            "frequency_stability": 0.91,
            "frequency_observations": 6,
            "frequency_drift_khz": 2.5,
            "duty_cycle_percent": 60.0
        }

        results_html = build_results_html(
            sorted_results=[
                (101.0, 20.0),
                (100.0, 10.0)
            ],
            points_scanned=2,
            average_occupancy=15.0,
            recommendation={
                "title": "SMART RECOMMENDATION",
                "frequency": 100.0,
                "occupancy": 10.0,
                "score": 70.0,
                "reason": []
            },
            diagnostic_snapshot=snapshot,
            diagnostic_snapshots={
                100.0: snapshot,
                101.0: None
            }
        )

        self.assertIn(
            "Survey Diagnostic Coverage",
            results_html
        )
        coverage_html = results_html[
            results_html.index(
                "Survey Diagnostic Coverage"
            ):
        ]

        self.assertLess(
            coverage_html.index(
                "100.000 MHz (recommended)"
            ),
            coverage_html.index("101.000 MHz")
        )
        self.assertIn(
            "Established (6)",
            results_html
        )
        self.assertIn(
            "No recent signal evidence",
            results_html
        )
        self.assertIn(
            "Collecting data",
            results_html
        )
        self.assertIn(
            "Remaining rows in occupancy order",
            results_html
        )


if __name__ == "__main__":
    unittest.main()
