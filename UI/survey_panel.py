from PyQt6.QtWidgets import QTextEdit


def create_survey_panel():

    survey_label = QTextEdit()

    survey_label.setReadOnly(
        True
    )

    survey_label.setText(
        "Survey Results\n"
    )

    survey_label.setFixedHeight(
        300
    )

    return survey_label