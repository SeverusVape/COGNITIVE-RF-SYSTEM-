import unittest

from unittest.mock import patch

from SIGNALS.feature_extractor import (
    calculate_bandwidth_stability,
    calculate_frequency_stability,
    FeatureStore,
    SignalFeatures
)


def feature(
        frequency,
        bandwidth_khz
):
    return SignalFeatures(
        frequency=frequency,
        peak_power=50.0,
        average_power=25.0,
        bandwidth_khz=bandwidth_khz,
        occupancy_percent=10.0,
        age_seconds=0.0,
        strength="M",
        persistence="N"
    )


class FeatureStoreTests(unittest.TestCase):

    def test_frequency_keys_are_normalized(self):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            store.update(
                feature(
                    100.004,
                    25.0
                )
            )

        self.assertIsNotNone(
            store.get(100.0)
        )

    def test_bandwidth_keeps_recent_maximum(self):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            store.update(
                feature(100.0, 25.0)
            )
            store.update(
                feature(100.0, 10.0)
            )

        self.assertEqual(
            store.get(100.0).bandwidth_khz,
            25.0
        )

    def test_stability_requires_minimum_observations(self):
        self.assertIsNone(
            calculate_bandwidth_stability(
                [25.0, 26.0, 24.0, 25.0]
            )
        )

    def test_consistent_bandwidth_has_high_stability(self):
        stability = calculate_bandwidth_stability(
            [100.0, 102.0, 98.0, 101.0, 99.0]
        )

        self.assertGreaterEqual(
            stability,
            0.98
        )

    def test_variable_bandwidth_has_lower_stability(self):
        stable = calculate_bandwidth_stability(
            [100.0, 102.0, 98.0, 101.0, 99.0]
        )
        variable = calculate_bandwidth_stability(
            [20.0, 50.0, 100.0, 150.0, 200.0]
        )

        self.assertLess(
            variable,
            stable
        )

    def test_store_records_bandwidth_stability(self):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            for bandwidth in (
                    100.0,
                    102.0,
                    98.0,
                    101.0,
                    99.0
            ):
                store.update(
                    feature(100.0, bandwidth)
                )

        stored = store.get(100.0)

        self.assertEqual(
            stored.bandwidth_observations,
            5
        )
        self.assertGreaterEqual(
            stored.bandwidth_stability,
            0.98
        )

    def test_stability_rejects_invalid_bandwidth(self):
        for value in (
                -1.0,
                float("nan"),
                float("inf"),
                "25",
                True
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calculate_bandwidth_stability(
                        [25.0, 25.0, 25.0, 25.0, value]
                    )

    def test_frequency_stability_requires_observations(self):
        self.assertIsNone(
            calculate_frequency_stability(
                [100.0, 100.001, 99.999, 100.0]
            )
        )

    def test_consistent_frequency_has_high_stability(self):
        drift_khz, stability = calculate_frequency_stability(
            [100.000, 100.002, 99.998, 100.001, 99.999]
        )

        self.assertAlmostEqual(
            drift_khz,
            1.0
        )
        self.assertGreaterEqual(
            stability,
            0.96
        )

    def test_frequency_drift_reduces_stability(self):
        _, stable = calculate_frequency_stability(
            [100.000, 100.002, 99.998, 100.001, 99.999]
        )
        _, drifting = calculate_frequency_stability(
            [99.960, 99.980, 100.000, 100.020, 100.040]
        )

        self.assertLess(
            drifting,
            stable
        )

    def test_store_records_frequency_stability(self):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            for frequency in (
                    100.000,
                    100.002,
                    99.998,
                    100.001,
                    99.999
            ):
                store.update(
                    feature(frequency, 25.0)
                )

        stored = store.get(100.0)

        self.assertEqual(
            stored.frequency_observations,
            5
        )
        self.assertAlmostEqual(
            stored.frequency_drift_khz,
            1.0
        )
        self.assertGreaterEqual(
            stored.frequency_stability,
            0.96
        )

    def test_frequency_stability_rejects_invalid_values(self):
        for value in (
                0.0,
                -100.0,
                float("nan"),
                float("inf"),
                "100",
                True
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calculate_frequency_stability(
                        [100.0, 100.0, 100.0, 100.0, value]
                    )

    def test_prune_stale_removes_feature_and_history(self):
        store = FeatureStore()

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=10.0
        ):
            store.update(
                feature(100.0, 25.0)
            )

        with patch(
                "SIGNALS.feature_extractor.time.monotonic",
                return_value=41.0
        ):
            removed = store.prune_stale(
                30.0
            )

        self.assertEqual(removed, 1)
        self.assertEqual(store.features, {})
        self.assertEqual(
            store.bandwidth_history,
            {}
        )
        self.assertEqual(
            store.frequency_history,
            {}
        )

    def test_prune_stale_rejects_negative_age(self):
        with self.assertRaises(ValueError):
            FeatureStore().prune_stale(-1)


if __name__ == "__main__":
    unittest.main()
