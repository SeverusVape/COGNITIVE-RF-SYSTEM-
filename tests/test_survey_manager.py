import unittest

from SURVEY.survey_manager import (
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


if __name__ == "__main__":
    unittest.main()
