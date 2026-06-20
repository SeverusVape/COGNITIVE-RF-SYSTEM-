from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton
)

def create_control_widgets():

    freq_label = QLabel(
        "Frequency (MHz)"
    )

    freq_input = QLineEdit()

    freq_input.setFixedWidth(
        150
    )

    freq_input.setText("100")

    tune_button = QPushButton(
        "Tune"
    )

    survey_button = QPushButton(
        "Add Survey Point"
    )

    clear_survey_button = QPushButton(
        "Clear Survey"
    )

    auto_tune_button = QPushButton(
        "AUTO TUNE BEST"
    )

    return (
        freq_label,
        freq_input,
        tune_button,
        survey_button,
        clear_survey_button,
        auto_tune_button
    )