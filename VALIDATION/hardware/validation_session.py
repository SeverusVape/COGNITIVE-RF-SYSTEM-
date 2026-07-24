"""Session lifecycle management for hardware validation evidence.

The session layer owns run identity, evidence-folder creation, and lightweight
runtime accounting. It does not write measurement records; that belongs to the
logging layer added in the next stage.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
import re
from uuid import uuid4

from VALIDATION.hardware.validation_models import (
    ValidationFrameRecord,
    ValidationSessionConfig,
    ValidationSessionSummary,
    ValidationSurveyRecord,
)


DEFAULT_RESULTS_ROOT = Path(
    "VALIDATION/hardware/results"
)

_SAFE_NAME_PATTERN = re.compile(
    r"[^A-Za-z0-9_.-]+"
)


def _format_timestamp(
        timestamp: datetime | None = None
):
    if timestamp is None:
        timestamp = datetime.now().astimezone()

    return timestamp.isoformat(
        timespec="seconds"
    )


def generate_validation_id(
        timestamp: datetime | None = None
):
    if timestamp is None:
        timestamp = datetime.now()

    return timestamp.strftime(
        "VAL-%Y%m%d-%H%M%S"
    )


def generate_session_id(
        timestamp: datetime | None = None,
        suffix: str | None = None
):
    if timestamp is None:
        timestamp = datetime.now()

    if suffix is None:
        suffix = uuid4().hex[:8]

    safe_suffix = _safe_name(
        suffix
    )

    return (
        timestamp.strftime(
            "SESSION-%Y%m%d-%H%M%S-"
        )
        + safe_suffix
    )


def _safe_name(value):
    safe_value = _SAFE_NAME_PATTERN.sub(
        "-",
        str(value).strip()
    ).strip("-")

    if not safe_value:
        return "validation-session"

    return safe_value


def _make_collision_safe_directory(path):
    candidate = path
    suffix = 2

    while candidate.exists():
        candidate = path.with_name(
            f"{path.name}_{suffix:02d}"
        )
        suffix += 1

    candidate.mkdir(
        parents=True,
        exist_ok=False
    )

    return candidate


class HardwareValidationSession:
    """Tracks one hardware-validation session."""

    def __init__(
            self,
            config: ValidationSessionConfig,
            results_root: str | Path = DEFAULT_RESULTS_ROOT,
            timestamp_provider=None
    ):
        self.config = config
        self.results_root = Path(
            results_root
        )
        self._timestamp_provider = (
            timestamp_provider
            or (lambda: datetime.now().astimezone())
        )
        self._active = False
        self._stopped = False
        self._session_directory = None
        self._start_time = None
        self._stop_time = None
        self._frame_count = 0
        self._survey_count = 0
        self._raw_candidate_total = 0
        self._confirmed_signal_total = 0
        self._detector_runtime_values = []
        self._occupancy_values = []
        self._confirmed_frequency_counter = Counter()
        self._smart_recommendation_counter = Counter()
        self._strongest_fft_bin_frequency_hz = None
        self._strongest_fft_bin_power_db = None
        self._survey_recommendations = []
        self._errors = []

    @property
    def active(self):
        return self._active

    @property
    def stopped(self):
        return self._stopped

    @property
    def session_directory(self):
        return self._session_directory

    @property
    def frame_count(self):
        return self._frame_count

    @property
    def survey_count(self):
        return self._survey_count

    def start(self):
        if self._active:
            raise RuntimeError(
                "Validation session is already active."
            )

        if self._stopped:
            raise RuntimeError(
                "Validation session cannot be restarted after stop."
            )

        folder_name = "_".join(
            [
                _safe_name(self.config.validation_id),
                _safe_name(self.config.session_id),
            ]
        )

        self._session_directory = _make_collision_safe_directory(
            self.results_root / folder_name
        )

        for child_name in (
                "frames",
                "surveys",
                "summaries",
                "artifacts"
        ):
            (
                self._session_directory
                / child_name
            ).mkdir()

        self._start_time = self._timestamp_provider()
        self._active = True

        return self._session_directory

    def stop(
            self,
            operator_metadata=None,
            limitations=None
    ):
        if not self._active:
            raise RuntimeError(
                "Validation session is not active."
            )

        self._stop_time = self._timestamp_provider()
        self._active = False
        self._stopped = True

        return self.build_summary(
            operator_metadata=operator_metadata,
            limitations=limitations
        )

    def add_error(self, message):
        self._errors.append(
            str(message)
        )

    def register_frame(
            self,
            record: ValidationFrameRecord
    ):
        self._require_active()
        self._validate_record_identity(
            record
        )

        self._frame_count += 1
        self._raw_candidate_total += record.raw_candidate_count
        self._confirmed_signal_total += record.confirmed_signal_count

        if record.detector_runtime_ms is not None:
            self._detector_runtime_values.append(
                record.detector_runtime_ms
            )

        if record.occupancy_percent is not None:
            self._occupancy_values.append(
                record.occupancy_percent
            )

        for frequency in record.confirmed_frequencies_hz:
            self._confirmed_frequency_counter[
                frequency
            ] += 1

        if record.smart_recommendation_hz is not None:
            self._smart_recommendation_counter[
                record.smart_recommendation_hz
            ] += 1

        if (
                record.strongest_fft_bin_power_db is not None
                and (
                    self._strongest_fft_bin_power_db is None
                    or (
                        record.strongest_fft_bin_power_db
                        > self._strongest_fft_bin_power_db
                    )
                )
        ):
            self._strongest_fft_bin_power_db = (
                record.strongest_fft_bin_power_db
            )
            self._strongest_fft_bin_frequency_hz = (
                record.strongest_fft_bin_frequency_hz
            )

    def register_survey(
            self,
            record: ValidationSurveyRecord
    ):
        self._require_active()
        self._validate_record_identity(
            record
        )

        self._survey_count += 1

        recommendation = (
            record.smart_recommendation_hz
            or record.best_frequency_hz
        )

        if recommendation is not None:
            self._survey_recommendations.append(
                recommendation
            )

    def build_summary(
            self,
            operator_metadata=None,
            limitations=None
    ):
        stop_time = (
            self._stop_time
            or self._timestamp_provider()
        )
        start_time = (
            self._start_time
            or stop_time
        )

        duration_seconds = max(
            0.0,
            (
                stop_time
                - start_time
            ).total_seconds()
        )

        return ValidationSessionSummary(
            validation_id=self.config.validation_id,
            session_id=self.config.session_id,
            session_name=self.config.session_name,
            start_timestamp=_format_timestamp(
                start_time
            ),
            stop_timestamp=_format_timestamp(
                stop_time
            ),
            duration_seconds=round(
                duration_seconds,
                3
            ),
            total_logged_frames=self._frame_count,
            total_surveys=self._survey_count,
            average_raw_candidate_count=self._average(
                self._raw_candidate_total,
                self._frame_count
            ),
            average_confirmed_signal_count=self._average(
                self._confirmed_signal_total,
                self._frame_count
            ),
            average_detector_runtime_ms=self._average_list(
                self._detector_runtime_values
            ),
            maximum_detector_runtime_ms=self._maximum(
                self._detector_runtime_values
            ),
            average_occupancy_percent=self._average_list(
                self._occupancy_values
            ),
            most_frequent_confirmed_frequencies_hz=(
                self._top_frequency_counts(
                    self._confirmed_frequency_counter
                )
            ),
            strongest_observed_fft_bin_frequency_hz=(
                self._strongest_fft_bin_frequency_hz
            ),
            strongest_observed_fft_bin_power_db=(
                self._strongest_fft_bin_power_db
            ),
            most_frequent_smart_recommendation_hz=(
                self._most_common_frequency(
                    self._smart_recommendation_counter
                )
            ),
            survey_recommendation_repeatability_percent=(
                self._survey_repeatability()
            ),
            errors_encountered=list(
                self._errors
            ),
            operator_metadata=operator_metadata or {},
            limitations=limitations or []
        )

    def _require_active(self):
        if not self._active:
            raise RuntimeError(
                "Validation session is not active."
            )

    def _validate_record_identity(self, record):
        if (
                record.validation_id != self.config.validation_id
                or record.session_id != self.config.session_id
        ):
            raise ValueError(
                "Record identity does not match validation session."
            )

    @staticmethod
    def _average(total, count):
        if count == 0:
            return None

        return round(
            total / count,
            3
        )

    @staticmethod
    def _average_list(values):
        if not values:
            return None

        return round(
            sum(values) / len(values),
            3
        )

    @staticmethod
    def _maximum(values):
        if not values:
            return None

        return max(values)

    @staticmethod
    def _top_frequency_counts(counter):
        return [
            {
                "frequency_hz": frequency,
                "count": count
            }
            for frequency, count in counter.most_common(
                5
            )
        ]

    @staticmethod
    def _most_common_frequency(counter):
        if not counter:
            return None

        return counter.most_common(
            1
        )[0][0]

    def _survey_repeatability(self):
        if not self._survey_recommendations:
            return None

        counts = Counter(
            self._survey_recommendations
        )
        most_common_count = counts.most_common(
            1
        )[0][1]

        return round(
            100.0
            * most_common_count
            / len(self._survey_recommendations),
            1
        )
