from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit
)

from PyQt6.QtCore import Qt
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
            720,
            760
        )

        self.setMinimumSize(
            560,
            520
        )

        self.setStyleSheet(
            """
            QWidget {
                background-color: #202124;
                color: #e8eaed;
            }

            QLabel#reportTitle {
                color: #ffffff;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#reportSubtitle {
                color: #9aa0a6;
                font-size: 12px;
            }

            QTextEdit {
                background-color: #111315;
                color: #e8eaed;
                border: 1px solid #3c4043;
                border-radius: 8px;
                padding: 16px;
                selection-background-color: #1769aa;
            }

            QPushButton {
                min-width: 96px;
                min-height: 32px;
                padding: 4px 16px;
                color: #ffffff;
                background-color: #1769aa;
                border: 1px solid #2b7bbb;
                border-radius: 6px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1f7fc5;
            }

            QPushButton:pressed {
                background-color: #135887;
            }
            """
        )

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            20,
            18,
            20,
            18
        )

        layout.setSpacing(
            12
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
