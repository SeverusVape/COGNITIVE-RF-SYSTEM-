import unittest

from unittest.mock import patch

from SIGNALS.feature_extractor import (
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

    def test_prune_stale_rejects_negative_age(self):
        with self.assertRaises(ValueError):
            FeatureStore().prune_stale(-1)


if __name__ == "__main__":
    unittest.main()
