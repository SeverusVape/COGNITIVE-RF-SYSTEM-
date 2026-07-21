from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit
)

from PyQt6.QtCore import Qt

from UI.theme import (
    SURVEY_POPUP_MARGINS,
    SURVEY_POPUP_MINIMUM_SIZE,
    SURVEY_POPUP_SIZE,
    SURVEY_POPUP_SPACING,
    SURVEY_POPUP_STYLESHEET
)


class SurveyPopup(QWidget):

    def __init__(
            self,
            results_text
    ):

        super().__init__()

        self.setWindowTitle(
            "Survey Results"
        )

        self.resize(
            *SURVEY_POPUP_SIZE
        )

        self.setMinimumSize(
            *SURVEY_POPUP_MINIMUM_SIZE
        )

        self.setStyleSheet(
            SURVEY_POPUP_STYLESHEET
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            *SURVEY_POPUP_MARGINS
        )

        layout.setSpacing(
            SURVEY_POPUP_SPACING
        )

        title = QLabel(
            "Survey Analysis Report"
        )

        title.setObjectName(
            "reportTitle"
        )

        subtitle = QLabel(
            "RF occupancy, recommendation, "
            "and decision-score summary"
        )

        subtitle.setObjectName(
            "reportSubtitle"
        )

        self.text_box = QTextEdit()

        self.text_box.setAccessibleName(
            "Survey analysis report"
        )

        self.text_box.setReadOnly(
            True
        )

        self.text_box.setLineWrapMode(
            QTextEdit.LineWrapMode.WidgetWidth
        )

        self.text_box.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.text_box.setHtml(
            results_text
        )

        self.text_box.verticalScrollBar().setValue(
            0
        )

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        close_button = QPushButton(
            "Close"
        )

        close_button.setAccessibleName(
            "Close survey analysis report"
        )

        close_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        close_button.clicked.connect(
            self.close
        )

        button_layout.addWidget(
            close_button
        )

        layout.addWidget(
            title
        )

        layout.addWidget(
            subtitle
        )

        layout.addWidget(
            self.text_box,
            1
        )

        layout.addLayout(
            button_layout
        )
