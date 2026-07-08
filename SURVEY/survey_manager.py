# ==================================================
# SURVEY STATE
# ==================================================

survey_frequencies = []
survey_results = {}
survey_metrics = {}
current_survey_index = 0
occupancy_percent = 0
heatmap_history = []

best_frequency = None
best_occupancy = 0

def add_survey_result(
    survey_label,
    frequency,
    occupancy
):

    survey_results[
        round(frequency, 1)
    ] = round(occupancy)

    text = "Survey Results\n\n"

    for freq in sorted(
            survey_results.keys()
    ):

        text += (
            f"{freq:.1f} MHz | "
            f"{survey_results[freq]}%\n"
        )

    survey_label.setText(
        text
    )


def clear_survey(
    survey_label
):

    survey_results.clear()

    survey_label.setText(
        "Survey Results"
    )

# ==================================================
# SURVEY HELPERS
# ==================================================

def build_progress_bar(
        progress_percent
):

    bar_length = 20

    bars = int(
        progress_percent
        / 100
        * bar_length
    )

    progress_bar = (
        "▮" * bars +
        "▯" * (bar_length - bars)
    )

    return progress_bar

# ==================================================
# FREQUENCY GENERATION
# ==================================================

def generate_frequencies(
        start_mhz,
        stop_mhz,
        step_mhz
):

    frequencies = []

    frequency = start_mhz

    while frequency <= stop_mhz:
        frequencies.append(
            round(frequency, 6)
        )

        frequency = round(
            frequency + step_mhz,
            6
        )

    if (
            len(frequencies) > 0
            and frequencies[-1] != round(
                stop_mhz, 6
        )
    ):
        frequencies.append(
            round(
                stop_mhz,6
            )
        )

    return frequencies

# ==================================================
# RESULT RANKING
# ==================================================

def rank_frequencies(
        survey_results
):

    sorted_results = sorted(
        survey_results.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_results

# ==================================================
# RESULTS TEXT
# ==================================================

def build_results_text(

        sorted_results,
        points_scanned,
        average_occupancy,
        recommendation
):
    recommendation_title = recommendation[
        "title"
    ]

    recommended_frequency = recommendation[
        "frequency"
    ]

    recommended_occupancy = recommendation[
        "occupancy"
    ]

    recommended_score = recommendation[
        "score"
    ]

    score_details = recommendation.get(
        "score_details"
    )

    recommended_reason = recommendation[
        "reason"
    ]

    results_text = (
        "========== SURVEY COMPLETE ==========\n\n"

        f"Points Scanned:\n"
        f"{points_scanned}\n\n"

        f"Average Occupancy:\n"
        f"{average_occupancy:.1f}%\n\n"

        "\n"
        "========== RECOMMENDED ==========\n\n"
        f"({recommendation_title})\n\n"
        f"Frequency:\n"
        f"{recommended_frequency:.3f} MHz\n\n"
        f"Occupancy:\n"
        f"{recommended_occupancy:.1f}%\n"
    )

    if recommended_score is not None:

        max_possible_score = 115

        results_text += (

            "\n"
            "Overall Score:\n"
            f"{recommended_score:.1f} / {max_possible_score}\n\n"

        )

    if score_details:
        results_text += (
            "Score Breakdown:\n"
            f"Occupancy Score:   "
            f"{score_details['occupancy_score']:.1f}\n"
            f"Power Score:       "
            f"{score_details['power_score']:.1f}\n"
            f"Persistence Score: "
            f"{score_details['persistence_score']:.1f}\n"
            f"Age Score:         "
            f"{score_details['age_score']:.1f}\n"
            f"Strength Score:    "
            f"{score_details['strength_score']:.1f}\n"
            f"Max Power:         "
            f"{score_details['max_power']:.1f} dB\n"
            f"Average Power:     "
            f"{score_details['average_power']:.1f} dB\n\n"
        )

    if recommended_reason:

        results_text += (
            "\n"
            "Decision Reason:\n"

        )

        for reason in recommended_reason:
            results_text += (

                f"✓ {reason}\n"

            )

    results_text += (
        "\n"
        "Measured Occupancy\n\n"
    )

    for freq, occupancy in sorted_results[:5]:
        results_text += (
            f"{freq:.3f} MHz"
            f" -> "
            f"{occupancy:.1f}%\n"
        )

    return results_text

# ==================================================
# STATUS TEXT
# ==================================================

def build_status_text(
        frequency,
        current_point,
        total_points,
        progress_percent,
        progress_bar
):

    survey_text = (
        "SURVEY STATUS\n\n"
        f"Frequency:\n"
        f"{frequency:.3f} MHz\n\n"
        f"Point:\n"
        f"{current_point}"
        f" / "
        f"{total_points}\n\n"
        f"Progress:\n"
        f"{progress_bar}\n"
        f"{progress_percent}%"
    )

    return survey_text