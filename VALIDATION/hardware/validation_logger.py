"""File logger for hardware-validation evidence.

This layer writes JSON/CSV evidence files inside a validation session folder.
It does not collect measurements from the production application; it only
persists records that are handed to it.
"""

from __future__ import annotations

from dataclasses import fields
import csv
import json
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


CONFIG_JSON_FILENAME = "session_config.json"
CONFIG_CSV_FILENAME = "session_config.csv"
FRAME_CSV_FILENAME = "frame_records.csv"
FRAME_JSONL_FILENAME = "frame_records.jsonl"
SURVEY_CSV_FILENAME = "survey_records.csv"
SURVEY_JSONL_FILENAME = "survey_records.jsonl"
SUMMARY_JSON_FILENAME = "session_summary.json"
SUMMARY_CSV_FILENAME = "session_summary.csv"


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
            session: HardwareValidationSession
    ):
        self.session = session
        self._session_directory = None
        self._frame_csv_writer = None
        self._survey_csv_writer = None

    @property
    def session_directory(self):
        return self._session_directory

    @property
    def active(self):
        return self.session.active

    def start(self):
        self._session_directory = self.session.start()
        self._write_config(
            self.session.config
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

        return self._session_directory

    def log_frame(
            self,
            record: ValidationFrameRecord
    ):
        self._require_started()

        self.session.register_frame(
            record
        )
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

    def log_survey(
            self,
            record: ValidationSurveyRecord
    ):
        self._require_started()

        self.session.register_survey(
            record
        )
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

    def stop(
            self,
            operator_metadata=None,
            limitations=None
    ):
        self._require_started()

        summary = self.session.stop(
            operator_metadata=operator_metadata,
            limitations=limitations
        )
        self._write_summary(
            summary
        )

        return summary

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

    def _require_started(self):
        if self._session_directory is None:
            raise RuntimeError(
                "Validation logger has not been started."
            )
