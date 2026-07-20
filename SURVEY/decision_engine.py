from statistics import median


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
        score_margin=None
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
        "score_margin": score_margin

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

        feature = None

        if not feature_snapshot_available:
            feature = find_nearest_feature(
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

        elif feature is not None:
            persistence = feature.persistence
            age_seconds = feature.age_seconds
            strength = feature.strength

        else:
            persistence = None
            age_seconds = 0
            strength = None

        if (
                feature_snapshot is not None
                or feature is not None
        ):
            if persistence == "A":
                persistence_bonus = 5

            elif persistence == "P":
                persistence_bonus = 10

            elif persistence == "L":
                persistence_bonus = 15

            if age_seconds >= 30:
                age_bonus = 10

            elif age_seconds >= 15:
                age_bonus = 6

            elif age_seconds >= 5:
                age_bonus = 3

            if strength == "M":
                strength_bonus = 3

            elif strength == "S":
                strength_bonus = 6


        # ----------------------------------
        # Occupancy Score (0–50)
        # Lower occupancy = higher score
        # ----------------------------------

        occupancy_score = min(
            50,
            max(
                0,
                (
                    100 - occupancy
                )
                / 100
                * 50
            )
        )

        # ----------------------------------
        # Maximum Power Score (0–30)
        # Stronger signal = higher score
        # ----------------------------------

        power_score_midpoint = 15.0
        power_score_per_db = 0.3

        power_score = min(
            30,
            max(
                0,
                power_score_midpoint
                + (
                    max_power
                    - survey_median_power
                )
                * power_score_per_db
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
        )

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
