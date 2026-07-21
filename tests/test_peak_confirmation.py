import unittest

from SIGNALS.peak_confirmation import (
    PeakConfirmer
)


def peak(
        frequency,
        power=50.0,
        bandwidth=25.0
):
    return (
        frequency,
        power,
        bandwidth
    )


class PeakConfirmationTests(unittest.TestCase):

    def test_peak_is_confirmed_on_second_hit(self):
        confirmer = PeakConfirmer()

        self.assertEqual(
            confirmer.update([
                peak(100.0)
            ]),
            []
        )

        self.assertEqual(
            confirmer.update([
                peak(100.0, 52.0)
            ]),
            [
                peak(100.0, 52.0)
            ]
        )

    def test_single_frame_spike_is_not_confirmed(self):
        confirmer = PeakConfirmer()

        confirmer.update([
            peak(100.0)
        ])

        self.assertEqual(
            confirmer.update([
                peak(101.0)
            ]),
            []
        )

    def test_two_hits_can_span_one_missed_frame(self):
        confirmer = PeakConfirmer()

        confirmer.update([
            peak(100.0)
        ])
        confirmer.update([])

        self.assertEqual(
            confirmer.update([
                peak(100.0)
            ]),
            [
                peak(100.0)
            ]
        )

    def test_small_frequency_drift_is_matched(self):
        confirmer = PeakConfirmer(
            tolerance_khz=25.0
        )

        confirmer.update([
            peak(100.000)
        ])

        self.assertEqual(
            confirmer.update([
                peak(100.020)
            ]),
            [
                peak(100.020)
            ]
        )

    def test_frequency_outside_tolerance_is_not_matched(
            self
    ):
        confirmer = PeakConfirmer(
            tolerance_khz=25.0
        )

        confirmer.update([
            peak(100.000)
        ])

        self.assertEqual(
            confirmer.update([
                peak(100.030)
            ]),
            []
        )

    def test_old_detection_expires_from_window(self):
        confirmer = PeakConfirmer()

        confirmer.update([
            peak(100.0)
        ])
        confirmer.update([])
        confirmer.update([])

        self.assertEqual(
            confirmer.update([
                peak(100.0)
            ]),
            []
        )

    def test_reset_discards_previous_detections(self):
        confirmer = PeakConfirmer()

        confirmer.update([
            peak(100.0)
        ])
        confirmer.reset()

        self.assertEqual(
            confirmer.update([
                peak(100.0)
            ]),
            []
        )

    def test_invalid_configuration_is_rejected(self):
        invalid_configurations = (
            {
                "required_hits": 0
            },
            {
                "required_hits": True
            },
            {
                "required_hits": 3,
                "window_frames": 2
            },
            {
                "tolerance_khz": -1
            }
        )

        for configuration in invalid_configurations:
            with self.subTest(
                    configuration=configuration
            ):
                with self.assertRaises(
                        ValueError
                ):
                    PeakConfirmer(
                        **configuration
                    )

    def test_invalid_peak_is_rejected(self):
        confirmer = PeakConfirmer()

        with self.assertRaises(ValueError):
            confirmer.update([
                (
                    100.0,
                    50.0
                )
            ])


if __name__ == "__main__":
    unittest.main()
