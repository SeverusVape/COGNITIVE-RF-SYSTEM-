"""File logger for hardware-validation evidence.

This layer writes JSON/CSV evidence files inside a validation session folder.
It does not collect measurements from the production application; it only
persists records that are handed to it.
"""

from __future__ import annotations

from dataclasses import fields
import csv
import json
import logging
from pathlib import Path

from VALIDATION.hardware.validation_models import (
    ValidationFrameRecord,
    ValidationSessionConfig,
    ValidationSessionSummary,
    ValidationSurveyRecord,
)
from VALIDATION.hardware.validation_session import (
    HardwareValidationSession,
)
from VALIDATION.hardware.validation_summary import (
    build_summary_markdown,
)


CONFIG_JSON_FILENAME = "session_config.json"
CONFIG_CSV_FILENAME = "session_config.csv"
FRAME_CSV_FILENAME = "frame_records.csv"
FRAME_JSONL_FILENAME = "frame_records.jsonl"
SURVEY_CSV_FILENAME = "survey_records.csv"
SURVEY_JSONL_FILENAME = "survey_records.jsonl"
SUMMARY_JSON_FILENAME = "session_summary.json"
SUMMARY_CSV_FILENAME = "session_summary.csv"
SUMMARY_MARKDOWN_FILENAME = "summary.md"
VALIDATION_LOG_FILENAME = "validation.log"


def _field_names(record_type):
    return [
        field.name
        for field in fields(record_type)
    ]


def _csv_value(value):
    if value is None:
        return ""

    if isinstance(
            value,
            (dict, list)
    ):
        return json.dumps(
            value,
            sort_keys=True
        )

    return value


def _write_json(path, payload):
    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True
        )
        + "\n",
        encoding="utf-8"
    )


def _write_one_row_csv(path, fieldnames, payload):
    with path.open(
            "w",
            newline="",
            encoding="utf-8"
    ) as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerow(
            {
                key: _csv_value(
                    payload.get(
                        key
                    )
                )
                for key in fieldnames
            }
        )


def _append_jsonl(path, payload):
    with path.open(
            "a",
            encoding="utf-8"
    ) as file_handle:
        file_handle.write(
            json.dumps(
                payload,
                sort_keys=True
            )
            + "\n"
        )


class _CsvAppendWriter:
    def __init__(
            self,
            path: Path,
            fieldnames
    ):
        self.path = path
        self.fieldnames = list(
            fieldnames
        )

    def append(self, payload):
        write_header = not self.path.exists()

        with self.path.open(
                "a",
                newline="",
                encoding="utf-8"
        ) as file_handle:
            writer = csv.DictWriter(
                file_handle,
                fieldnames=self.fieldnames
            )

            if write_header:
                writer.writeheader()

            writer.writerow(
                {
                    key: _csv_value(
                        payload.get(
                            key
                        )
                    )
                    for key in self.fieldnames
                }
            )


