from html import escape
from math import isfinite
from numbers import Integral, Real

from UI.theme import (
    apply_report_html_theme,
    confidence_color
)
from UI.survey_panel import (
    build_survey_progress_html,
    show_empty_survey
)
from UTILS.config import SMART_MAX_SCORE
from SIGNALS.behavior_profile import (
    build_behavior_profile
)


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
# DIAGNOSTIC STATUS
# ==================================================

def build_diagnostic_evidence_text(
        observation_count,
        include_observation_word=True
):
    if (
            isinstance(observation_count, bool)
            or not isinstance(observation_count, Integral)
            or observation_count < 0
    ):
        raise ValueError(
            "Observation count must be a non-negative integer."
        )

    if observation_count <= 0:
        return "No recent signal evidence"

    status = (
        "Established"
        if observation_count >= 5
        else "Provisional"
    )

    noun = (
        "observations"
        if observation_count != 1
        else "observation"
    )

    if include_observation_word:
        return (
            f"{status} "
            f"({observation_count} {noun})"
        )

    return f"{status} ({observation_count})"


def format_diagnostic_value(
        value,
        unit="",
        scale=1.0,
        missing_text="Collecting data"
):
    if value is None:
        return missing_text

    if (
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not isfinite(value)
    ):
        raise ValueError(
            "Diagnostic value must be a finite number or None."
        )

    return f"{value * scale:.1f}{unit}"

# ==================================================
# RESULTS TEXT
# ==================================================

