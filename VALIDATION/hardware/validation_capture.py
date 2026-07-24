"""Production-facing helpers for hardware-validation records.

The helpers here transform already-computed application measurements into
validation records. They do not tune, detect, score, or modify application
behavior.
"""

from datetime import datetime

import numpy as np

from VALIDATION.hardware.validation_models import (
    ValidationFrameRecord,
    ValidationSessionConfig,
    ValidationSurveyRecord,
)
from VALIDATION.hardware.validation_session import (
    generate_session_id,
    generate_validation_id,
)


def current_timestamp():
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def frequency_list_hz(peaks):
    return [
        round(
            float(peak[0]) * 1e6,
            3
        )
        for peak in peaks
    ]


def normalize_decision_mode(
        decision_mode
):
    mode = str(
        decision_mode
        or "unknown"
    ).strip().upper()

    if mode in (
            "FREE",
            "FIND FREE CHANNEL"
    ):
        return "FREE"

    if mode in (
            "SMART",
            "SMART RECOMMENDATION"
    ):
        return "SMART"

    return mode


def normalize_completion_status(
        completion_status
):
    status = str(
        completion_status
        or "unknown"
    ).strip().lower()

    if status in (
            "success",
            "cancelled",
            "interrupted",
            "failed"
    ):
        return status

    return "unknown"


def _frequency_mhz_to_hz(
        frequency_mhz
):
    if frequency_mhz is None:
        return None

    return float(
        frequency_mhz
    ) * 1e6


def build_session_config(
        timestamp,
        configuration_id,
        session_name,
        test_band,
        operator_notes,
        antenna_description,
        location_description,
        expected_signal_description,
        center_frequency_hz,
        sample_rate_hz,
        fft_size,
        gain,
        detector_configuration,
        confirmation_configuration,
        validation_log_interval_ms,
        survey_defaults,
        software_version="SPECTRA validation capture",
        git_commit_sha="unknown"
):
    gain_mode = (
        "auto"
        if gain == "auto"
        else "manual"
    )

    gain_db = (
        None
        if gain == "auto"
        else float(gain)
    )

    return ValidationSessionConfig(
        validation_id=generate_validation_id(
            timestamp
        ),
        session_id=generate_session_id(
            timestamp
        ),
        configuration_id=configuration_id,
        session_name=session_name,
        test_band=test_band,
        operator_notes=operator_notes,
        antenna_description=antenna_description,
        location_description=location_description,
        expected_signal_description=(
            expected_signal_description
        ),
        start_timestamp=timestamp.isoformat(
            timespec="seconds"
        ),
        center_frequency_hz=center_frequency_hz,
        sample_rate_hz=sample_rate_hz,
        fft_size=fft_size,
        gain_mode=gain_mode,
        gain_db=gain_db,
        detector_name="adaptive local-threshold detector",
        detector_configuration=detector_configuration,
        confirmation_configuration=confirmation_configuration,
        validation_log_interval_ms=(
            validation_log_interval_ms
        ),
        survey_defaults=survey_defaults,
        smart_mode_state="available",
        software_version=software_version,
        git_commit_sha=git_commit_sha
    )


def build_frame_record(
        validation_id,
        session_id,
        frame_index,
        timestamp,
        center_frequency_hz,
        freqs_mhz,
        power_db,
        threshold_db,
        occupancy_percent,
        raw_peaks,
        confirmed_peaks,
        detector_runtime_ms,
        smart_recommendation_mhz=None,
        application_mode="monitoring"
):
    strongest_index = int(
        np.argmax(
            power_db
        )
    )

    return ValidationFrameRecord(
        validation_id=validation_id,
        session_id=session_id,
        frame_index=frame_index,
        timestamp=timestamp,
        center_frequency_hz=center_frequency_hz,
        strongest_fft_bin_frequency_hz=round(
            float(freqs_mhz[strongest_index]) * 1e6,
            3
        ),
        strongest_fft_bin_power_db=round(
            float(np.max(power_db)),
            3
        ),
        average_power_db=round(
            float(np.mean(power_db)),
            3
        ),
        threshold_db=round(
            float(threshold_db),
            3
        ),
        occupancy_percent=round(
            float(occupancy_percent),
            3
        ),
        raw_candidate_count=len(
            raw_peaks
        ),
        confirmed_signal_count=len(
            confirmed_peaks
        ),
        detector_runtime_ms=round(
            float(detector_runtime_ms),
            3
        ),
        confirmed_frequencies_hz=frequency_list_hz(
            confirmed_peaks
        ),
        candidate_frequencies_hz=frequency_list_hz(
            raw_peaks
        ),
        smart_recommendation_hz=(
            None
            if smart_recommendation_mhz is None
            else float(smart_recommendation_mhz) * 1e6
        ),
        application_mode=application_mode
    )


def build_survey_record(
        validation_id,
        session_id,
        survey_index,
        timestamp,
        survey_frequencies_mhz,
        sorted_results,
        points_scanned,
        recommendation,
        decision_mode,
        average_occupancy,
        completion_status="success",
        completion_reason="",
        error_message=""
):
    start_frequency_hz = None
    stop_frequency_hz = None
    step_frequency_hz = None

    if survey_frequencies_mhz:
        start_frequency_hz = (
            float(survey_frequencies_mhz[0])
            * 1e6
        )
        stop_frequency_hz = (
            float(survey_frequencies_mhz[-1])
            * 1e6
        )

    if len(survey_frequencies_mhz) >= 2:
        step_frequency_hz = (
            float(
                survey_frequencies_mhz[1]
                - survey_frequencies_mhz[0]
            )
            * 1e6
        )

    recommended_frequency = recommendation.get(
        "frequency"
    )
    runner_up_frequency = recommendation.get(
        "runner_up_frequency"
    )
    normalized_decision_mode = normalize_decision_mode(
        decision_mode
    )
    normalized_completion_status = (
        normalize_completion_status(
            completion_status
        )
    )
    best_frequency_hz = _frequency_mhz_to_hz(
        recommended_frequency
    )
    smart_recommendation_hz = (
        best_frequency_hz
        if normalized_decision_mode == "SMART"
        else None
    )

    ranked_results = [
        {
            "frequency_hz": round(
                float(frequency_mhz) * 1e6,
                3
            ),
            "occupancy_percent": float(occupancy)
        }
        for frequency_mhz, occupancy in sorted_results
    ]

    return ValidationSurveyRecord(
        validation_id=validation_id,
        session_id=session_id,
        survey_index=survey_index,
        timestamp=timestamp,
        start_frequency_hz=start_frequency_hz,
        stop_frequency_hz=stop_frequency_hz,
        step_frequency_hz=step_frequency_hz,
        number_of_points=points_scanned,
        ranked_results=ranked_results,
        best_frequency_hz=best_frequency_hz,
        smart_recommendation_hz=smart_recommendation_hz,
        completion_status=normalized_completion_status,
        completion_reason=str(
            completion_reason
            or ""
        ),
        error_message=str(
            error_message
            or ""
        ),
        decision_mode=normalized_decision_mode,
        recommended_occupancy_percent=recommendation.get(
            "occupancy"
        ),
        winner_score=recommendation.get(
            "score"
        ),
        runner_up_frequency_hz=(
            _frequency_mhz_to_hz(
                runner_up_frequency
            )
        ),
        runner_up_score=recommendation.get(
            "runner_up_score"
        ),
        score_margin=recommendation.get(
            "score_margin"
        ),
        decision_confidence=recommendation.get(
            "decision_confidence",
            "N/A"
        ),
        notes=(
            f"Average occupancy: {average_occupancy:.1f}%"
        )
    )
