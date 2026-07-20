from PyQt6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QComboBox
)


def create_survey_controls():

    start_freq_input = QLineEdit()
    start_freq_input.setText("88")
    start_freq_input.setObjectName(
        "surveyInput"
    )
    start_freq_input.setAccessibleName(
        "Survey start frequency in megahertz"
    )

    stop_freq_input = QLineEdit()
    stop_freq_input.setText("92")
    stop_freq_input.setObjectName(
        "surveyInput"
    )
    stop_freq_input.setAccessibleName(
        "Survey stop frequency in megahertz"
    )

    step_freq_input = QLineEdit()
    step_freq_input.setText("1")
    step_freq_input.setObjectName(
        "surveyInput"
    )
    step_freq_input.setAccessibleName(
        "Survey frequency step in megahertz"
    )

    decision_mode_combo = QComboBox()
    decision_mode_combo.setObjectName(
        "surveyMode"
    )
    decision_mode_combo.setAccessibleName(
        "Survey decision mode"
    )

    decision_mode_combo.addItems([
        "Find Free Channel",
        "Find Active Signal",
        "Smart Recommendation",
    ])

    decision_mode_combo.setCurrentIndex(0)

    start_survey_button = QPushButton(
        "Start Survey"
    )
    start_survey_button.setObjectName(
        "surveyPrimaryButton"
    )

    return (
        start_freq_input,
        stop_freq_input,
        step_freq_input,
        decision_mode_combo,
        start_survey_button
    )
