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

            classification = (
                classify_signal(
                    power,
                    freq
                )
            )

            signal_text += (
                f"{freq:.2f} MHz  "
                f"{classification}\n"
            )

    signals_label.setText(
        signal_text
    )