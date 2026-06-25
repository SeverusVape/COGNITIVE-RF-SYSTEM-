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

    return (
        best_frequency,
        best_occupancy
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

    return (
        best_frequency,
        best_occupancy
    )

# ==================================================
# DECISION ENGINE
# ==================================================

def make_decision(
        mode,
        survey_results
):

    if mode == "FREE":
        return find_free_channel(
            survey_results
        )

    elif mode == "ACTIVE":
        return find_active_signal(
            survey_results
        )

    return find_free_channel(
        survey_results
    )