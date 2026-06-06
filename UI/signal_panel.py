from PyQt6.QtWidgets import QTextEdit


def create_signal_panel():

    signals_label = QTextEdit()

    signals_label.setReadOnly(
        True
    )

    signals_label.setText(
        "Detected Signals\n\nNone"
    )

    signals_label.setFixedHeight(
        100
    )

    return signals_label