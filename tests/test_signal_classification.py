import unittest

from SIGNALS.signal_classifier import (
    classify_signal,
    classify_strength
)
from SIGNALS.signal_type_classifier import (
    classify_signal_type
)
from SIGNALS.feature_extractor import SignalFeatures


class SignalClassificationTests(unittest.TestCase):

    def test_strength_boundaries(self):
        self.assertEqual(
            classify_strength(45),
            "W"
        )
        self.assertEqual(
            classify_strength(45.1),
            "M"
        )
        self.assertEqual(
            classify_strength(60),
            "M"
        )
        self.assertEqual(
            classify_strength(60.1),
            "S"
        )

    def test_persistence_boundaries(self):
        expected = {
            1: "N",
            5: "A",
            10: "P",
            20: "L"
        }

        for count, persistence in expected.items():
            with self.subTest(count=count):
                self.assertEqual(
                    classify_signal(
                        50,
                        100.0,
                        count
                    )[2],
                    persistence
                )

    def test_known_frequency_bands(self):
        expected = {
            100.0: "BC",
            120.0: "AIRBND",
            145.0: "2m",
            146.5: "2m-RPT",
            162.5: "NOAA",
            430.0: "70cm",
            445.0: "70cm-RPT",
            465.0: "GMRS"
        }

        for frequency, band in expected.items():
            with self.subTest(
                    frequency=frequency
            ):
                self.assertEqual(
                    classify_signal(
                        50,
                        frequency
                    )[0],
                    band
                )

    def test_feature_signal_type_uses_frequency_band(self):
        sample = SignalFeatures(
            frequency=120.0,
            peak_power=50.0,
            average_power=25.0,
            bandwidth_khz=25.0,
            occupancy_percent=10.0,
            age_seconds=0.0,
            strength="M",
            persistence="N"
        )

        self.assertEqual(
            classify_signal_type(sample),
            "Airband"
        )


if __name__ == "__main__":
    unittest.main()
