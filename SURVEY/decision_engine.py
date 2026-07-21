import math

from statistics import median

from UTILS.config import (
    SMART_AGE_5_SECONDS_SCORE,
    SMART_AGE_15_SECONDS_SCORE,
    SMART_AGE_30_SECONDS_SCORE,
    SMART_MAX_SCORE,
    SMART_OCCUPANCY_MAX_SCORE,
    SMART_PERSISTENCE_ACTIVE_SCORE,
    SMART_PERSISTENCE_LONG_SCORE,
    SMART_PERSISTENCE_PERSISTENT_SCORE,
    SMART_POWER_MAX_SCORE,
    SMART_POWER_SCORE_MIDPOINT,
    SMART_POWER_SCORE_PER_DB,
    SMART_STRENGTH_MEDIUM_SCORE,
    SMART_STRENGTH_STRONG_SCORE
)


def classify_decision_confidence(
        score_margin,
        maximum_score=SMART_MAX_SCORE
):
    if score_margin is None:
        return "N/A"

    if (
            isinstance(score_margin, bool)
            or not isinstance(
                score_margin,
                (int, float)
            )
            or not math.isfinite(
                score_margin
            )
            or score_margin < 0
    ):
        raise ValueError(
            "Score margin must be a finite, "
            "non-negative number."
        )

    if (
            isinstance(maximum_score, bool)
            or not isinstance(
                maximum_score,
                (int, float)
            )
            or not math.isfinite(
                maximum_score
            )
            or maximum_score <= 0
    ):
        raise ValueError(
            "Maximum score must be a finite, "
            "positive number."
        )

    normalized_margin = (
        score_margin
        / maximum_score
    )

    if normalized_margin < 0.03:
        return "LOW"

    if normalized_margin < 0.08:
        return "MODERATE"

    return "HIGH"


# ==================================================
# BUILD RECOMMENDATION
# ==================================================

def build_recommendation(

        frequency,
        occupancy,
        mode,
        title,
        score=None,
        reason=None,
        score_details=None,
        runner_up_frequency=None,
        runner_up_score=None,
        score_margin=None,
        decision_confidence="N/A"
):

    return {

        "frequency": frequency,
        "occupancy": occupancy,
        "mode": mode,
        "title": title,
        "score": score,
        "reason": reason,
        "score_details": score_details,
        "runner_up_frequency": runner_up_frequency,
        "runner_up_score": runner_up_score,
        "score_margin": score_margin,
        "decision_confidence": decision_confidence

    }
# ==================================================
# FIND FREE CHANNEL
# ==================================================

def find_free_channel(
        survey_results
):

    if len(survey_results) == 0:
        return build_recommendation(
            frequency=None,
            occupancy=None,
            mode="FREE",
            title="NO SURVEY DATA",
            reason=[
                "No survey results available"
            ]
        )

    best_frequency = min(
        survey_results,
        key=survey_results.get
    )

    best_occupancy = survey_results[
        best_frequency
    ]

    return build_recommendation(

        frequency=best_frequency,
        occupancy=best_occupancy,
        mode="FREE",
        title="FREE CHANNEL",
        reason=[
            "Lowest occupancy"
        ]
    )

# ==================================================
# FIND ACTIVE SIGNAL
# ==================================================

def find_active_signal(
        survey_results
):

    if len(survey_results) == 0:
        return build_recommendation(
            frequency=None,
            occupancy=None,
            mode="ACTIVE",
            title="NO SURVEY DATA",
            reason=[
                "No survey results available"
            ]
        )

    best_frequency = max(
        survey_results,
        key=survey_results.get
    )

    best_occupancy = survey_results[
        best_frequency
    ]

    return build_recommendation(

        frequency=best_frequency,
        occupancy=best_occupancy,
        mode="ACTIVE",
        title="MOST ACTIVE SIGNAL",
        reason=[
            "Highest occupancy"
        ]

    )

# ==================================================
# FIND NEAREST FEATURE
# ==================================================

