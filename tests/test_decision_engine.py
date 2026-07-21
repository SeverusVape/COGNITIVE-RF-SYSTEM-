import unittest

from collections import OrderedDict
from unittest.mock import patch

from SURVEY.decision_engine import (
    build_feature_snapshot,
    classify_decision_confidence,
    find_active_signal,
    find_free_channel,
    smart_recommendation
)
from SIGNALS.feature_extractor import (
    FeatureStore,
    SignalFeatures
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


def signal_feature(
        frequency,
        strength="M",
        persistence="A"
):
    return SignalFeatures(
        frequency=frequency,
        peak_power=55.0,
        average_power=25.0,
        bandwidth_khz=20.0,
        occupancy_percent=10.0,
        age_seconds=4.0,
        strength=strength,
        persistence=persistence,
        duty_cycle_percent=80.0
    )


class SmartDecisionTests(unittest.TestCase):

    def test_decision_confidence_uses_normalized_margin(
            self
    ):
        expected_confidence = {
            None: "N/A",
            0.0: "LOW",
            2.9: "LOW",
            3.0: "MODERATE",
            7.9: "MODERATE",
            8.0: "HIGH"
        }

        for margin, expected in expected_confidence.items():
            with self.subTest(
                    margin=margin
            ):
                self.assertEqual(
                    classify_decision_confidence(
                        margin,
                        maximum_score=100
                    ),
                    expected
                )

    def test_decision_confidence_rejects_invalid_values(
            self
    ):
        for invalid_margin in (
                -1,
                float("nan"),
                float("inf"),
                True
        ):
            with self.subTest(
                    invalid_margin=invalid_margin
            ):
                with self.assertRaises(
                        ValueError
                ):
                    classify_decision_confidence(
                        invalid_margin
                    )

        for invalid_maximum in (
                0,
                -1,
                float("nan"),
                True
        ):
            with self.subTest(
                    invalid_maximum=invalid_maximum
            ):
                with self.assertRaises(
                        ValueError
                ):
                    classify_decision_confidence(
                        1,
                        maximum_score=invalid_maximum
                    )

    def test_free_and_active_modes_select_opposites(self):
        survey_results = {
            100.0: 10.0,
            101.0: 30.0,
            102.0: 20.0
        }

        self.assertEqual(
            find_free_channel(
                survey_results
            )["frequency"],
            100.0
        )

        self.assertEqual(
            find_active_signal(
                survey_results
            )["frequency"],
            101.0
        )

    def test_feature_snapshot_uses_fresh_nearby_feature(
            self
    ):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            for _ in range(3):
                store.update(
                    signal_feature(
                        100.012,
                        strength="S",
                        persistence="P"
                    )
                )

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.5
        ):
            snapshot = build_feature_snapshot(
                100.0,
                store,
                max_age_seconds=2.0
            )

        self.assertIsNotNone(
            snapshot
        )
        self.assertEqual(
            snapshot["strength"],
            "S"
        )
        self.assertEqual(
            snapshot["persistence"],
            "P"
        )
        self.assertEqual(
            snapshot["bandwidth_observations"],
            3
        )
        self.assertEqual(
            snapshot["frequency_observations"],
            3
        )

    def test_feature_snapshot_ignores_stale_feature(
            self
    ):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            store.update(
                signal_feature(
                    100.0
                )
            )

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=13.0
        ):
            snapshot = build_feature_snapshot(
                100.0,
                store,
                max_age_seconds=2.0
            )

        self.assertIsNone(
            snapshot
        )

    def test_smart_mode_without_metrics_falls_back_to_free(
            self
    ):
        decision = smart_recommendation(
            {
                100.0: 20.0,
                101.0: 10.0
            },
            {},
            [],
            None
        )

        self.assertEqual(
            decision["mode"],
            "FREE"
        )
        self.assertEqual(
            decision["frequency"],
            101.0
        )

    def test_smart_mode_uses_feature_store_when_snapshot_absent(
            self
    ):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            store.update(
                signal_feature(
                    100.0,
                    strength="S",
                    persistence="P"
                )
            )

        survey_results = {
            100.0: 20.0,
            101.0: 20.0
        }

        survey_metrics = {
            100.0: {
                "occupancy": 20.0,
                "max_power": 50.0,
                "average_power": 30.0
            },
            101.0: {
                "occupancy": 20.0,
                "max_power": 50.0,
                "average_power": 30.0
            }
        }

        decision = smart_recommendation(
            survey_results,
            survey_metrics,
            [],
            store
        )

        self.assertEqual(
            decision["frequency"],
            100.0
        )
        self.assertEqual(
            decision["score_details"][
                "persistence_score"
            ],
            10
        )
        self.assertEqual(
            decision["score_details"][
                "strength_score"
            ],
            6
        )

    def test_explicit_empty_snapshot_blocks_feature_store_fallback(
            self
    ):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            store.update(
                signal_feature(
                    100.0,
                    strength="S",
                    persistence="P"
                )
            )

        decision = smart_recommendation(
            {
                100.0: 20.0
            },
            {
                100.0: build_metric(
                    20.0,
                    50.0,
                    feature_snapshot=None
                )
            },
            [],
            store
        )

        self.assertEqual(
            decision["score_details"][
                "persistence_score"
            ],
            0
        )
        self.assertEqual(
            decision["score_details"][
                "strength_score"
            ],
            0
        )

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

        self.assertEqual(
            decision["decision_confidence"],
            "MODERATE"
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

        self.assertEqual(
            decision["decision_confidence"],
            "N/A"
        )


if __name__ == "__main__":
    unittest.main()
