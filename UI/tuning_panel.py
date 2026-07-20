from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget
)

from UI.theme import (
    TUNING_PANEL_MARGINS,
    TUNING_PANEL_SPACING,
    TUNING_PANEL_STYLESHEET
)


def create_tuning_panel(
        frequency_display,
        freq_label,
        freq_input,
        tune_button,
        auto_tune_button
):
    panel = QWidget()

    panel.setObjectName(
        "tuningPanel"
    )

    panel.setStyleSheet(
        TUNING_PANEL_STYLESHEET
    )

    layout = QVBoxLayout(
        panel
    )

    layout.setContentsMargins(
        *TUNING_PANEL_MARGINS
    )

    layout.setSpacing(
        TUNING_PANEL_SPACING
    )

    eyebrow = QLabel(
        "RECEIVER CENTER"
    )

    eyebrow.setObjectName(
        "tuningEyebrow"
    )

    eyebrow.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    frequency_display.setObjectName(
        "frequencyDisplay"
    )

    frequency_display.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    subtitle = QLabel(
        "Manual tuning or latest survey recommendation"
    )

    subtitle.setObjectName(
        "tuningSubtitle"
    )

    subtitle.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    freq_label.setText(
        "Center frequency (MHz)"
    )

    freq_label.setObjectName(
        "tuningFieldLabel"
    )

    freq_input.setObjectName(
        "tuningInput"
    )

    freq_input.setAccessibleName(
        "Receiver center frequency in megahertz"
    )

    freq_input.setToolTip(
        "Enter the RTL-SDR center frequency in MHz."
    )

    tune_button.setObjectName(
        "tunePrimaryButton"
    )

    tune_button.setToolTip(
        "Tune the receiver to the entered frequency."
    )

    auto_tune_button.setText(
        "Auto-tune best"
    )

    auto_tune_button.setObjectName(
        "autoTuneButton"
    )

    auto_tune_button.setToolTip(
        "Tune to the latest survey recommendation."
    )

    controls_layout = QHBoxLayout()

    controls_layout.setSpacing(
        8
    )

    controls_layout.addStretch()

    controls_layout.addWidget(
        freq_label
    )

    controls_layout.addWidget(
        freq_input
    )

    controls_layout.addWidget(
        tune_button
    )

    controls_layout.addWidget(
        auto_tune_button
    )

    controls_layout.addStretch()

    layout.addWidget(
        eyebrow
    )

    layout.addWidget(
        frequency_display
    )

    layout.addWidget(
        subtitle
    )

    layout.addSpacing(
        4
    )

    layout.addLayout(
        controls_layout
    )

    return panel
