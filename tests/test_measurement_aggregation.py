import unittest

from UTILS.measurement_aggregation import (
    aggregate_measurements
)


def measurement(
        occupancy,
        max_power,
        average_power
):
    return {
        "occupancy": occupancy,
        "max_power": max_power,
        "average_power": average_power
    }


class MeasurementAggregationTests(
        unittest.TestCase
):

    def test_minimum_frame_count_is_enforced(self):
        frames = [
            measurement(8, 48, 20),
            measurement(9, 49, 21)
        ]

        self.assertIsNone(
            aggregate_measurements(
                frames,
                minimum_count=3
            )
        )

    def test_median_measurement_is_returned(self):
        frames = [
            measurement(8, 48, 20),
            measurement(10, 50, 22),
            measurement(9, 49, 21)
        ]

        self.assertEqual(
            aggregate_measurements(
                frames,
                minimum_count=3
            ),
            measurement(
                9.0,
                49.0,
                21.0
            )
        )

    def test_single_frame_outlier_is_rejected(self):
        frames = [
            measurement(9, 49, 20),
            measurement(10, 50, 21),
            measurement(95, 100, 90),
            measurement(8, 48, 19),
            measurement(9, 49, 20)
        ]

        self.assertEqual(
            aggregate_measurements(
                frames,
                minimum_count=3
            ),
            measurement(
                9.0,
                49.0,
                20.0
            )
        )

    def test_missing_measurement_field_is_rejected(self):
        frames = [
            measurement(8, 48, 20),
            measurement(9, 49, 21),
            {
                "occupancy": 10,
                "max_power": 50
            }
        ]

        self.assertIsNone(
            aggregate_measurements(
                frames,
                minimum_count=3
            )
        )

    def test_invalid_measurement_value_is_rejected(self):
        invalid_values = (
            "invalid",
            float("nan"),
            float("inf")
        )

        for invalid_value in invalid_values:
            with self.subTest(
                    invalid_value=invalid_value
            ):
                frames = [
                    measurement(8, 48, 20),
                    measurement(9, 49, 21),
                    measurement(
                        invalid_value,
                        50,
                        22
                    )
                ]

                self.assertIsNone(
                    aggregate_measurements(
                        frames,
                        minimum_count=3
                    )
                )

    def test_invalid_minimum_count_is_rejected(self):
        frames = [
            measurement(8, 48, 20)
        ]

        for invalid_count in (
                0,
                -1,
                1.5,
                True
        ):
            with self.subTest(
                    invalid_count=invalid_count
            ):
                with self.assertRaises(
                        ValueError
                ):
                    aggregate_measurements(
                        frames,
                        minimum_count=invalid_count
                    )


if __name__ == "__main__":
    unittest.main()