class HardwareValidationLogger:
    """Persists records for one hardware-validation session."""

    def __init__(
            self,
            session: HardwareValidationSession,
            error_callback=None
    ):
        self.session = session
        self._error_callback = error_callback
        self._session_directory = None
        self._frame_csv_writer = None
        self._survey_csv_writer = None
        self._writes_disabled = False
        self._last_error = None
        self._event_logger = None
        self._event_handler = None

    @property
    def session_directory(self):
        return self._session_directory

    @property
    def active(self):
        return (
            self.session.active
            and not self._writes_disabled
        )

    @property
    def failed(self):
        return self._writes_disabled

    @property
    def last_error(self):
        return self._last_error

    def start(self):
        try:
            self._session_directory = self.session.start()
            self._start_event_log()
            self._write_event(
                logging.INFO,
                "Validation session started."
            )
            self._write_config(
                self.session.config
            )
            self._write_event(
                logging.INFO,
                "Configuration snapshot saved."
            )
            self._frame_csv_writer = _CsvAppendWriter(
                self._session_directory
                / "frames"
                / FRAME_CSV_FILENAME,
                _field_names(
                    ValidationFrameRecord
                )
            )
            self._survey_csv_writer = _CsvAppendWriter(
                self._session_directory
                / "surveys"
                / SURVEY_CSV_FILENAME,
                _field_names(
                    ValidationSurveyRecord
                )
            )
        except (
                OSError,
                TypeError,
                ValueError
        ) as error:
            self._record_write_error(
                "starting validation session",
                error
            )
            return None

        return self._session_directory

    def log_frame(
            self,
            record: ValidationFrameRecord
    ):
        self._require_started()

        try:
            payload = record.to_dict()

            self._frame_csv_writer.append(
                payload
            )
            _append_jsonl(
                self._session_directory
                / "frames"
                / FRAME_JSONL_FILENAME,
                payload
            )
            self.session.register_frame(
                record
            )
            if self.session.frame_count == 1:
                self._write_event(
                    logging.INFO,
                    "First validation frame recorded."
                )
        except (
                OSError,
                TypeError,
                ValueError
        ) as error:
            self._record_write_error(
                "writing frame evidence",
                error
            )
            return False

        return True

    def log_survey(
            self,
            record: ValidationSurveyRecord
    ):
        self._require_started()

        try:
            payload = record.to_dict()

            self._survey_csv_writer.append(
                payload
            )
            _append_jsonl(
                self._session_directory
                / "surveys"
                / SURVEY_JSONL_FILENAME,
                payload
            )
            self.session.register_survey(
                record
            )
            self._write_event(
                logging.INFO,
                "Survey record saved: "
                f"index={record.survey_index}, "
                f"status={record.completion_status}."
            )
        except (
                OSError,
                TypeError,
                ValueError
        ) as error:
            self._record_write_error(
                "writing survey evidence",
                error
            )
            return False

        return True

    def stop(
            self,
            operator_metadata=None,
            limitations=None
    ):
        self._require_started()

        try:
            self._write_event(
                logging.INFO,
                "Validation session stop requested."
            )
            summary = self.session.stop(
                operator_metadata=operator_metadata,
                limitations=limitations
            )
            self._write_summary(
                summary
            )
            self._write_event(
                logging.INFO,
                "Session summary generated."
            )
            self._write_event(
                logging.INFO,
                "Validation session stopped."
            )
        except (
                OSError,
                TypeError,
                ValueError
        ) as error:
            self._record_write_error(
                "writing session summary",
                error
            )
            return None
        finally:
            self._close_event_log()

        return summary

    def record_invalid_frame(
            self,
            message
    ):
        self._require_started()
        self.session.register_invalid_frame(
            message
        )
        self._write_event(
            logging.WARNING,
            str(message)
        )

    def record_shutdown(self):
        if not self.active:
            return

        self._write_event(
            logging.INFO,
            "Application shutdown requested while validation was active."
        )

    def _record_write_error(
            self,
            operation,
            error
    ):
        message = (
            f"Validation write error while {operation}: "
            f"{type(error).__name__}: {error}"
        )
        self._last_error = message
        self._writes_disabled = True
        self._write_event(
            logging.ERROR,
            message
        )

        if self.session.active:
            self.session.abort_due_to_error(
                message
            )
        else:
            self.session.add_error(
                message
            )

        if self._error_callback is not None:
            try:
                self._error_callback(
                    message
                )
            except Exception as callback_error:
                self.session.add_error(
                    "Validation error callback failed: "
                    f"{type(callback_error).__name__}: "
                    f"{callback_error}"
                )

        self._close_event_log()

    def _start_event_log(self):
        logger_name = (
            "SPECTRA.validation."
            + self.session.config.session_id
        )
        self._event_logger = logging.getLogger(
            logger_name
        )
        self._event_logger.setLevel(
            logging.INFO
        )
        self._event_logger.propagate = False

        for handler in list(
                self._event_logger.handlers
        ):
            handler.close()
            self._event_logger.removeHandler(
                handler
            )

        self._event_handler = logging.FileHandler(
            self._session_directory
            / VALIDATION_LOG_FILENAME,
            encoding="utf-8"
        )
        self._event_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )
        )
        self._event_logger.addHandler(
            self._event_handler
        )

    def _write_event(
            self,
            level,
            message
    ):
        if self._event_logger is None:
            return

        self._event_logger.log(
            level,
            str(message)
        )

    def _close_event_log(self):
        if self._event_handler is None:
            return

        try:
            self._event_handler.flush()
            self._event_handler.close()
        except OSError as error:
            self.session.add_error(
                "Validation event-log close error: "
                f"{type(error).__name__}: {error}"
            )
        finally:
            if self._event_logger is not None:
                self._event_logger.removeHandler(
                    self._event_handler
                )

            self._event_handler = None

    def _write_config(
            self,
            config: ValidationSessionConfig
    ):
        payload = config.to_dict()

        _write_json(
            self._session_directory
            / CONFIG_JSON_FILENAME,
            payload
        )
        _write_one_row_csv(
            self._session_directory
            / CONFIG_CSV_FILENAME,
            _field_names(
                ValidationSessionConfig
            ),
            payload
        )
    def _write_summary(
            self,
            summary: ValidationSessionSummary
    ):
        payload = summary.to_dict()

        _write_json(
            self._session_directory
            / "summaries"
            / SUMMARY_JSON_FILENAME,
            payload
        )
        _write_one_row_csv(
            self._session_directory
            / "summaries"
            / SUMMARY_CSV_FILENAME,
            _field_names(
                ValidationSessionSummary
            ),
            payload
        )
        (
            self._session_directory
            / "summaries"
            / SUMMARY_MARKDOWN_FILENAME
        ).write_text(
            build_summary_markdown(
                summary,
                self.session.config
            ),
            encoding="utf-8"
        )

    def _require_started(self):
        if self._session_directory is None:
            raise RuntimeError(
                "Validation logger has not been started."
            )

        if self._writes_disabled:
            raise RuntimeError(
                "Validation writes are disabled after a previous error."
            )
