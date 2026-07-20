from PyQt6.QtWidgets import QTextEdit


def create_survey_panel():

    survey_label = QTextEdit()

    survey_label.setObjectName(
        "surveyResultsCard"
    )

    survey_label.setAccessibleName(
        "Survey status and results"
    )

    survey_label.setReadOnly(
        True
    )

    survey_label.setText(
        "\n"
        "No Survey Data Available\n\n"
        "Run a survey to generate\n"
        "occupancy statistics,\n"
        "recommendations, and\n"
        "heatmap history."
    )

    survey_label.setFixedHeight(
        280
    )

    return survey_label
