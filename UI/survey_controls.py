from PyQt6.QtWidgets import (
    QLineEdit,
    QPushButton
)


def create_survey_controls():

    start_freq_input = QLineEdit()
    start_freq_input.setText("88")

    stop_freq_input = QLineEdit()
    stop_freq_input.setText("92")

    step_freq_input = QLineEdit()
    step_freq_input.setText("1")

    start_survey_button = QPushButton(
        "Start Survey"
    )

    return (
        start_freq_input,
        stop_freq_input,
        step_freq_input,
        start_survey_button
    )