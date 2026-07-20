from html import escape

from UI.theme import (
    apply_report_html_theme,
    confidence_color
)
from UI.survey_panel import (
    build_survey_progress_html,
    show_empty_survey
)
from UTILS.config import SMART_MAX_SCORE


# ==================================================
# SURVEY STATE
# ==================================================

survey_frequencies = []
survey_results = {}
survey_metrics = {}
current_survey_index = 0
occupancy_percent = 0
heatmap_history = []

best_frequency = None
best_occupancy = 0

def add_survey_result(
    survey_label,
    frequency,
    occupancy
):

    survey_results[
        round(frequency, 1)
    ] = round(occupancy)

    rows = []

    for freq in sorted(
            survey_results.keys()
    ):

        rows.append(
            f"{freq:.1f} MHz | "
            f"{survey_results[freq]}%"
        )

    survey_label.setHtml(
        "<b>MANUAL SURVEY POINTS</b><br><br>"
        + "<br>".join(rows)
    )


def clear_survey(
    survey_label
):

    survey_results.clear()

    show_empty_survey(
        survey_label
    )

# ==================================================
# SURVEY HELPERS
# ==================================================

def build_progress_bar(
        progress_percent
):

    bar_length = 20

    bars = int(
        progress_percent
        / 100
        * bar_length
    )

    progress_bar = (
        "▮" * bars +
        "▯" * (bar_length - bars)
    )

    return progress_bar

# ==================================================
# FREQUENCY GENERATION
# ==================================================

def generate_frequencies(
        start_mhz,
        stop_mhz,
        step_mhz
):

    frequencies = []

    frequency = start_mhz

    while frequency <= stop_mhz:
        frequencies.append(
            round(frequency, 6)
        )

        frequency = round(
            frequency + step_mhz,
            6
        )

    if (
            len(frequencies) > 0
            and frequencies[-1] != round(
                stop_mhz, 6
        )
    ):
        frequencies.append(
            round(
                stop_mhz,6
            )
        )

    return frequencies

# ==================================================
# RESULT RANKING
# ==================================================

