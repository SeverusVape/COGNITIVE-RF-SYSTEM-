import numpy as np


REQUIRED_MEASUREMENTS = (
    "occupancy",
    "max_power",
    "average_power"
)


def aggregate_measurements(
        measurements
):
    if not measurements:
        return None

    normalized_measurements = {
        name: []
        for name in REQUIRED_MEASUREMENTS
    }

    for measurement in measurements:
        if (
                not isinstance(measurement, dict)
                or not all(
                    name in measurement
                    for name in REQUIRED_MEASUREMENTS
                )
        ):
            return None

        try:
            values = {
                name: float(
                    measurement[name]
                )
                for name in REQUIRED_MEASUREMENTS
            }
        except (TypeError, ValueError):
            return None

        if not all(
                np.isfinite(value)
                for value in values.values()
        ):
            return None

        for name, value in values.items():
            normalized_measurements[
                name
            ].append(
                value
            )

    return {
        name: round(
            float(
                np.median(values)
            ),
            1
        )
        for name, values in normalized_measurements.items()
    }
