from PyQt6.QtWidgets import QTextEdit


def create_status_panel():

    status_label = QTextEdit()

    status_label.setReadOnly(
        True
    )

    status_label.setText(
        "Status\n\nStarting..."
    )

    status_label.setFixedHeight(
        200
    )

    return status_label