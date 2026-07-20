import unittest

from unittest.mock import patch

import SIGNALS.signal_history as history


class SignalHistoryTests(unittest.TestCase):

    def setUp(self):
        history.signal_history.clear()
        history.signal_first_seen.clear()
        history.signal_last_seen.clear()
        history.seen_this_cycle.clear()
        history.history_update_count = 0

    def test_same_signal_counts_once_per_update_cycle(self):
        with patch(
                "SIGNALS.signal_history.time.time",
                return_value=100.0
        ), patch(
                "SIGNALS.signal_history.time.monotonic",
                return_value=50.0
        ):
            first = history.update_signal_history(
                100.04
            )
            duplicate = history.update_signal_history(
                100.02
            )

        self.assertEqual(first[0], 1)
        self.assertEqual(duplicate[0], 1)

        history.reset_cycle_tracking()

        with patch(
                "SIGNALS.signal_history.time.time",
                return_value=101.0
        ), patch(
                "SIGNALS.signal_history.time.monotonic",
                return_value=51.0
        ):
            next_cycle = (
                history.update_signal_history(
                    100.0
                )
            )

        self.assertEqual(next_cycle[0], 2)
        self.assertEqual(next_cycle[1], 1)

    def test_occupancy_uses_history_update_count(self):
        history.signal_history[100.0] = 3
        history.history_update_count = 4

        self.assertEqual(
            history.get_occupancy_percent(
                100.0
            ),
            75.0
        )

    def test_pruning_removes_all_signal_state(self):
        history.signal_history[100.0] = 5
        history.signal_first_seen[100.0] = 1.0
        history.signal_last_seen[100.0] = 10.0
        history.seen_this_cycle.add(100.0)

        with patch(
                "SIGNALS.signal_history.time.monotonic",
                return_value=41.0
        ):
            removed = history.prune_stale_history(
                30.0
            )

        self.assertEqual(removed, 1)
        self.assertNotIn(
            100.0,
            history.signal_history
        )
        self.assertNotIn(
            100.0,
            history.signal_first_seen
        )
        self.assertNotIn(
            100.0,
            history.signal_last_seen
        )
        self.assertNotIn(
            100.0,
            history.seen_this_cycle
        )

    def test_pruning_rejects_negative_age(self):
        with self.assertRaises(ValueError):
            history.prune_stale_history(-1)


if __name__ == "__main__":
    unittest.main()
