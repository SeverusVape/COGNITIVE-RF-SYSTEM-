from html import escape
from enum import Enum

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


class SurveyStatusState(str, Enum):
    NO_SURVEY_DATA = "no_survey_data"
    RECOMMENDATION_AVAILABLE = "recommendation_available"
    ON_RECOMMENDED_CHANNEL = "on_recommended_channel"
    OFF_RECOMMENDED_CHANNEL = "off_recommended_channel"
    SURVEY_IN_PROGRESS = "survey_in_progress"
    AUTO_TUNE_COMPLETE = "auto_tune_complete"
    ALREADY_ON_RECOMMENDED_CHANNEL = (
        "already_on_recommended_channel"
    )
    AUTO_TUNE_UNAVAILABLE = "auto_tune_unavailable"
    AUTO_TUNE_FAILED = "auto_tune_failed"
    NOTICE = "notice"


STATUS_PRESENTATION = {
    SurveyStatusState.NO_SURVEY_DATA: (
        "NO SURVEY DATA",
        "neutral"
    ),
    SurveyStatusState.RECOMMENDATION_AVAILABLE: (
        "RECOMMENDATION AVAILABLE",
        "info"
    ),
    SurveyStatusState.ON_RECOMMENDED_CHANNEL: (
        "ON RECOMMENDED CHANNEL",
        "success"
    ),
    SurveyStatusState.OFF_RECOMMENDED_CHANNEL: (
        "OFF RECOMMENDED CHANNEL",
        "warning"
    ),
    SurveyStatusState.AUTO_TUNE_COMPLETE: (
        "AUTO-TUNE COMPLETE",
        "success"
    ),
    SurveyStatusState.ALREADY_ON_RECOMMENDED_CHANNEL: (
        "ALREADY ON RECOMMENDED CHANNEL",
        "success"
    ),
    SurveyStatusState.AUTO_TUNE_UNAVAILABLE: (
        "AUTO-TUNE UNAVAILABLE",
        "warning"
    ),
    SurveyStatusState.AUTO_TUNE_FAILED: (
        "AUTO-TUNE FAILED",
        "error"
    )
}


def _notice_color(
        tone
):
    if tone == "neutral":
        return TEXT_STRONG

    return NOTICE_COLORS.get(
        tone,
        TEXT_PRIMARY
    )


def _format_frequency(
        frequency
):
    if frequency is None:
        raise ValueError(
            "A frequency is required for this survey status."
        )

    return f"{float(frequency):.1f} MHz"


def _build_status_body(
        state,
        current_frequency,
        recommended_frequency,
        message
):
    if state == SurveyStatusState.NO_SURVEY_DATA:
        return (
            "Run a survey to generate a recommendation."
        )

    if state == SurveyStatusState.RECOMMENDATION_AVAILABLE:
        return (
            "Recommended: "
            f"{_format_frequency(recommended_frequency)}"
            "<br>Tune manually or use Auto-Tune."
        )

    if state == SurveyStatusState.ON_RECOMMENDED_CHANNEL:
        return (
            "Current center: "
            f"{_format_frequency(current_frequency)}"
        )

    if state == SurveyStatusState.OFF_RECOMMENDED_CHANNEL:
        return (
            "Current center: "
            f"{_format_frequency(current_frequency)}"
            "<br>Recommended: "
            f"{_format_frequency(recommended_frequency)}"
        )

    if state == SurveyStatusState.AUTO_TUNE_COMPLETE:
        return (
            "Receiver tuned to "
            f"{_format_frequency(current_frequency)}."
        )

    if (
            state
            == SurveyStatusState.ALREADY_ON_RECOMMENDED_CHANNEL
    ):
        return (
            "Receiver center is already "
            f"{_format_frequency(current_frequency)}."
        )

    if state == SurveyStatusState.AUTO_TUNE_UNAVAILABLE:
        return (
            escape(message)
            if message
            else "Complete a survey before using Auto-Tune."
        )

    if state == SurveyStatusState.AUTO_TUNE_FAILED:
        return (
            escape(message)
            if message
            else "Unable to tune the receiver."
        )

    if state == SurveyStatusState.NOTICE:
        return escape(message) if message else ""

    raise ValueError(
        f"Unsupported survey status state: {state}"
    )


def build_survey_status_html(
        state,
        current_frequency=None,
        recommended_frequency=None,
        message=None,
        title=None,
        tone=None
):
    state = SurveyStatusState(state)

    if state == SurveyStatusState.NOTICE:
        status_title = title or "SURVEY STATUS"
        status_tone = tone or "info"
    else:
        status_title, status_tone = (
            STATUS_PRESENTATION[state]
        )

    color = _notice_color(
        status_tone
    )
    body = _build_status_body(
        state,
        current_frequency,
        recommended_frequency,
        message
    )

    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY STATUS"
        "</div>"
        f"<div style='color:{color};"
        "font-size:14px;font-weight:700;"
        "margin-top:10px;'>"
        f"{escape(status_title)}"
        "</div>"
        f"<div style='color:{TEXT_PRIMARY};"
        "font-size:10px;margin-top:7px;'>"
        f"{body}"
        "</div>"
    )


def build_empty_survey_html():
    return build_survey_status_html(
        SurveyStatusState.NO_SURVEY_DATA
    )


def build_survey_notice_html(
        title,
        message,
        tone="info"
):
    return build_survey_status_html(
        SurveyStatusState.NOTICE,
        title=title,
        message=message,
        tone=tone
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
    show_survey_status(
        survey_label,
        SurveyStatusState.NO_SURVEY_DATA
    )


def show_survey_status(
        survey_label,
        state,
        **values
):
    state = SurveyStatusState(state)

    if state == SurveyStatusState.SURVEY_IN_PROGRESS:
        status_html = build_survey_progress_html(
            values["frequency"],
            values["current_point"],
            values["total_points"],
            values["progress_percent"]
        )
    else:
        status_html = build_survey_status_html(
            state,
            **values
        )

    survey_label.setHtml(
        status_html
    )


def show_survey_notice(
        survey_label,
        title,
        message,
        tone="info"
):
    show_survey_status(
        survey_label,
        SurveyStatusState.NOTICE,
        title=title,
        message=message,
        tone=tone
    )


def show_survey_progress(
        survey_label,
        frequency,
        current_point,
        total_points,
        progress_percent
):
    show_survey_status(
        survey_label,
        SurveyStatusState.SURVEY_IN_PROGRESS,
        frequency=frequency,
        current_point=current_point,
        total_points=total_points,
        progress_percent=progress_percent
    )
