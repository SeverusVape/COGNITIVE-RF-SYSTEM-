import unittest

from SIGNALS.signal_classifier import (
    classify_signal,
    classify_persistence,
    classify_strength
)
from SIGNALS.frequency_band import (
    classify_frequency_band,
    get_frequency_band_context
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
            0.0: "N",
            2.0: "A",
            5.0: "P",
            15.0: "L"
        }

        for count, persistence in expected.items():
            with self.subTest(count=count):
                self.assertEqual(
                    classify_persistence(
                        count
                    ),
                    persistence
                )

    def test_persistence_rejects_invalid_duration(self):
        for duration in (
                -1,
                float("nan"),
                float("inf"),
                "5",
                True
        ):
            with self.subTest(duration=duration):
                with self.assertRaises(ValueError):
                    classify_persistence(duration)

    def test_known_frequency_bands(self):
        expected = {
            100.0: "BC",
            120.0: "AIRBND",
            145.0: "2m",
            146.5: "2m",
            162.5: "NOAA",
            430.0: "70cm",
            445.0: "70cm",
            465.0: "GMRS",
            468.0: "GMRS"
        }

        for frequency, band in expected.items():
            with self.subTest(
                    frequency=frequency
            ):
                self.assertEqual(
                    classify_frequency_band(
                        frequency
                    ),
                    band
                )

    def test_band_context_is_independent_of_strength(self):
        weak_band = classify_signal(
            30,
            100.0
        )[0]

        strong_band = classify_signal(
            70,
            100.0
        )[0]

        self.assertEqual(
            weak_band,
            "BC"
        )
        self.assertEqual(
            strong_band,
            "BC"
        )

    def test_specific_noaa_context_precedes_weather_band(self):
        self.assertEqual(
            classify_frequency_band(162.5),
            "NOAA"
        )
        self.assertEqual(
            classify_frequency_band(162.2),
            "WX"
        )

    def test_invalid_or_unmapped_frequency_is_unknown(self):
        for frequency in (
                None,
                "invalid",
                float("nan"),
                200.0
        ):
            with self.subTest(
                    frequency=frequency
            ):
                self.assertEqual(
                    classify_frequency_band(
                        frequency
                    ),
                    "Unknown"
                )

    def test_context_exposes_code_name_and_limits(self):
        context = get_frequency_band_context(
            120.0
        )

        self.assertEqual(
            context.code,
            "AIRBND"
        )
        self.assertEqual(
            context.name,
            "Airband"
        )
        self.assertEqual(
            context.start_mhz,
            118.0
        )
        self.assertEqual(
            context.stop_mhz,
            137.0
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
