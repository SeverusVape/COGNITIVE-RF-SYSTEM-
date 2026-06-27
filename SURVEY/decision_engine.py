# ==================================================
# BUILD RECOMMENDATION
# ==================================================

def build_recommendation(

        frequency,
        occupancy,
        mode,
        title,
        score=None,
        reason=None
):

    return {

        "frequency": frequency,
        "occupancy": occupancy,
        "mode": mode,
        "title": title,
        "score": score,
        "reason": reason

    }
# ==================================================
# FIND FREE CHANNEL
# ==================================================

def find_free_channel(
        survey_results
):

    if len(survey_results) == 0:
        return None, None

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
        return None, None

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

    free_recommendation = find_free_channel(
        survey_results
    )

    active_recommendation = find_active_signal(
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

        if feature is not None:
            print(
                f"{frequency:.1f} MHz -> "
                f"{feature.frequency:.3f} MHz | "
                f"PERSIST={feature.persistence} | "
                f"AGE={feature.age_seconds:.1f}s"
            )


        # ----------------------------------
        # Occupancy Score (0–50)
        # Lower occupancy = higher score
        # ----------------------------------

        score += max(
            0,
            50 - occupancy
        )

        # ----------------------------------
        # Maximum Power Score (0–30)
        # Stronger signal = higher score
        # ----------------------------------

        score += max_power / 100 * 30

        frequency_scores[frequency] = score

    # BEST SMART SCORE
    best_frequency = max(
        frequency_scores,
        key=frequency_scores.get
    )

    best_score = frequency_scores[
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

        ]

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