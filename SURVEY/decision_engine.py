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
        score_details=None
):

    return {

        "frequency": frequency,
        "occupancy": occupancy,
        "mode": mode,
        "title": title,
        "score": score,
        "reason": reason,
        "score_details": score_details

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
        max_distance_mhz=0.5
):

    if feature_store is None:
        return None

    if len(feature_store.features) == 0:
        return None

    nearest_feature = None
    nearest_distance = float("inf")

    for feature_frequency, feature in feature_store.features.items():

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

    frequency_scores = {}

    for frequency, metrics in survey_metrics.items():
        occupancy = metrics["occupancy"]
        max_power = metrics["max_power"]
        average_power = metrics["average_power"]
        score = 0

        feature = find_nearest_feature(
            frequency,
            feature_store
        )

        persistence_bonus = 0
        age_bonus = 0
        strength_bonus = 0

        if feature is not None:

            if feature.persistence == "A":
                persistence_bonus = 5

            elif feature.persistence == "P":
                persistence_bonus = 10

            elif feature.persistence == "L":
                persistence_bonus = 15

            if feature.age_seconds >= 30:
                age_bonus = 10

            elif feature.age_seconds >= 15:
                age_bonus = 6

            elif feature.age_seconds >= 5:
                age_bonus = 3

            if feature.strength == "M":
                strength_bonus = 3

            elif feature.strength == "S":
                strength_bonus = 6


        # ----------------------------------
        # Occupancy Score (0–50)
        # Lower occupancy = higher score
        # ----------------------------------

        occupancy_score = max(
            0,
            50 - occupancy
        )

        # ----------------------------------
        # Maximum Power Score (0–30)
        # Stronger signal = higher score
        # ----------------------------------

        power_score = min(
            30,
            max(
                0,
                max_power / 100 * 30
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

    # BEST SMART SCORE
    best_frequency = max(
        frequency_scores,
        key=lambda frequency: frequency_scores[frequency]["score"]
    )

    best_score = frequency_scores[
        best_frequency
    ]["score"]

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

        score_details=score_details

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