def rank_frequencies(
        survey_results
):

    sorted_results = sorted(
        survey_results.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_results

# ==================================================
# RESULTS TEXT
# ==================================================

def build_results_html(

        sorted_results,
        points_scanned,
        average_occupancy,
        recommendation
):
    recommendation_title = recommendation[
        "title"
    ]

    recommended_frequency = recommendation[
        "frequency"
    ]

    recommended_occupancy = recommendation[
        "occupancy"
    ]

    recommended_score = recommendation[
        "score"
    ]

    score_details = recommendation.get(
        "score_details"
    )

    runner_up_frequency = recommendation.get(
        "runner_up_frequency"
    )

    runner_up_score = recommendation.get(
        "runner_up_score"
    )

    score_margin = recommendation.get(
        "score_margin"
    )

    decision_confidence = recommendation.get(
        "decision_confidence",
        "N/A"
    )

    recommended_reason = recommendation[
        "reason"
    ]

    confidence_text_color = confidence_color(
        decision_confidence
    )

    frequency_text = (
        "N/A"
        if recommended_frequency is None
        else f"{recommended_frequency:.3f} MHz"
    )

    occupancy_text = (
        "N/A"
        if recommended_occupancy is None
        else f"{recommended_occupancy:.1f}%"
    )

    report = [
        """
        <div style="color:{{TEXT_PRIMARY}}; font-size:13px;">
        <table width="100%" cellspacing="8" cellpadding="14">
          <tr>
            <td bgcolor="{{CARD_SURFACE}}">
              <span style="color:{{TEXT_MUTED}}; font-size:10px;">
                POINTS SCANNED
              </span><br>
              <span style="font-size:22px; font-weight:600;">
        """,
        str(points_scanned),
        """
              </span>
            </td>
            <td bgcolor="{{CARD_SURFACE}}">
              <span style="color:{{TEXT_MUTED}}; font-size:10px;">
                AVERAGE OCCUPANCY
              </span><br>
              <span style="font-size:22px; font-weight:600;">
        """,
        f"{average_occupancy:.1f}%",
        """
              </span>
            </td>
          </tr>
        </table>

        <h2 style="color:{{TEXT_STRONG}}; margin-top:18px;">
          Recommendation
        </h2>

        <table width="100%" cellspacing="0" cellpadding="16">
          <tr>
            <td bgcolor="{{RECOMMENDATION_SURFACE}}">
              <span style="color:{{ACCENT_LIGHT}}; font-size:11px;">
        """,
        escape(
            recommendation_title.upper()
        ),
        """
              </span><br><br>
              <span style="color:{{TEXT_STRONG}}; font-size:28px;
                           font-weight:700;">
        """,
        frequency_text,
        """
              </span>
            </td>
          </tr>
        </table>

        <table width="100%" cellspacing="8" cellpadding="10">
          <tr>
            <td bgcolor="{{CARD_SURFACE}}">
              <span style="color:{{TEXT_MUTED}};">Occupancy</span><br>
              <b>
        """,
        occupancy_text,
        """
              </b>
            </td>
        """
    ]

    if recommended_score is not None:
        report.extend([
            """
            <td bgcolor="{{CARD_SURFACE}}">
              <span style="color:{{TEXT_MUTED}};">Overall Score</span><br>
              <b>
            """,
            f"{recommended_score:.1f} / {SMART_MAX_SCORE}",
            """
              </b>
            </td>
            """
        ])

    report.append(
        """
          </tr>
        </table>
        """
    )

    if (
            runner_up_frequency is not None
            and runner_up_score is not None
            and score_margin is not None
    ):
        report.extend([
            """
            <h3 style="color:{{TEXT_STRONG}}; margin-top:16px;">
              Decision Comparison
            </h3>
            <table width="100%" cellspacing="0" cellpadding="8">
              <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
                <td><b>Candidate</b></td>
                <td><b>Frequency</b></td>
                <td align="right"><b>Score</b></td>
              </tr>
              <tr>
                <td>Recommended</td>
                <td>
            """,
            frequency_text,
            """
                </td>
                <td align="right">
            """,
            f"{recommended_score:.1f} / {SMART_MAX_SCORE}",
            """
                </td>
              </tr>
              <tr bgcolor="{{TABLE_ALTERNATE_SURFACE}}">
                <td>Runner-up</td>
                <td>
            """,
            f"{runner_up_frequency:.3f} MHz",
            """
                </td>
                <td align="right">
            """,
            f"{runner_up_score:.1f} / {SMART_MAX_SCORE}",
            """
                </td>
              </tr>
            </table>

            <table width="100%" cellspacing="8" cellpadding="10">
              <tr>
                <td bgcolor="{{CARD_SURFACE}}">
                  <span style="color:{{TEXT_MUTED}};">Decision Margin</span><br>
                  <b>
            """,
            f"{score_margin:.1f} points",
            """
                  </b>
                </td>
                <td bgcolor="{{CARD_SURFACE}}">
                  <span style="color:{{TEXT_MUTED}};">
                    Confidence (score separation)
                  </span><br>
                  <span style="font-weight:700; color:
            """,
            confidence_text_color,
            ';">',
            escape(
                decision_confidence
            ),
            """
                  </span>
                </td>
              </tr>
            </table>
            <p style="color:{{TEXT_SUBTLE}}; font-size:10px;">
              Confidence reflects winner/runner-up score separation,
              not statistical certainty.
            </p>
            """
        ])

    if score_details:
        score_rows = (
            (
                "Occupancy",
                score_details["occupancy_score"]
            ),
            (
                "Power",
                score_details["power_score"]
            ),
            (
                "Persistence",
                score_details["persistence_score"]
            ),
            (
                "Age",
                score_details["age_score"]
            ),
            (
                "Strength",
                score_details["strength_score"]
            )
        )

        report.append(
            """
            <h3 style="color:{{TEXT_STRONG}}; margin-top:16px;">
              Score Breakdown
            </h3>
            <table width="100%" cellspacing="0" cellpadding="7">
              <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
                <td><b>Component</b></td>
                <td align="right"><b>Score</b></td>
              </tr>
            """
        )

        for index, (
                label,
                value
        ) in enumerate(score_rows):
            row_color = (
                "{{TABLE_ALTERNATE_SURFACE}}"
                if index % 2
                else "{{REPORT_SURFACE}}"
            )

            report.extend([
                f'<tr bgcolor="{row_color}"><td>',
                escape(label),
                '</td><td align="right">',
                f"{value:.1f}",
                "</td></tr>"
            ])

        report.extend([
            """
            </table>
            <p style="color:{{TEXT_MUTED}};">
              Max power: <b style="color:{{TEXT_PRIMARY}};">
            """,
            f"{score_details['max_power']:.1f} dB",
            """
              </b>&nbsp;&nbsp;&nbsp; Average power:
              <b style="color:{{TEXT_PRIMARY}};">
            """,
            f"{score_details['average_power']:.1f} dB",
            "</b></p>"
        ])

    if recommended_reason:
        report.append(
            """
            <h3 style="color:{{TEXT_STRONG}}; margin-top:16px;">
              Decision Rationale
            </h3>
            <ul style="margin-top:4px;">
            """
        )

        for reason in recommended_reason:
            report.extend([
                '<li style="margin-bottom:4px;">',
                escape(reason),
                "</li>"
            ])

        report.append("</ul>")

    report.append(
        """
        <h3 style="color:{{TEXT_STRONG}}; margin-top:16px;">
          Measured Occupancy
        </h3>
        <table width="100%" cellspacing="0" cellpadding="7">
          <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
            <td><b>Rank</b></td>
            <td><b>Frequency</b></td>
            <td align="right"><b>Occupancy</b></td>
          </tr>
        """
    )

    for rank, (
            frequency,
            occupancy
    ) in enumerate(
        sorted_results[:5],
        start=1
    ):
        row_color = (
            "{{TABLE_ALTERNATE_SURFACE}}"
            if rank % 2 == 0
            else "{{REPORT_SURFACE}}"
        )

        report.extend([
            f'<tr bgcolor="{row_color}">',
            f"<td>{rank}</td>",
            f"<td>{frequency:.3f} MHz</td>",
            f'<td align="right">{occupancy:.1f}%</td>',
            "</tr>"
        ])

    report.append(
        """
        </table>
        </div>
        """
    )

    return apply_report_html_theme(
        "".join(report)
    )

# ==================================================
# STATUS TEXT
# ==================================================

def build_status_text(
        frequency,
        current_point,
        total_points,
        progress_percent
):

    survey_text = build_survey_progress_html(
        frequency,
        current_point,
        total_points,
        progress_percent
    )

    return survey_text
