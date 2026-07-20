from PyQt6.QtWidgets import QTextEdit


def create_status_panel():

    status_label = QTextEdit()

    status_label.setObjectName(
        "systemStatusCard"
    )

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


def update_status_panel(
    status_label,
    freq_input,
    sample_rate,
    freqs_mhz,
    peaks,
    threshold,
    meter,
    occupancy
):

    status_text = (
        "<b>Status</b><br><br>"
        "RTL-SDR Connected<br>"
        f"Center: {freq_input.text()} MHz<br>"
        f"Sample Rate: {sample_rate / 1e6:.3f} MSPS<br>"
        f"Range: {freqs_mhz[0]:.3f} - {freqs_mhz[-1]:.3f} MHz<br>"
        f"Signals Found: {len(peaks)}<br>"
        f"Median Threshold: {threshold:.1f} dB<br>"
        f"Occupancy: {meter}&nbsp;&nbsp;{occupancy:.0f}%<br>"
    )

    status_label.setHtml(
        status_text
    )
