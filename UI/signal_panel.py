from PyQt6.QtWidgets import QTextEdit
from SIGNALS.signal_history import (
    update_signal_history
)

def create_signal_panel():

    signals_label = QTextEdit()

    signals_label.setReadOnly(
        True
    )

    signals_label.setText(
        "Detected Signals\n\nNone"
    )

    signals_label.setFixedHeight(
        120
    )

    return signals_label


def update_signal_panel(
    signals_label,
    peaks,
    classify_signal
):

    signal_text = (
        "Detected Signals\n\n"
    )

    if len(peaks) == 0:

        signal_text += "None"

    else:

        for freq, power in peaks:

            history_count, age_seconds = (
                update_signal_history(
                    freq
                )
            )

            if age_seconds < 60:

                age_text = (
                    f"{age_seconds}s"
                )

            else:

                age_text = (
                    f"{age_seconds // 60}m"
                )

            classification = (
                classify_signal(
                    power,
                    freq,
                    history_count
                )
            )

            signal_text += (
                f"{freq:.2f} MHz  "
                f"{classification} "
                f"[{age_text}]\n"
            )

    signals_label.setText(
        signal_text
    )