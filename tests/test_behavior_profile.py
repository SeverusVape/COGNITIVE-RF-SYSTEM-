import unittest

from SIGNALS.behavior_profile import (
    build_behavior_profile,
    describe_activity,
    describe_stability
)


class BehaviorProfileTests(unittest.TestCase):

    def test_stability_descriptors_have_clear_boundaries(self):
        self.assertEqual(
            describe_stability(0.8),
            "Stable"
        )
        self.assertEqual(
            describe_stability(0.5),
            "Moderately stable"
        )
        self.assertEqual(
            describe_stability(0.49),
            "Variable"
        )

    def test_activity_descriptors_have_clear_boundaries(self):
        self.assertEqual(
            describe_activity(75.0),
            "Continuous"
        )
        self.assertEqual(
            describe_activity(25.0),
            "Intermittent"
        )
        self.assertEqual(
            describe_activity(24.9),
            "Sporadic"
        )

    def test_missing_measurements_remain_pending(self):
        profile = build_behavior_profile({})

        self.assertIsNone(profile)

        profile = build_behavior_profile({
            "frequency_stability": None,
            "bandwidth_stability": None,
            "duty_cycle_percent": None
        })

        self.assertEqual(
            set(profile.values()),
            {"Collecting data"}
        )

    def test_profile_describes_measurements_without_identity_claim(self):
        profile = build_behavior_profile({
            "frequency_stability": 0.91,
            "bandwidth_stability": 0.67,
            "duty_cycle_percent": 66.7
        })

        self.assertEqual(profile, {
            "frequency_behavior": "Stable",
            "bandwidth_behavior": "Moderately stable",
            "activity_pattern": "Intermittent"
        })

    def test_invalid_measurements_are_rejected(self):
        for invalid in (-0.1, 1.1, float("nan"), True):
            with self.subTest(stability=invalid):
                with self.assertRaises(ValueError):
                    describe_stability(invalid)

        for invalid in (-1, 101, float("inf"), True):
            with self.subTest(duty_cycle=invalid):
                with self.assertRaises(ValueError):
                    describe_activity(invalid)


if __name__ == "__main__":
    unittest.main()