def build_results_html(

        sorted_results,
        points_scanned,
        average_occupancy,
        recommendation,
        diagnostic_snapshot=None,
        diagnostic_snapshots=None
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

    score_text = (
        "N/A"
        if recommended_score is None
        else f"{recommended_score:.1f} / {SMART_MAX_SCORE}"
    )

    report = [
        """
        <div style="color:{{TEXT_PRIMARY}}; font-size:13px;">
        <table width="100%" cellspacing="6" cellpadding="6">
          <tr>
            <td width="46%" bgcolor="{{RECOMMENDATION_SURFACE}}">
              <span style="color:{{ACCENT_LIGHT}}; font-size:11px;
                           font-weight:700;">
        """,
        escape(
            recommendation_title.upper()
        ),
        """
              </span><br>
              <span style="color:{{TEXT_STRONG}}; font-size:27px;
                           font-weight:700;">
        """,
        frequency_text,
        """
              </span><br>
              <span style="color:{{TEXT_MUTED}}; font-size:10px;">
                Score:
              </span>
              <b style="color:{{TEXT_STRONG}}; font-size:12px;">
        """,
        score_text,
        """
              </b>
              <span style="color:{{TEXT_SUBTLE}};">
                &nbsp;&nbsp;·&nbsp;&nbsp;
              </span>
              <span style="color:{{TEXT_MUTED}}; font-size:10px;">
                Spectral-bin occupancy:
              </span>
              <b style="color:{{TEXT_STRONG}}; font-size:12px;">
        """,
        occupancy_text,
        """
              </b>
            </td>
            <td width="18%" bgcolor="{{CARD_SURFACE}}">
              <b style="color:{{TEXT_MUTED}}; font-size:11px;">
                POINTS SCANNED
              </b><br>
              <span style="font-size:17px; font-weight:700;">
        """,
        str(points_scanned),
        """
              </span>
            </td>
            <td width="36%" bgcolor="{{CARD_SURFACE}}">
              <b style="color:{{TEXT_MUTED}}; font-size:11px;">
                AVERAGE SPECTRAL-BIN OCCUPANCY
              </b><br>
              <span style="font-size:17px; font-weight:700;">
        """,
        f"{average_occupancy:.1f}%",
        """
              </span>
            </td>
          </tr>
        </table>

        <table width="100%" cellspacing="6" cellpadding="8">
          <tr>
            <td width="46%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    ]

    if (
            runner_up_frequency is not None
            and runner_up_score is not None
            and score_margin is not None
    ):
        report.extend([
            """
            <p style="color:{{STATUS_SUCCESS}}; font-size:15px;
                      font-weight:700; margin-top:4px; margin-bottom:4px;">
              DECISION COMPARISON
            </p>
            <table width="100%" cellspacing="0" cellpadding="6">
              <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
                <td><b>Candidate</b></td>
                <td><b>Frequency</b></td>
                <td align="right"><b>Score</b></td>
              </tr>
              <tr bgcolor="{{RECOMMENDATION_SURFACE}}">
                <td style="color:{{ACCENT_LIGHT}};"><b>★ Recommended</b></td>
                <td style="color:{{TEXT_STRONG}};"><b>
            """,
            frequency_text,
            """
                </b></td>
                <td align="right" style="color:{{TEXT_STRONG}};"><b>
            """,
            f"{recommended_score:.1f} / {SMART_MAX_SCORE}",
            """
                </b></td>
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

            <table width="100%" cellspacing="0" cellpadding="10"
                   style="margin-top:10px;">
              <tr>
                <td bgcolor="{{REPORT_SURFACE}}">
                  <span style="color:{{TEXT_MUTED}}; font-size:10px;
                               font-weight:700;">
                    DECISION SEPARATION
                  </span><br>
                  <b style="color:{{TEXT_STRONG}}; font-size:20px;">
            """,
            f"{score_margin:.1f} points",
            """
                  </b><br><br>
                  <span style="color:{{TEXT_MUTED}};">
                    Score Separation:
                  </span>
                  <span style="font-weight:700; color:
            """,
            confidence_text_color,
            ';">',
            escape(
                decision_confidence
            ),
            """
                  </span><br>
                  <span style="color:{{TEXT_SUBTLE}}; font-size:10px;">
                    Score separation is not statistical certainty.
                  </span>
                </td>
              </tr>
            </table>
            <p style="color:{{TEXT_SUBTLE}}; font-size:10px;">
              Separation category reflects only the winner/runner-up
              SMART score margin.
            </p>
            """
        ])

    if recommended_reason:
        report.append(
            """
            <p style="color:{{STATUS_SUCCESS}}; font-size:15px;
                      font-weight:700; margin-top:10px; margin-bottom:4px;">
              WHY SELECTED
            </p>
            <table width="100%" cellspacing="0" cellpadding="3">
            """
        )

        for reason in recommended_reason:
            display_reason = (
                "Highest SMART score"
                if reason == "Highest overall score"
                else reason
            )

            report.extend([
                "<tr><td width='18' valign='top' "
                "style='color:{{ACCENT_LIGHT}};font-weight:700;'>"
                "✓</td><td>",
                escape(display_reason),
                "</td></tr>"
            ])

        report.append("</table>")

    report.append(
        """
            </td>
            <td width="54%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    )

    if score_details:
        score_rows = (
            (
                "Spectral-bin Occupancy",
                score_details["occupancy_score"]
            ),
            (
                "Relative Power",
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
            <p style="color:{{STATUS_SUCCESS}}; font-size:15px;
                      font-weight:700; margin-top:4px; margin-bottom:4px;">
              SCORE BREAKDOWN
            </p>
            <table width="100%" cellspacing="0" cellpadding="4">
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
            if index in (0, 2):
                group_label = (
                    "PRIMARY SCORE COMPONENTS"
                    if index == 0
                    else "SIGNAL HISTORY FACTORS"
                )

                report.extend([
                    "<tr bgcolor='{{RECOMMENDATION_SURFACE}}'>"
                    "<td colspan='2' style='color:{{TEXT_MUTED}};"
                    "font-size:9px;font-weight:700;padding-top:4px;"
                    "padding-bottom:3px;'>",
                    group_label,
                    "</td></tr>"
                ])

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
            <p style="color:{{TEXT_MUTED}}; font-size:10px;">
              Max relative power: <b style="color:{{TEXT_PRIMARY}};">
            """,
            f"{score_details['max_power']:.1f} dB",
            """
              </b><br>Average relative power:
              <b style="color:{{TEXT_PRIMARY}};">
            """,
            f"{score_details['average_power']:.1f} dB",
            "</b></p>"
        ])

    report.append(
        """
            </td>
          </tr>
        </table>
        <table width="100%" cellspacing="6" cellpadding="7">
          <tr>
            <td width="58%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    )

    if diagnostic_snapshot:
        behavior_profile = build_behavior_profile(
            diagnostic_snapshot
        )
        bandwidth_stability = diagnostic_snapshot.get(
            "bandwidth_stability"
        )
        frequency_stability = diagnostic_snapshot.get(
            "frequency_stability"
        )
        frequency_drift_khz = diagnostic_snapshot.get(
            "frequency_drift_khz"
        )
        duty_cycle_percent = diagnostic_snapshot.get(
            "duty_cycle_percent"
        )
        bandwidth_observations = diagnostic_snapshot.get(
            "bandwidth_observations",
            0
        )
        frequency_observations = diagnostic_snapshot.get(
            "frequency_observations",
            0
        )

        diagnostic_observations = min(
            bandwidth_observations,
            frequency_observations
        )

        diagnostic_rows = (
            (
                "Bandwidth stability",
                format_diagnostic_value(
                    bandwidth_stability,
                    unit="%",
                    scale=100.0
                )
            ),
            (
                "Frequency stability",
                format_diagnostic_value(
                    frequency_stability,
                    unit="%",
                    scale=100.0
                )
            ),
            (
                "Frequency drift",
                format_diagnostic_value(
                    frequency_drift_khz,
                    unit=" kHz"
                )
            ),
            (
                "Recent duty cycle",
                format_diagnostic_value(
                    duty_cycle_percent,
                    unit="%",
                    missing_text="N/A"
                )
            ),
            (
                "Diagnostic maturity",
                build_diagnostic_evidence_text(
                    diagnostic_observations
                )
            )
        )

        report.append(
            """
            <p style="color:{{TEXT_MUTED}}; font-size:12px;
                      font-weight:700; margin-top:3px; margin-bottom:2px;">
              Signal Diagnostics
            </p>
            <table width="100%" cellspacing="0" cellpadding="3">
              <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
                <td><b>Measurement</b></td>
                <td align="right"><b>Observed value</b></td>
              </tr>
            """
        )

        for index, (label, value) in enumerate(
                diagnostic_rows
        ):
            row_color = (
                "{{TABLE_ALTERNATE_SURFACE}}"
                if index % 2
                else "{{REPORT_SURFACE}}"
            )

            report.extend([
                f'<tr bgcolor="{row_color}"><td>',
                escape(label),
                '</td><td align="right">',
                escape(value),
                "</td></tr>"
            ])

        report.append(
            """
            </table>
            <p style="color:{{TEXT_SUBTLE}}; font-size:9px;
                      margin-top:3px; margin-bottom:3px;">
              Diagnostic only · Provisional: 3–4 observations ·
              Established: 5+
            </p>
            """
        )

        if behavior_profile:
            behavior_rows = (
                (
                    "Frequency behavior",
                    behavior_profile[
                        "frequency_behavior"
                    ]
                ),
                (
                    "Bandwidth behavior",
                    behavior_profile[
                        "bandwidth_behavior"
                    ]
                ),
                (
                    "Activity pattern",
                    behavior_profile[
                        "activity_pattern"
                    ]
                )
            )

            report.append(
                """
                <p style="color:{{TEXT_MUTED}}; font-size:12px;
                          font-weight:700; margin-top:4px;
                          margin-bottom:2px;">
                  Observed Signal Behavior
                </p>
                <table width="100%" cellspacing="0" cellpadding="3">
                  <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
                    <td><b>Characteristic</b></td>
                    <td align="right"><b>Descriptor</b></td>
                  </tr>
                """
            )

            for index, (label, value) in enumerate(
                    behavior_rows
            ):
                row_color = (
                    "{{TABLE_ALTERNATE_SURFACE}}"
                    if index % 2
                    else "{{REPORT_SURFACE}}"
                )

                report.extend([
                    f'<tr bgcolor="{row_color}"><td>',
                    escape(label),
                    '</td><td align="right">',
                    escape(value),
                    "</td></tr>"
                ])

            report.append(
                """
                </table>
                <p style="color:{{TEXT_SUBTLE}}; font-size:9px;
                          margin-top:3px; margin-bottom:2px;">
                  Behavior summary only—not modulation or service identity.
                </p>
                """
            )

    report.append(
        """
            </td>
            <td width="42%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    )

    report.append(
        """
        <p style="color:{{TEXT_MUTED}}; font-size:12px;
                  font-weight:700; margin-top:3px; margin-bottom:2px;">
          Measured Spectral-Bin Occupancy
        </p>
        <table width="100%" cellspacing="0" cellpadding="3">
          <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
            <td><b>Rank</b></td>
            <td><b>Frequency</b></td>
            <td align="right"><b>Spectral-bin occupancy</b></td>
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
            </td>
          </tr>
        </table>
        <table width="100%" cellspacing="6" cellpadding="7">
          <tr>
            <td width="100%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    )

    if diagnostic_snapshots:
        ordered_frequencies = []

        if recommended_frequency in diagnostic_snapshots:
            ordered_frequencies.append(
                recommended_frequency
            )

        for frequency, _ in sorted_results:
            if frequency not in ordered_frequencies:
                ordered_frequencies.append(
                    frequency
                )

        report.append(
            """
            <p style="color:{{TEXT_MUTED}}; font-size:12px;
                      font-weight:700; margin-top:3px; margin-bottom:2px;">
              Survey Diagnostic Coverage
            </p>
            <table width="100%" cellspacing="0" cellpadding="3">
              <tr bgcolor="{{TABLE_HEADER_SURFACE}}">
                <td><b>Frequency</b></td>
                <td><b>Evidence</b></td>
                <td><b>Frequency</b></td>
                <td><b>Bandwidth</b></td>
                <td align="right"><b>Activity</b></td>
              </tr>
            """
        )

        for index, frequency in enumerate(
                ordered_frequencies[:5]
        ):
            snapshot = diagnostic_snapshots.get(
                frequency
            )

            if snapshot:
                profile = build_behavior_profile(
                    snapshot
                )
                observation_count = min(
                    snapshot.get(
                        "bandwidth_observations",
                        0
                    ),
                    snapshot.get(
                        "frequency_observations",
                        0
                    )
                )
                evidence = build_diagnostic_evidence_text(
                    observation_count,
                    include_observation_word=False
                )
                frequency_behavior = profile[
                    "frequency_behavior"
                ]
                bandwidth_behavior = profile[
                    "bandwidth_behavior"
                ]
                activity_pattern = profile[
                    "activity_pattern"
                ]
            else:
                observation_count = 0
                evidence = build_diagnostic_evidence_text(
                    observation_count,
                    include_observation_word=False
                )
                frequency_behavior = "Collecting data"
                bandwidth_behavior = "Collecting data"
                activity_pattern = "Collecting data"

            row_color = (
                "{{TABLE_ALTERNATE_SURFACE}}"
                if index % 2
                else "{{REPORT_SURFACE}}"
            )

            frequency_label = f"{frequency:.3f} MHz"

            if frequency == recommended_frequency:
                frequency_label += " (recommended)"

            report.extend([
                f'<tr bgcolor="{row_color}"><td>',
                escape(frequency_label),
                "</td><td>",
                escape(evidence),
                "</td><td>",
                escape(frequency_behavior),
                "</td><td>",
                escape(bandwidth_behavior),
                '</td><td align="right">',
                escape(activity_pattern),
                "</td></tr>"
            ])

        report.append(
            """
            </table>
            <p style="color:{{TEXT_SUBTLE}}; font-size:9px;
                      margin-top:3px; margin-bottom:2px;">
              Recommended first · Remaining rows in occupancy order ·
              Diagnostic only
            </p>
            """
        )

    report.append(
        """
            </td>
          </tr>
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
