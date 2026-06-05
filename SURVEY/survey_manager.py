def add_survey_result(
    survey_label,
    frequency,
    occupancy
):

    current_text = survey_label.toPlainText()

    new_line = (
        f"{frequency:.1f} MHz | "
        f"{occupancy:.0f}%\n"
    )

    survey_label.setText(
        current_text + "\n" + new_line
    )