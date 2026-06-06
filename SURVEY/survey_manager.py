survey_results = {}


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