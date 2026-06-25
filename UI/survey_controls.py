from PyQt6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QComboBox
)


def create_survey_controls():

    start_freq_input = QLineEdit()
    start_freq_input.setText("88")

    stop_freq_input = QLineEdit()
    stop_freq_input.setText("92")

    step_freq_input = QLineEdit()
    step_freq_input.setText("1")

    decision_mode_combo = QComboBox()

    decision_mode_combo.addItems([
        "Find Free Channel",
        "Find Active Signal",
        "Smart Recommendation",
    ])

    decision_mode_combo.setCurrentIndex(0)

    start_survey_button = QPushButton(
        "Start Survey"
    )

    return (
        start_freq_input,
        stop_freq_input,
        step_freq_input,
        decision_mode_combo,
        start_survey_button
    )