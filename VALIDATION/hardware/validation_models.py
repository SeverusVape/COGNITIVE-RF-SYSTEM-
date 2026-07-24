"""JSON-safe data contracts for automated hardware validation.

These records contain evidence only. They deliberately avoid Qt, NumPy, and
SDR objects so the logging layer can serialize them without application-level
knowledge.
"""

from dataclasses import asdict, dataclass, field
import json
import math
from typing import Any


def _validate_json_safe(
        value,
        path="record"
):
    if value is None or isinstance(
            value,
            (str, bool, int)
    ):
        return

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(
                f"{path} must not contain non-finite numbers."
            )
        return

    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_safe(
                item,
                f"{path}[{index}]"
            )
        return

    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"{path} must use string dictionary keys."
                )

            _validate_json_safe(
                item,
                f"{path}.{key}"
            )
        return

    raise TypeError(
        f"{path} contains a non-JSON-safe value "
        f"of type {type(value).__name__}."
    )


@dataclass
class _JsonSafeRecord:
    """Shared serialization behavior for validation records."""

    def __post_init__(self):
        _validate_json_safe(
            asdict(self)
        )

    def to_dict(self):
        payload = asdict(self)

        _validate_json_safe(
            payload
        )

        return payload

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            allow_nan=False,
            sort_keys=True
        )


@dataclass
class ValidationSessionConfig(_JsonSafeRecord):
    validation_id: str
    session_id: str
    configuration_id: str
    session_name: str
    test_band: str
    operator_notes: str
    antenna_description: str
    location_description: str
    expected_signal_description: str
    start_timestamp: str
    center_frequency_hz: float | None
    sample_rate_hz: float
    fft_size: int
    gain_mode: str
    gain_db: float | None
    detector_name: str
    detector_configuration: dict[str, Any] = field(
        default_factory=dict
    )
    confirmation_configuration: dict[str, Any] = field(
        default_factory=dict
    )
    update_interval_ms: int | None = None
    validation_log_interval_ms: int | None = None
    survey_defaults: dict[str, Any] = field(
        default_factory=dict
    )
    smart_mode_state: str = "unknown"
    software_version: str = "unknown"
    git_commit_sha: str = "unknown"


@dataclass
class ValidationFrameRecord(_JsonSafeRecord):
    validation_id: str
    session_id: str
    frame_index: int
    timestamp: str
    center_frequency_hz: float | None
    strongest_frequency_hz: float | None
    strongest_power_db: float | None
    average_power_db: float | None
    threshold_db: float | None
    occupancy_percent: float | None
    raw_candidate_count: int
    confirmed_signal_count: int
    detector_runtime_ms: float | None
    confirmed_frequencies_hz: list[float] = field(
        default_factory=list
    )
    candidate_frequencies_hz: list[float] = field(
        default_factory=list
    )
    smart_recommendation_hz: float | None = None
    application_mode: str = "monitoring"
    notes: str = ""


@dataclass
class ValidationSurveyRecord(_JsonSafeRecord):
    validation_id: str
    session_id: str
    survey_index: int
    timestamp: str
    start_frequency_hz: float | None
    stop_frequency_hz: float | None
    step_frequency_hz: float | None
    number_of_points: int
    ranked_results: list[dict[str, Any]] = field(
        default_factory=list
    )
    best_frequency_hz: float | None = None
    smart_recommendation_hz: float | None = None
    survey_runtime_seconds: float | None = None
    completion_status: str = "unknown"
    decision_mode: str = "unknown"
    recommended_occupancy_percent: float | None = None
    winner_score: float | None = None
    runner_up_frequency_hz: float | None = None
    runner_up_score: float | None = None
    score_margin: float | None = None
    decision_confidence: str = "N/A"
    notes: str = ""


@dataclass
class ValidationSessionSummary(_JsonSafeRecord):
    validation_id: str
    session_id: str
    session_name: str
    start_timestamp: str
    stop_timestamp: str
    duration_seconds: float
    total_logged_frames: int
    total_surveys: int
    average_raw_candidate_count: float | None
    average_confirmed_signal_count: float | None
    average_detector_runtime_ms: float | None
    maximum_detector_runtime_ms: float | None
    average_occupancy_percent: float | None
    most_frequent_confirmed_frequencies_hz: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )
    strongest_observed_frequency_hz: float | None = None
    strongest_observed_power_db: float | None = None
    most_frequent_smart_recommendation_hz: float | None = None
    survey_recommendation_repeatability_percent: float | None = None
    errors_encountered: list[str] = field(
        default_factory=list
    )
    operator_metadata: dict[str, Any] = field(
        default_factory=dict
    )
    limitations: list[str] = field(
        default_factory=list
    )
