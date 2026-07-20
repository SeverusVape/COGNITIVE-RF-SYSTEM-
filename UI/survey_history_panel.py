from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

from UI.theme import (
    STATUS_WARNING,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_STRONG,
    TEXT_SUBTLE
)


def _survey_word(
        survey_count
):
    if survey_count == 1:
        return "survey"

    return "surveys"


def build_survey_history_html(
        frequencies,
        average_occupancies,
        survey_count
):
    rows = []

    for rank, (
            frequency,
            occupancy
    ) in enumerate(
            zip(
                frequencies,
                average_occupancies
            ),
            start=1
    ):
        rows.append(
            "<tr>"
            f"<td style='color:{TEXT_SUBTLE};"
            "padding:3px 8px 3px 0;'>"
            f"{rank}</td>"
            f"<td style='color:{TEXT_PRIMARY};"
            "padding:3px 8px 3px 0;'>"
            f"{frequency:.1f} MHz</td>"
            f"<td align='right' "
            f"style='color:{STATUS_WARNING};"
            "font-weight:600;padding:3px 0;'>"
            f"{occupancy:.1f}%</td>"
            "</tr>"
        )

    history_context = (
        f"Average occupancy across {survey_count} "
        f"completed {_survey_word(survey_count)}"
    )

    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY HISTORY"
        "</div>"
        f"<div style='color:{TEXT_STRONG};"
        "font-size:13px;font-weight:700;"
        "margin-top:4px;'>"
        "Most occupied frequencies"
        "</div>"
        f"<div style='color:{TEXT_SUBTLE};"
        "font-size:10px;margin-top:2px;'>"
        f"{history_context}"
        "</div>"
        "<table width='100%' cellspacing='0' "
        "cellpadding='0' style='margin-top:8px;'>"
        + "".join(rows)
        + "</table>"
    )


def build_empty_survey_history_html():
    return (
        f"<div style='color:{TEXT_MUTED};"
        "font-size:10px;font-weight:600;'>"
        "SURVEY HISTORY"
        "</div>"
        f"<div style='color:{TEXT_STRONG};"
        "font-size:13px;font-weight:700;"
        "margin-top:4px;'>"
        "Most occupied frequencies"
        "</div>"
        f"<div style='color:{TEXT_SUBTLE};"
        "font-size:10px;margin-top:8px;'>"
        "Complete a survey to build history."
        "</div>"
    )


def create_survey_history_panel():
    history_label = QLabel()

    history_label.setObjectName(
        "surveyHistoryCard"
    )

    history_label.setTextFormat(
        Qt.TextFormat.RichText
    )

    history_label.setAlignment(
        Qt.AlignmentFlag.AlignTop
        | Qt.AlignmentFlag.AlignLeft
    )

    history_label.setWordWrap(
        True
    )

    history_label.setMinimumHeight(
        150
    )

    show_empty_survey_history(
        history_label
    )

    return history_label


def show_empty_survey_history(
        history_label
):
    history_label.setText(
        build_empty_survey_history_html()
    )


def update_survey_history(
        history_label,
        frequencies,
        average_occupancies,
        survey_count
):
    history_label.setText(
        build_survey_history_html(
            frequencies,
            average_occupancies,
            survey_count
        )
    )
