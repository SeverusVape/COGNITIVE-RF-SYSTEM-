import math

from numbers import Real


def _validate_percent(value, label):
    if (
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not math.isfinite(value)
            or value < 0
            or value > 100
    ):
        raise ValueError(
            f"{label} must be a finite number from 0 to 100."
        )


def describe_stability(stability):
    if stability is None:
        return "Collecting data"

    if (
            isinstance(stability, bool)
            or not isinstance(stability, Real)
            or not math.isfinite(stability)
            or stability < 0
            or stability > 1
    ):
        raise ValueError(
            "Stability must be a finite number from 0 to 1."
        )

    if stability >= 0.8:
        return "Stable"

    if stability >= 0.5:
        return "Moderately stable"

    return "Variable"


def describe_activity(duty_cycle_percent):
    if duty_cycle_percent is None:
        return "Collecting data"

    _validate_percent(
        duty_cycle_percent,
        "Duty cycle"
    )

    if duty_cycle_percent >= 75:
        return "Continuous"

    if duty_cycle_percent >= 25:
        return "Intermittent"

    return "Sporadic"


def build_behavior_profile(feature_snapshot):
    if not feature_snapshot:
        return None

    return {
        "frequency_behavior": describe_stability(
            feature_snapshot.get(
                "frequency_stability"
            )
        ),
        "bandwidth_behavior": describe_stability(
            feature_snapshot.get(
                "bandwidth_stability"
            )
        ),
        "activity_pattern": describe_activity(
            feature_snapshot.get(
                "duty_cycle_percent"
            )
        )
    }
