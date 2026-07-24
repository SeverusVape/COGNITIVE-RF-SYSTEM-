"""Reviewer-readable hardware-validation session summaries."""

from VALIDATION.hardware.validation_models import (
    ValidationSessionConfig,
    ValidationSessionSummary,
)


def _display(value, suffix=""):
    if value is None:
        return "Not observed"

    return f"{value}{suffix}"


def _frequency_mhz(frequency_hz):
    if frequency_hz is None:
        return "Not observed"

    return f"{frequency_hz / 1e6:.6f} MHz"


def build_summary_markdown(
        summary: ValidationSessionSummary,
        config: ValidationSessionConfig
):
    """Render a neutral engineering summary from captured evidence."""
    completion_rows = (
        [
            f"| {status} | {count} |"
            for status, count
            in sorted(
                summary.survey_completion_state_counts.items()
            )
        ]
        or [
            "| None recorded | 0 |"
        ]
    )
    frequency_rows = (
        [
            "| "
            f"{_frequency_mhz(item['frequency_hz'])} | "
            f"{item['count']} |"
            for item
            in summary.most_frequent_confirmed_frequencies_hz
        ]
        or [
            "| None observed | 0 |"
        ]
    )
    warnings = (
        [
            f"- {message}"
            for message in summary.warnings_encountered
        ]
        or [
            "- None recorded."
        ]
    )
    errors = (
        [
            f"- {message}"
            for message in summary.errors_encountered
        ]
        or [
            "- None recorded."
        ]
    )
    limitations = (
        [
            f"- {message}"
            for message in summary.limitations
        ]
        or [
            "- No limitations were supplied."
        ]
    )

    lines = [
        "# SPECTRA Hardware Validation Session Summary",
        "",
        "This report summarizes observed SPECTRA behavior. It does not "
        "establish RF ground truth, calibrated power, probability of "
        "detection, or classical false-alarm probability.",
        "",
        "## Session Identity",
        "",
        f"- Validation ID: `{summary.validation_id}`",
        f"- Session ID: `{summary.session_id}`",
        f"- Session name: {summary.session_name}",
        f"- Test band: {config.test_band}",
        f"- Configuration ID: `{summary.configuration_id}`",
        f"- Git commit: `{summary.git_commit_sha}`",
        f"- Start: {summary.start_timestamp}",
        f"- Stop: {summary.stop_timestamp}",
        f"- Duration: {summary.duration_seconds:.3f} s",
        "",
        "## Evidence Totals",
        "",
        f"- Logged frames: {summary.total_logged_frames}",
        f"- Valid frames: {summary.valid_frame_count}",
        f"- Skipped or invalid frames: "
        f"{summary.skipped_invalid_frame_count}",
        f"- Survey records: {summary.total_surveys}",
        "",
        "## Observed Frame Metrics",
        "",
        "| Metric | Observed value |",
        "|---|---:|",
        "| Average raw candidates per frame | "
        f"{_display(summary.average_raw_candidate_count)} |",
        "| Average confirmed signals per frame | "
        f"{_display(summary.average_confirmed_signal_count)} |",
        "| Average detector runtime | "
        f"{_display(summary.average_detector_runtime_ms, ' ms')} |",
        "| Maximum detector runtime | "
        f"{_display(summary.maximum_detector_runtime_ms, ' ms')} |",
        "| Average spectral-bin occupancy | "
        f"{_display(summary.average_occupancy_percent, '%')} |",
        "",
        "## Survey Completion States",
        "",
        "| State | Count |",
        "|---|---:|",
        *completion_rows,
        "",
        "## Recommendation Observations",
        "",
        "- Most frequent SMART recommendation: "
        f"{_frequency_mhz(summary.most_frequent_smart_recommendation_hz)}",
        "- Survey recommendation repeatability: "
        f"{_display(summary.survey_recommendation_repeatability_percent, '%')}",
        "",
        "Repeatability is the fraction of recorded survey recommendations "
        "matching the most common recommendation. It is not a probability "
        "of correct selection.",
        "",
        "## Confirmed-Frequency Observations",
        "",
        "| Frequency | Frame observations |",
        "|---|---:|",
        *frequency_rows,
        "",
        "## Strongest Observed FFT Bin",
        "",
        "- Frequency: "
        f"{_frequency_mhz(summary.strongest_observed_fft_bin_frequency_hz)}",
        "- Relative FFT power: "
        f"{_display(summary.strongest_observed_fft_bin_power_db, ' dB')}",
        "",
        "The strongest FFT bin is a spectral maximum, not necessarily a "
        "confirmed or identified signal.",
        "",
        "## Operator Metadata",
        "",
        f"- Notes: {config.operator_notes or 'unspecified'}",
        f"- Antenna: {config.antenna_description or 'unspecified'}",
        f"- Location: {config.location_description or 'unspecified'}",
        "- Expected signal description: "
        f"{config.expected_signal_description or 'unspecified'}",
        "",
        "## Warnings",
        "",
        *warnings,
        "",
        "## Errors",
        "",
        *errors,
        "",
        "## Limitations",
        "",
        *limitations,
        "",
    ]

    return "\n".join(
        lines
    )
