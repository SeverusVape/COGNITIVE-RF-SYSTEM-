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
# SMART RECOMMENDATION
# ==================================================

def smart_recommendation(

        survey_results,
        survey_metrics,
        heatmap_history
):

    free_recommendation = find_free_channel(
        survey_results
    )

    active_recommendation = find_active_signal(
        survey_results
    )

    # Placeholder:
    # Until Smart scoring is implemented,
    # return the FREE recommendation.

    return build_recommendation(

        frequency=free_recommendation["frequency"],

        occupancy=free_recommendation["occupancy"],

        mode="SMART",

        title="SMART RECOMMENDATION",

        score=None,

        reason=[
            "Using free-channel fallback",
            "Lowest occupancy selected"
        ]

    )
# ==================================================
# DECISION ENGINE
# ==================================================

def make_decision(

        mode,
        survey_results,
        survey_metrics=None,
        heatmap_history=None
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
            heatmap_history

        )

    return find_free_channel(
        survey_results
    )