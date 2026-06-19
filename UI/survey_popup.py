from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit
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
            500,
            600
        )

        layout = QVBoxLayout()

        text_box = QTextEdit()

        text_box.setReadOnly(
            True
        )

        text_box.setText(
            results_text
        )

        layout.addWidget(
            text_box
        )

        self.setLayout(
            layout
        )