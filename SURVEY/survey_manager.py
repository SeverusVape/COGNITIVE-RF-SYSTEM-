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

    report = [
        """
        <div style="color:{{TEXT_PRIMARY}}; font-size:13px;">
        <table width="100%" cellspacing="10" cellpadding="10">
          <tr>
            <td width="32%" valign="top" bgcolor="{{CARD_SURFACE}}">
        <table width="100%" cellspacing="5" cellpadding="8">
          <tr>
            <td bgcolor="{{CARD_SURFACE}}">
              <b style="color:{{TEXT_MUTED}}; font-size:11px;">
                POINTS SCANNED
              </b><br>
              <span style="font-size:20px; font-weight:700;">
        """,
        str(points_scanned),
        """
              </span>
            </td>
            <td bgcolor="{{CARD_SURFACE}}">
              <b style="color:{{TEXT_MUTED}}; font-size:11px;">
                AVERAGE OCCUPANCY
              </b><br>
              <span style="font-size:20px; font-weight:700;">
        """,
        f"{average_occupancy:.1f}%",
        """
              </span>
            </td>
          </tr>
        </table>

        <h2 style="color:{{TEXT_STRONG}}; margin-top:8px;">
          Recommendation
        </h2>

        <table width="100%" cellspacing="0" cellpadding="9">
          <tr>
            <td bgcolor="{{RECOMMENDATION_SURFACE}}">
              <span style="color:{{ACCENT_LIGHT}}; font-size:11px;">
        """,
        escape(
            recommendation_title.upper()
        ),
        """
              </span><br>
              <span style="color:{{TEXT_STRONG}}; font-size:23px;
                           font-weight:700;">
        """,
        frequency_text,
        """
              </span>
            </td>
          </tr>
        </table>

        <table width="100%" cellspacing="5" cellpadding="6">
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
            </td>
            <td width="33%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    )

    if (
            runner_up_frequency is not None
            and runner_up_score is not None
            and score_margin is not None
    ):
        report.extend([
            """
            <p style="color:{{TEXT_STRONG}}; font-size:15px;
                      font-weight:700; margin-top:4px; margin-bottom:4px;">
              Decision Comparison
            </p>
            <table width="100%" cellspacing="0" cellpadding="5">
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

            <table width="100%" cellspacing="5" cellpadding="6">
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
              Confidence represents score separation, not statistical
              certainty.
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
            <h3 style="color:{{TEXT_STRONG}}; margin-top:14px;">
              Score Breakdown
            </h3>
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
            <p style="color:{{TEXT_STRONG}}; font-size:14px;
                      font-weight:700; margin-top:8px; margin-bottom:3px;">
              Decision Rationale
            </p>
            <ul style="margin-top:2px; margin-bottom:4px;">
            """
        )

        for reason in recommended_reason:
            report.extend([
                '<li style="margin-bottom:2px;">',
                escape(reason),
                "</li>"
            ])

        report.append("</ul>")

    report.append(
        """
            </td>
            <td width="35%" valign="top" bgcolor="{{CARD_SURFACE}}">
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

        diagnostic_maturity = (
            "Provisional"
            if diagnostic_observations < 5
            else "Established"
        )

        def percent_or_pending(value):
            return (
                "Collecting data"
                if value is None
                else f"{value * 100:.1f}%"
            )

        drift_text = (
            "Collecting data"
            if frequency_drift_khz is None
            else f"{frequency_drift_khz:.1f} kHz"
        )

        duty_cycle_text = (
            "N/A"
            if duty_cycle_percent is None
            else f"{duty_cycle_percent:.1f}%"
        )

        diagnostic_rows = (
            (
                "Bandwidth stability",
                percent_or_pending(
                    bandwidth_stability
                )
            ),
            (
                "Frequency stability",
                percent_or_pending(
                    frequency_stability
                )
            ),
            (
                "Frequency drift",
                drift_text
            ),
            (
                "Recent duty cycle",
                duty_cycle_text
            ),
            (
                "Diagnostic maturity",
                (
                    f"{diagnostic_maturity} "
                    f"({diagnostic_observations} observations)"
                )
            )
        )

        report.append(
            """
            <p style="color:{{TEXT_STRONG}}; font-size:14px;
                      font-weight:700; margin-top:6px; margin-bottom:3px;">
              Signal Diagnostics
            </p>
            <table width="100%" cellspacing="0" cellpadding="4">
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
            <p style="color:{{TEXT_SUBTLE}}; font-size:10px;">
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
                <p style="color:{{TEXT_STRONG}}; font-size:14px;
                          font-weight:700; margin-top:7px;
                          margin-bottom:3px;">
                  Observed Signal Behavior
                </p>
                <table width="100%" cellspacing="0" cellpadding="4">
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
                <p style="color:{{TEXT_SUBTLE}}; font-size:10px;">
                  Behavior summary only—not modulation or service identity.
                </p>
                """
            )

    report.append(
        """
            </td>
          </tr>
        </table>
        <table width="100%" cellspacing="10" cellpadding="10">
          <tr>
            <td width="36%" valign="top" bgcolor="{{CARD_SURFACE}}">
        """
    )

    report.append(
        """
        <p style="color:{{TEXT_STRONG}}; font-size:14px;
                  font-weight:700; margin-top:6px; margin-bottom:3px;">
          Measured Occupancy
        </p>
        <table width="100%" cellspacing="0" cellpadding="4">
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
            </td>
            <td width="64%" valign="top" bgcolor="{{CARD_SURFACE}}">
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
            <p style="color:{{TEXT_STRONG}}; font-size:14px;
                      font-weight:700; margin-top:6px; margin-bottom:3px;">
              Survey Diagnostic Coverage
            </p>
            <table width="100%" cellspacing="0" cellpadding="4">
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
                evidence = (
                    "Established"
                    if observation_count >= 5
                    else "Provisional"
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
                evidence = "No peak snapshot"
                frequency_behavior = "N/A"
                bandwidth_behavior = "N/A"
                activity_pattern = "N/A"

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
                escape(
                    f"{evidence} ({observation_count})"
                    if observation_count
                    else evidence
                ),
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
            <p style="color:{{TEXT_SUBTLE}}; font-size:10px;">
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
