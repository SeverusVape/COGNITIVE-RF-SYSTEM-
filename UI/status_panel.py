from html import escape

from PyQt6.QtWidgets import QTextEdit

from UI.theme import (
    ACCENT_LIGHT,
    STATUS_ERROR,
    STATUS_SUCCESS,
    STATUS_WARNING,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_STRONG,
    TEXT_SUBTLE
)


STATUS_TONE_COLORS = {
    "error": STATUS_ERROR,
    "success": STATUS_SUCCESS,
    "warning": STATUS_WARNING,
    "info": ACCENT_LIGHT
}


def build_status_message_html(
        title,
        message,
        tone="info"
):
    color = STATUS_TONE_COLORS.get(
        tone,
        TEXT_PRIMARY
    )

    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SYSTEM STATUS"
        "</div>"
        f"<div style='color:{color};"
        "font-size:14px;font-weight:700;"
        "margin-top:9px;'>"
        f"{escape(title)}"
        "</div>"
        f"<div style='color:{TEXT_PRIMARY};"
        "font-size:10px;margin-top:7px;'>"
        f"{escape(message)}"
        "</div>"
    )


def create_status_panel():
    status_label = QTextEdit()

    status_label.setObjectName(
        "systemStatusCard"
    )

    status_label.setAccessibleName(
        "RTL-SDR receiver status"
    )

    status_label.setReadOnly(
        True
    )

    show_status_message(
        status_label,
        "Starting receiver",
        "Waiting for RTL-SDR connection.",
        tone="info"
    )

    status_label.setFixedHeight(
        200
    )

    return status_label


def show_status_message(
        status_label,
        title,
        message,
        tone="info"
):
    status_label.setHtml(
        build_status_message_html(
            title,
            message,
            tone
        )
    )


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
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SYSTEM STATUS"
        "</div>"
        f"<div style='color:{STATUS_SUCCESS};"
        "font-size:13px;font-weight:700;"
        "margin-top:7px;'>"
        "RECEIVER CONNECTED"
        "</div>"
        "<table width='100%' cellspacing='0' "
        "cellpadding='0' style='margin-top:7px;'>"
        f"<tr><td style='color:{TEXT_SUBTLE};'>Center</td>"
        f"<td align='right' style='color:{TEXT_STRONG};'>"
        f"{escape(freq_input.text())} MHz</td></tr>"
        f"<tr><td style='color:{TEXT_SUBTLE};'>Sample rate</td>"
        f"<td align='right' style='color:{TEXT_PRIMARY};'>"
        f"{sample_rate / 1e6:.3f} MSPS</td></tr>"
        f"<tr><td style='color:{TEXT_SUBTLE};'>Range</td>"
        f"<td align='right' style='color:{TEXT_PRIMARY};'>"
        f"{freqs_mhz[0]:.3f} – {freqs_mhz[-1]:.3f} MHz"
        "</td></tr>"
        f"<tr><td style='color:{TEXT_SUBTLE};'>Signals</td>"
        f"<td align='right' style='color:{TEXT_PRIMARY};'>"
        f"{len(peaks)}</td></tr>"
        f"<tr><td style='color:{TEXT_SUBTLE};'>Threshold</td>"
        f"<td align='right' style='color:{TEXT_PRIMARY};'>"
        f"{threshold:.1f} dB</td></tr>"
        "</table>"
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;margin-top:7px;'>"
        "OCCUPANCY"
        "</div>"
        f"<div style='color:{ACCENT_LIGHT};"
        "font-size:10px;font-weight:600;"
        "margin-top:2px;'>"
        f"{meter}&nbsp;&nbsp;{occupancy:.0f}%"
        "</div>"
    )

    status_label.setHtml(
        status_text
    )
