"""Application-independent orchestration for hardware validation.

The controller owns validation session state and persistence timing. It accepts
measurements already computed by SPECTRA and does not tune hardware, detect
signals, rank survey results, or modify application behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from VALIDATION.hardware.validation_capture import (
    build_frame_record,
    build_session_config,
    build_survey_record,
)
from VALIDATION.hardware.validation_logger import (
    HardwareValidationLogger,
)
from VALIDATION.hardware.validation_environment import (
    get_git_commit_sha,
)
from VALIDATION.hardware.validation_session import (
    DEFAULT_RESULTS_ROOT,
    HardwareValidationSession,
)


@dataclass(frozen=True)
class HardwareValidationSettings:
    configuration_id: str
    session_name: str
    test_band: str
    operator_notes: str
    antenna_description: str
    location_description: str
    expected_signal_description: str
    sample_rate_hz: float
    fft_size: int
    gain: str | float
    detector_configuration: dict[str, Any] = field(
        default_factory=dict
    )
    confirmation_configuration: dict[str, Any] = field(
        default_factory=dict
    )
    logging_interval_ms: int = 1000
    survey_defaults: dict[str, Any] = field(
        default_factory=dict
    )
    detector_name: str = "adaptive local-threshold detector"
    update_interval_ms: int | None = None
    software_version: str = "SPECTRA validation capture"
    limitations: tuple[str, ...] = (
        "RTL-SDR measurements are relative, not calibrated dBm.",
        "Indoor antenna placement affects observed occupancy.",
        "Validation records reflect SPECTRA application behavior.",
    )


class HardwareValidationController:
    """Coordinates validation evidence without owning production processing."""

    def __init__(
            self,
            settings: HardwareValidationSettings,
            center_frequency_provider: Callable[[], float | None],
            survey_frequencies_provider: Callable[[], list[float]],
            decision_mode_provider: Callable[[], str] | None = None,
            status_callback=None,
            results_root: str | Path = DEFAULT_RESULTS_ROOT,
            datetime_provider=None,
            monotonic_provider=None,
            git_sha_provider=None
    ):
        self.settings = settings
        self._center_frequency_provider = center_frequency_provider
        self._survey_frequencies_provider = survey_frequencies_provider
        self._decision_mode_provider = (
            decision_mode_provider
            or (lambda: "unknown")
        )
        self._status_callback = status_callback
        self._results_root = Path(
            results_root
        )
        self._datetime_provider = (
            datetime_provider
            or (lambda: datetime.now().astimezone())
        )
        self._monotonic_provider = (
            monotonic_provider
            or perf_counter
        )
        self._git_sha_provider = (
            git_sha_provider
            or get_git_commit_sha
        )
        self._logger = None
        self._frame_index = 0
        self._survey_index = 0
        self._last_frame_time = None
        self._last_output_directory = None
        self._notify_status(
            "inactive",
            "Validation idle"
        )

    @property
    def active(self):
        return (
            self._logger is not None
            and self._logger.active
        )

    @property
    def frame_index(self):
        return self._frame_index

    @property
    def survey_index(self):
        return self._survey_index

    @property
    def session_directory(self):
        if self._logger is None:
            return self._last_output_directory

        return self._logger.session_directory

    @property
    def errors(self):
        if self._logger is None:
            return []

        return self._logger.session.errors

    def start(self):
        if self.active:
            return False

        self._frame_index = 0
        self._survey_index = 0
        self._last_frame_time = None

        try:
            timestamp = self._datetime_provider()
            config = build_session_config(
                timestamp=timestamp,
                configuration_id=self.settings.configuration_id,
                session_name=self.settings.session_name,
                test_band=self.settings.test_band,
                operator_notes=self.settings.operator_notes,
                antenna_description=(
                    self.settings.antenna_description
                ),
                location_description=(
                    self.settings.location_description
                ),
                expected_signal_description=(
                    self.settings.expected_signal_description
                ),
                center_frequency_hz=(
                    self._center_frequency_provider()
                ),
                sample_rate_hz=self.settings.sample_rate_hz,
                fft_size=self.settings.fft_size,
                gain=self.settings.gain,
                detector_configuration=(
                    self.settings.detector_configuration
                ),
                confirmation_configuration=(
                    self.settings.confirmation_configuration
                ),
                validation_log_interval_ms=(
                    self.settings.logging_interval_ms
                ),
                survey_defaults=self.settings.survey_defaults,
                detector_name=self.settings.detector_name,
                update_interval_ms=(
                    self.settings.update_interval_ms
                ),
                active_decision_mode=(
                    self._decision_mode_provider()
                ),
                software_version=self.settings.software_version,
                git_commit_sha=self._git_sha_provider()
            )
            session = HardwareValidationSession(
                config,
                results_root=self._results_root,
                timestamp_provider=self._datetime_provider
            )
            self._logger = HardwareValidationLogger(
                session,
                error_callback=self._handle_write_error
            )
            output_directory = self._logger.start()
        except Exception as error:
            self._notify_status(
                "error",
                "Validation setup error: "
                f"{type(error).__name__}: {error}"
            )
            return False

        if output_directory is None:
            return False

        self._last_output_directory = output_directory
        self._notify_status(
            "recording",
            "Validation logging active",
            output_directory
        )

        return True

    def stop(self):
        if not self.active:
            return False

        try:
            output_directory = self._logger.session_directory
            summary = self._logger.stop(
                limitations=list(
                    self.settings.limitations
                )
            )
        except Exception as error:
            self._handle_controller_error(
                "Validation stop error",
                error
            )
            return False

        if summary is None:
            return False

        self._last_output_directory = output_directory
        self._notify_status(
            "saved",
            "Validation log saved",
            output_directory
        )

        return True

    def shutdown(self):
        if self.active:
            return self.stop()

        return True

    def log_frame(
            self,
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
        if not self.active:
            return False

        now = self._monotonic_provider()
        minimum_interval_seconds = (
            self.settings.logging_interval_ms
            / 1000
        )

        if (
                self._last_frame_time is not None
                and (
                    now
                    - self._last_frame_time
                ) < minimum_interval_seconds
        ):
            return False

        next_frame_index = self._frame_index + 1

        try:
            frame_record = build_frame_record(
                validation_id=(
                    self._logger.session.config.validation_id
                ),
                session_id=(
                    self._logger.session.config.session_id
                ),
                frame_index=next_frame_index,
                timestamp=self._timestamp_text(),
                center_frequency_hz=(
                    self._center_frequency_provider()
                ),
                freqs_mhz=freqs_mhz,
                power_db=power_db,
                threshold_db=threshold_db,
                occupancy_percent=occupancy_percent,
                raw_peaks=raw_peaks,
                confirmed_peaks=confirmed_peaks,
                detector_runtime_ms=detector_runtime_ms,
                smart_recommendation_mhz=smart_recommendation_mhz,
                application_mode=application_mode
            )
        except Exception as error:
            self._handle_controller_error(
                "Validation frame capture error",
                error
            )
            return False

        self._last_frame_time = now

        if frame_record is None:
            self._logger.session.add_error(
                "Skipped invalid validation frame: FFT frequency and "
                "power arrays must be non-empty, length-matched, and "
                "contain at least one finite pair."
            )
            return False

        if not self._logger.log_frame(
                frame_record
        ):
            return False

        self._frame_index = next_frame_index

        return True

    def log_survey(
            self,
            recommendation,
            sorted_results,
            points_scanned,
            average_occupancy,
            decision_mode,
            completion_status="success",
            completion_reason="",
            error_message=""
    ):
        if not self.active:
            return False

        next_survey_index = self._survey_index + 1

        try:
            survey_record = build_survey_record(
                validation_id=(
                    self._logger.session.config.validation_id
                ),
                session_id=(
                    self._logger.session.config.session_id
                ),
                survey_index=next_survey_index,
                timestamp=self._timestamp_text(),
                survey_frequencies_mhz=list(
                    self._survey_frequencies_provider()
                ),
                sorted_results=sorted_results,
                points_scanned=points_scanned,
                recommendation=recommendation,
                decision_mode=decision_mode,
                average_occupancy=average_occupancy,
                completion_status=completion_status,
                completion_reason=completion_reason,
                error_message=error_message
            )
        except Exception as error:
            self._handle_controller_error(
                "Validation survey capture error",
                error
            )
            return False

        if not self._logger.log_survey(
                survey_record
        ):
            return False

        self._survey_index = next_survey_index

        return True

    def _timestamp_text(self):
        return self._datetime_provider().isoformat(
            timespec="seconds"
        )

    def _handle_write_error(self, message):
        self._notify_status(
            "error",
            message,
            self.session_directory
        )

    def _handle_controller_error(
            self,
            operation,
            error
    ):
        message = (
            f"{operation}: "
            f"{type(error).__name__}: {error}"
        )

        if self._logger is not None:
            self._logger.session.add_error(
                message
            )

        self._notify_status(
            "error",
            message,
            self.session_directory
        )

    def _notify_status(
            self,
            state,
            message,
            output_directory=None
    ):
        if self._status_callback is None:
            return

        self._status_callback(
            state,
            message,
            output_directory
        )
