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