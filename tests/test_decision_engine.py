import unittest

from collections import OrderedDict

from SURVEY.decision_engine import (
    smart_recommendation
)
from UTILS.config import SMART_MAX_SCORE


def build_metric(
        occupancy,
        max_power,
        feature_snapshot=None
):
    return {
        "occupancy": occupancy,
        "max_power": max_power,
        "average_power": max_power - 20,
        "feature_snapshot": feature_snapshot
    }


def make_smart_decision(
        survey_metrics
):
    survey_results = {
        frequency: metrics["occupancy"]
        for frequency, metrics in survey_metrics.items()
    }

    return smart_recommendation(
        survey_results,
        survey_metrics,
        [],
        None
    )


class SmartDecisionTests(unittest.TestCase):

    def test_occupancy_score_uses_full_range(self):
        expected_scores = {
            0: 50,
            25: 37.5,
            50: 25,
            75: 12.5,
            100: 0
        }

        for occupancy, expected in expected_scores.items():
            with self.subTest(
                    occupancy=occupancy
            ):
                decision = make_smart_decision({
                    100.0: build_metric(
                        occupancy,
                        50
                    )
                })

                self.assertEqual(
                    decision[
                        "score_details"
                    ]["occupancy_score"],
                    expected
                )

    def test_power_score_ignores_absolute_offset(self):
        base_metrics = {
            100.0: build_metric(10, 50),
            101.0: build_metric(10, 55),
            102.0: build_metric(10, 60)
        }

        shifted_metrics = {
            frequency: build_metric(
                metrics["occupancy"],
                metrics["max_power"] + 20
            )
            for frequency, metrics in base_metrics.items()
        }

        base_decision = make_smart_decision(
            base_metrics
        )

        shifted_decision = make_smart_decision(
            shifted_metrics
        )

        self.assertEqual(
            base_decision["frequency"],
            shifted_decision["frequency"]
        )

        self.assertEqual(
            base_decision["score"],
            shifted_decision["score"]
        )

        self.assertEqual(
            base_decision[
                "score_details"
            ]["power_score"],
            16.5
        )

    def test_maximum_score_matches_configuration(self):
        metrics = {
            100.0: build_metric(
                0,
                100,
                {
                    "frequency": 100.0,
                    "persistence": "L",
                    "age_seconds": 30,
                    "strength": "S"
                }
            ),
            101.0: build_metric(100, 0),
            102.0: build_metric(100, 0)
        }

        decision = make_smart_decision(
            metrics
        )

        self.assertEqual(
            decision["score"],
            SMART_MAX_SCORE
        )

    def test_runner_up_and_margin_are_recorded(self):
        metrics = {
            100.0: build_metric(10, 50),
            101.0: build_metric(20, 50),
            102.0: build_metric(30, 50)
        }

        decision = make_smart_decision(
            metrics
        )

        self.assertEqual(
            decision["frequency"],
            100.0
        )

        self.assertEqual(
            decision["runner_up_frequency"],
            101.0
        )

        self.assertEqual(
            decision["runner_up_score"],
            55.0
        )

        self.assertEqual(
            decision["score_margin"],
            5.0
        )

    def test_tie_breaking_ignores_insertion_order(self):
        first_order = OrderedDict([
            (
                101.0,
                build_metric(10, 50)
            ),
            (
                100.0,
                build_metric(10, 50)
            )
        ])

        reverse_order = OrderedDict(
            reversed(
                list(
                    first_order.items()
                )
            )
        )

        self.assertEqual(
            make_smart_decision(
                first_order
            )["frequency"],
            100.0
        )

        self.assertEqual(
            make_smart_decision(
                reverse_order
            )["frequency"],
            100.0
        )

    def test_single_point_has_no_runner_up(self):
        decision = make_smart_decision({
            100.0: build_metric(10, 50)
        })

        self.assertIsNone(
            decision["runner_up_frequency"]
        )

        self.assertIsNone(
            decision["runner_up_score"]
        )

        self.assertIsNone(
            decision["score_margin"]
        )


if __name__ == "__main__":
    unittest.main()