def find_nearest_feature(
        survey_frequency,
        feature_store,
        max_distance_mhz=0.5,
        max_age_seconds=None
):

    if feature_store is None:
        return None

    if len(feature_store.features) == 0:
        return None

    nearest_feature = None
    nearest_distance = float("inf")

    for feature_frequency, feature in feature_store.features.items():
        if max_age_seconds is not None:
            seconds_since_seen = (
                feature_store.get_seconds_since_seen(
                    feature_frequency
                )
            )

            if (
                    seconds_since_seen is None
                    or seconds_since_seen > max_age_seconds
            ):
                continue

        distance = abs(
            feature_frequency - survey_frequency
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest_feature = feature

    if nearest_distance > max_distance_mhz:
        return None

    return nearest_feature


def build_feature_snapshot(
        survey_frequency,
        feature_store,
        max_distance_mhz=0.5,
        max_age_seconds=None
):
    feature = find_nearest_feature(
        survey_frequency,
        feature_store,
        max_distance_mhz=max_distance_mhz,
        max_age_seconds=max_age_seconds
    )

    if feature is None:
        return None

    return {
        "frequency": float(
            feature.frequency
        ),
        "persistence": feature.persistence,
        "age_seconds": float(
            feature.age_seconds
        ),
        "strength": feature.strength,
        "bandwidth_stability": (
            feature.bandwidth_stability
        ),
        "bandwidth_observations": (
            feature.bandwidth_observations
        ),
        "frequency_drift_khz": (
            feature.frequency_drift_khz
        ),
        "frequency_stability": (
            feature.frequency_stability
        ),
        "frequency_observations": (
            feature.frequency_observations
        ),
        "duty_cycle_percent": float(
            feature.duty_cycle_percent
        )
    }

# ==================================================
# SMART RECOMMENDATION
# ==================================================

def smart_recommendation(

        survey_results,
        survey_metrics,
        heatmap_history,
        feature_store
):

    if survey_metrics is None:
        return find_free_channel(
            survey_results
        )

    if len(survey_metrics) == 0:
        return find_free_channel(
            survey_results
        )

    survey_median_power = median(
        metrics["max_power"]
        for metrics in survey_metrics.values()
    )

    frequency_scores = {}

    for frequency, metrics in survey_metrics.items():
        occupancy = metrics["occupancy"]
        max_power = metrics["max_power"]
        average_power = metrics["average_power"]
        score = 0

        feature_snapshot_available = (
            "feature_snapshot" in metrics
        )

        feature_snapshot = metrics.get(
            "feature_snapshot"
        )

        if not feature_snapshot_available:
            feature_snapshot = build_feature_snapshot(
                frequency,
                feature_store
            )

        persistence_bonus = 0
        age_bonus = 0
        strength_bonus = 0

        if feature_snapshot is not None:
            persistence = feature_snapshot.get(
                "persistence"
            )

            age_seconds = feature_snapshot.get(
                "age_seconds",
                0
            )

            strength = feature_snapshot.get(
                "strength"
            )

        else:
            persistence = None
            age_seconds = 0
            strength = None

        if feature_snapshot is not None:
            if persistence == "A":
                persistence_bonus = (
                    SMART_PERSISTENCE_ACTIVE_SCORE
                )

            elif persistence == "P":
                persistence_bonus = (
                    SMART_PERSISTENCE_PERSISTENT_SCORE
                )

            elif persistence == "L":
                persistence_bonus = (
                    SMART_PERSISTENCE_LONG_SCORE
                )

            if age_seconds >= 30:
                age_bonus = (
                    SMART_AGE_30_SECONDS_SCORE
                )

            elif age_seconds >= 15:
                age_bonus = (
                    SMART_AGE_15_SECONDS_SCORE
                )

            elif age_seconds >= 5:
                age_bonus = (
                    SMART_AGE_5_SECONDS_SCORE
                )

            if strength == "M":
                strength_bonus = (
                    SMART_STRENGTH_MEDIUM_SCORE
                )

            elif strength == "S":
                strength_bonus = (
                    SMART_STRENGTH_STRONG_SCORE
                )


        # ----------------------------------
        # Occupancy Score (0–50)
        # Lower occupancy = higher score
        # ----------------------------------

        occupancy_score = min(
            SMART_OCCUPANCY_MAX_SCORE,
            max(
                0,
                (
                    100 - occupancy
                )
                / 100
                * SMART_OCCUPANCY_MAX_SCORE
            )
        )

        # ----------------------------------
        # Maximum Power Score (0–30)
        # Stronger signal = higher score
        # ----------------------------------

        power_score = min(
            SMART_POWER_MAX_SCORE,
            max(
                0,
                SMART_POWER_SCORE_MIDPOINT
                + (
                    max_power
                    - survey_median_power
                )
                * SMART_POWER_SCORE_PER_DB
            )
        )

        score = (
                occupancy_score
                + power_score
                + persistence_bonus
                + age_bonus
                + strength_bonus
        )

        frequency_scores[frequency] = {
            "score": score,
            "occupancy_score": occupancy_score,
            "power_score": power_score,
            "persistence_score": persistence_bonus,
            "age_score": age_bonus,
            "strength_score": strength_bonus,
            "max_power": max_power,
            "average_power": average_power
        }

    ranked_frequencies = sorted(
        frequency_scores,
        key=lambda frequency: (
            frequency_scores[
                frequency
            ]["score"],
            -survey_metrics[
                frequency
            ]["occupancy"],
            survey_metrics[
                frequency
            ]["max_power"],
            -frequency
        ),
        reverse=True
    )

    best_frequency = ranked_frequencies[
        0
    ]

    best_score = frequency_scores[
        best_frequency
    ]["score"]

    runner_up_frequency = None
    runner_up_score = None
    score_margin = None

    if len(ranked_frequencies) > 1:
        runner_up_frequency = ranked_frequencies[
            1
        ]

        runner_up_score = frequency_scores[
            runner_up_frequency
        ]["score"]

        score_margin = (
            best_score
            - runner_up_score
        )

    score_details = frequency_scores[
        best_frequency
    ]

    decision_confidence = (
        classify_decision_confidence(
            score_margin
        )
    )

    return build_recommendation(

        frequency=best_frequency,

        occupancy=survey_metrics[
            best_frequency
        ]["occupancy"],

        mode="SMART",

        title="SMART RECOMMENDATION",

        score=round(
            best_score,
            1
        ),

        reason=[

            "Highest overall score",

            "Balanced occupancy and signal strength"

        ],

        score_details=score_details,

        runner_up_frequency=runner_up_frequency,

        runner_up_score=(
            None
            if runner_up_score is None
            else round(
                runner_up_score,
                1
            )
        ),

        score_margin=(
            None
            if score_margin is None
            else round(
                score_margin,
                1
            )
        ),

        decision_confidence=decision_confidence

    )
# ==================================================
# DECISION ENGINE
# ==================================================

def make_decision(

        mode,
        survey_results,
        survey_metrics=None,
        heatmap_history=None,
        feature_store=None
):

    if mode == "FREE":

        return find_free_channel(
            survey_results
        )

    elif mode == "ACTIVE":

        return find_active_signal(
            survey_results
        )

    elif mode == "SMART":

        return smart_recommendation(

            survey_results,
            survey_metrics,
            heatmap_history,
            feature_store

        )

    return find_free_channel(
        survey_results
    )
