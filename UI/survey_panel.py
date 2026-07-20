from html import escape

from PyQt6.QtWidgets import (
    QPushButton,
    QTextEdit
)

from UI.theme import (
    ACCENT_LIGHT,
    CARD_SURFACE,
    STATUS_ERROR,
    STATUS_SUCCESS,
    STATUS_WARNING,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_STRONG,
    TEXT_SUBTLE
)


NOTICE_COLORS = {
    "error": STATUS_ERROR,
    "success": STATUS_SUCCESS,
    "warning": STATUS_WARNING,
    "info": ACCENT_LIGHT
}


def _notice_color(
        tone
):
    return NOTICE_COLORS.get(
        tone,
        TEXT_PRIMARY
    )


def build_empty_survey_html():
    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY STATUS"
        "</div>"
        f"<div style='color:{TEXT_STRONG};"
        "font-size:14px;font-weight:700;"
        "margin-top:10px;'>"
        "No survey data"
        "</div>"
        f"<div style='color:{TEXT_SUBTLE};"
        "font-size:10px;margin-top:6px;'>"
        "Run a survey to generate occupancy statistics, "
        "recommendations, and history."
        "</div>"
    )


def build_survey_notice_html(
        title,
        message,
        tone="info"
):
    color = _notice_color(
        tone
    )

    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY STATUS"
        "</div>"
        f"<div style='color:{color};"
        "font-size:14px;font-weight:700;"
        "margin-top:10px;'>"
        f"{escape(title)}"
        "</div>"
        f"<div style='color:{TEXT_PRIMARY};"
        "font-size:10px;margin-top:7px;'>"
        f"{escape(message)}"
        "</div>"
    )


def build_survey_progress_html(
        frequency,
        current_point,
        total_points,
        progress_percent
):
    progress = max(
        0,
        min(
            100,
            int(progress_percent)
        )
    )

    remaining = 100 - progress

    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY IN PROGRESS"
        "</div>"
        f"<div style='color:{ACCENT_LIGHT};"
        "font-size:18px;font-weight:700;"
        "margin-top:8px;'>"
        f"{frequency:.3f} MHz"
        "</div>"
        f"<table width='100%' cellspacing='0' "
        "cellpadding='0' style='margin-top:10px;'>"
        "<tr>"
        f"<td style='color:{TEXT_MUTED};font-size:10px;'>"
        "SCAN POINT</td>"
        f"<td align='right' style='color:{TEXT_PRIMARY};"
        "font-size:10px;font-weight:600;'>"
        f"{current_point} / {total_points}</td>"
        "</tr>"
        "</table>"
        "<table width='100%' cellspacing='0' cellpadding='0' "
        "style='margin-top:8px;'>"
        "<tr>"
        f"<td width='{progress}%' height='8' "
        f"bgcolor='{ACCENT_LIGHT}'></td>"
        f"<td width='{remaining}%' height='8' "
        f"bgcolor='{CARD_SURFACE}'></td>"
        "</tr>"
        "</table>"
        f"<div align='right' style='color:{TEXT_MUTED};"
        "font-size:10px;margin-top:4px;'>"
        f"{progress}%"
        "</div>"
    )


def build_survey_complete_html(
        recommended_frequency,
        points_scanned
):
    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY STATUS"
        "</div>"
        f"<div style='color:{STATUS_SUCCESS};"
        "font-size:14px;font-weight:700;"
        "margin-top:8px;'>"
        "SURVEY COMPLETE"
        "</div>"
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;margin-top:12px;'>"
        "RECOMMENDED FREQUENCY"
        "</div>"
        f"<div style='color:{TEXT_STRONG};"
        "font-size:20px;font-weight:700;"
        "margin-top:2px;'>"
        f"{recommended_frequency:.1f} MHz"
        "</div>"
        f"<div style='color:{TEXT_PRIMARY};"
        "font-size:10px;margin-top:10px;'>"
        f"{points_scanned} points scanned"
        "</div>"
    )


def create_survey_panel():
    survey_label = QTextEdit()

    survey_label.setObjectName(
        "surveyResultsCard"
    )

    survey_label.setAccessibleName(
        "Survey status and results"
    )

    survey_label.setReadOnly(
        True
    )

    show_empty_survey(
        survey_label
    )

    survey_label.setFixedHeight(
        280
    )

    return survey_label


def create_survey_results_button():
    results_button = QPushButton(
        "View detailed results"
    )

    results_button.setObjectName(
        "surveyResultsButton"
    )

    results_button.setAccessibleName(
        "Open detailed survey results"
    )

    results_button.setToolTip(
        "Open the complete survey analysis report."
    )

    results_button.setVisible(
        False
    )

    return results_button


def show_empty_survey(
        survey_label
):
    survey_label.setHtml(
        build_empty_survey_html()
    )


def show_survey_notice(
        survey_label,
        title,
        message,
        tone="info"
):
    survey_label.setHtml(
        build_survey_notice_html(
            title,
            message,
            tone
        )
    )


def show_survey_progress(
        survey_label,
        frequency,
        current_point,
        total_points,
        progress_percent
):
    survey_label.setHtml(
        build_survey_progress_html(
            frequency,
            current_point,
            total_points,
            progress_percent
        )
    )


def show_survey_complete(
        survey_label,
        recommended_frequency,
        points_scanned
):
    survey_label.setHtml(
        build_survey_complete_html(
            recommended_frequency,
            points_scanned
        )
    )
