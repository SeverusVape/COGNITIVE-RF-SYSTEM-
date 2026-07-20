from html import escape

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

    text = "Survey Results\n\n"

    for freq in sorted(
            survey_results.keys()
    ):

        text += (
            f"{freq:.1f} MHz | "
            f"{survey_results[freq]}%\n"
        )

    survey_label.setText(
        text
    )


def clear_survey(
    survey_label
):

    survey_results.clear()

    survey_label.setText(
        "\n"
        "No Survey Data Available\n\n"
        "Run a survey to generate\n"
        "occupancy statistics,\n"
        "recommendations, and\n"
        "heatmap history."
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

    confidence_color = {
        "HIGH": "#4ade80",
        "MODERATE": "#fbbf24",
        "LOW": "#fb7185",
        "N/A": "#9aa0a6"
    }.get(
        decision_confidence,
        "#9aa0a6"
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
        <div style="color:#e8eaed; font-size:13px;">
        <table width="100%" cellspacing="8" cellpadding="14">
          <tr>
            <td bgcolor="#1d2329">
              <span style="color:#9aa0a6; font-size:10px;">
                POINTS SCANNED
              </span><br>
              <span style="font-size:22px; font-weight:600;">
        """,
        str(points_scanned),
        """
              </span>
            </td>
            <td bgcolor="#1d2329">
              <span style="color:#9aa0a6; font-size:10px;">
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

        <h2 style="color:#ffffff; margin-top:18px;">
          Recommendation
        </h2>

        <table width="100%" cellspacing="0" cellpadding="16">
          <tr>
            <td bgcolor="#132631">
              <span style="color:#7dd3fc; font-size:11px;">
        """,
        escape(
            recommendation_title.upper()
        ),
        """
              </span><br><br>
              <span style="color:#ffffff; font-size:28px;
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
            <td bgcolor="#1d2329">
              <span style="color:#9aa0a6;">Occupancy</span><br>
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
            <td bgcolor="#1d2329">
              <span style="color:#9aa0a6;">Overall Score</span><br>
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
            <h3 style="color:#ffffff; margin-top:16px;">
              Decision Comparison
            </h3>
            <table width="100%" cellspacing="0" cellpadding="8">
              <tr bgcolor="#252a30">
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
              <tr bgcolor="#181b1f">
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
                <td bgcolor="#1d2329">
                  <span style="color:#9aa0a6;">Decision Margin</span><br>
                  <b>
            """,
            f"{score_margin:.1f} points",
            """
                  </b>
                </td>
                <td bgcolor="#1d2329">
                  <span style="color:#9aa0a6;">
                    Confidence (score separation)
                  </span><br>
                  <span style="font-weight:700; color:
            """,
            confidence_color,
            ';">',
            escape(
                decision_confidence
            ),
            """
                  </span>
                </td>
              </tr>
            </table>
            <p style="color:#7f8a93; font-size:10px;">
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
            <h3 style="color:#ffffff; margin-top:16px;">
              Score Breakdown
            </h3>
            <table width="100%" cellspacing="0" cellpadding="7">
              <tr bgcolor="#252a30">
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
                "#181b1f"
                if index % 2
                else "#111315"
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
            <p style="color:#9aa0a6;">
              Max power: <b style="color:#e8eaed;">
            """,
            f"{score_details['max_power']:.1f} dB",
            """
              </b>&nbsp;&nbsp;&nbsp; Average power:
              <b style="color:#e8eaed;">
            """,
            f"{score_details['average_power']:.1f} dB",
            "</b></p>"
        ])

    if recommended_reason:
        report.append(
            """
            <h3 style="color:#ffffff; margin-top:16px;">
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
        <h3 style="color:#ffffff; margin-top:16px;">
          Measured Occupancy
        </h3>
        <table width="100%" cellspacing="0" cellpadding="7">
          <tr bgcolor="#252a30">
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
            "#181b1f"
            if rank % 2 == 0
            else "#111315"
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

    return "".join(report)

# ==================================================
# STATUS TEXT
# ==================================================

def build_status_text(
        frequency,
        current_point,
        total_points,
        progress_percent,
        progress_bar
):

    survey_text = (
        "SURVEY STATUS\n\n"
        f"Frequency:\n"
        f"{frequency:.3f} MHz\n\n"
        f"Point:\n"
        f"{current_point}"
        f" / "
        f"{total_points}\n\n"
        f"Progress:\n"
        f"{progress_bar}\n"
        f"{progress_percent}%"
    )

    return survey_text
