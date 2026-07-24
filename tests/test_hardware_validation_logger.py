from datetime import datetime, timedelta, timezone
import csv
import json
import tempfile
import unittest

from VALIDATION.hardware.validation_logger import (
    CONFIG_CSV_FILENAME,
    CONFIG_JSON_FILENAME,
    FRAME_CSV_FILENAME,
    FRAME_JSONL_FILENAME,
    HardwareValidationLogger,
    SUMMARY_CSV_FILENAME,
    SUMMARY_JSON_FILENAME,
    SURVEY_CSV_FILENAME,
    SURVEY_JSONL_FILENAME,
)
from VALIDATION.hardware.validation_models import (
    ValidationFrameRecord,
    ValidationSessionConfig,
    ValidationSurveyRecord,
)
from VALIDATION.hardware.validation_session import (
    HardwareValidationSession,
)


class HardwareValidationLoggerTests(unittest.TestCase):

    @staticmethod
    def _config():
        return ValidationSessionConfig(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-20260724-143000-test",
            configuration_id="CFG-HW-01",
            session_name="Brooklyn FM survey",
            test_band="88-92 MHz",
            operator_notes="Indoor validation",
            antenna_description="RTL-SDR dipole",
            location_description="Fourth-floor window",
            expected_signal_description="Local FM broadcast carriers",
            start_timestamp="2026-07-24T14:30:00-04:00",
            center_frequency_hz=90e6,
            sample_rate_hz=2.048e6,
            fft_size=8192,
            gain_mode="manual",
            gain_db=20.0,
            detector_name="adaptive",
            detector_configuration={
                "threshold_margin_db": 10.0
            }
        )

    @staticmethod
    def _frame(frame_index=1):
        return ValidationFrameRecord(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-20260724-143000-test",
            frame_index=frame_index,
            timestamp="2026-07-24T14:30:01-04:00",
            center_frequency_hz=90e6,
            strongest_frequency_hz=90.1e6,
            strongest_power_db=42.0,
            average_power_db=21.0,
            threshold_db=31.0,
            occupancy_percent=8.0,
            raw_candidate_count=2,
            confirmed_signal_count=1,
            detector_runtime_ms=1.5,
            confirmed_frequencies_hz=[
                90.1e6
            ],
            candidate_frequencies_hz=[
                90.1e6,
                90.4e6
            ],
            smart_recommendation_hz=89e6,
            application_mode="survey"
        )

    @staticmethod
    def _survey():
        return ValidationSurveyRecord(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-20260724-143000-test",
            survey_index=1,
            timestamp="2026-07-24T14:31:00-04:00",
            start_frequency_hz=88e6,
            stop_frequency_hz=92e6,
            step_frequency_hz=1e6,
            number_of_points=5,
            ranked_results=[
                {
                    "frequency_hz": 90e6,
                    "occupancy_percent": 8.0
                }
            ],
            best_frequency_hz=90e6,
            smart_recommendation_hz=90e6,
            completion_status="success",
            winner_score=69.0,
            runner_up_frequency_hz=88e6,
            runner_up_score=63.9,
            score_margin=5.1,
            decision_confidence="MODERATE"
        )

    def _logger(self, temp_dir):
        start = datetime(
            2026,
            7,
            24,
            18,
            0,
            tzinfo=timezone.utc
        )
        timestamps = iter(
            [
                start,
                start + timedelta(seconds=10)
            ]
        )
        session = HardwareValidationSession(
            self._config(),
            results_root=temp_dir,
            timestamp_provider=lambda: next(timestamps)
        )

        return HardwareValidationLogger(
            session
        )

    def test_start_writes_configuration_json_and_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = self._logger(
                temp_dir
            )
            session_path = logger.start()

            config_json_path = (
                session_path
                / CONFIG_JSON_FILENAME
            )
            config_csv_path = (
                session_path
                / CONFIG_CSV_FILENAME
            )

            self.assertTrue(
                config_json_path.exists()
            )
            self.assertTrue(
                config_csv_path.exists()
            )

            payload = json.loads(
                config_json_path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                payload["configuration_id"],
                "CFG-HW-01"
            )

            with config_csv_path.open(
                    newline="",
                    encoding="utf-8"
            ) as file_handle:
                rows = list(
                    csv.DictReader(
                        file_handle
                    )
                )

            self.assertEqual(
                rows[0]["session_name"],
                "Brooklyn FM survey"
            )
            self.assertIn(
                "threshold_margin_db",
                rows[0]["detector_configuration"]
            )

    def test_log_frame_writes_csv_and_jsonl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = self._logger(
                temp_dir
            )
            session_path = logger.start()
            logger.log_frame(
                self._frame(frame_index=1)
            )
            logger.log_frame(
                self._frame(frame_index=2)
            )

            frame_csv_path = (
                session_path
                / "frames"
                / FRAME_CSV_FILENAME
            )
            frame_jsonl_path = (
                session_path
                / "frames"
                / FRAME_JSONL_FILENAME
            )

            with frame_csv_path.open(
                    newline="",
                    encoding="utf-8"
            ) as file_handle:
                rows = list(
                    csv.DictReader(
                        file_handle
                    )
                )

            self.assertEqual(
                len(rows),
                2
            )
            self.assertEqual(
                rows[0]["frame_index"],
                "1"
            )
            self.assertIn(
                "90100000.0",
                rows[0]["confirmed_frequencies_hz"]
            )

            json_lines = frame_jsonl_path.read_text(
                encoding="utf-8"
            ).splitlines()

            self.assertEqual(
                len(json_lines),
                2
            )
            self.assertEqual(
                json.loads(
                    json_lines[1]
                )["frame_index"],
                2
            )

    def test_log_survey_writes_csv_and_jsonl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = self._logger(
                temp_dir
            )
            session_path = logger.start()
            logger.log_survey(
                self._survey()
            )

            survey_csv_path = (
                session_path
                / "surveys"
                / SURVEY_CSV_FILENAME
            )
            survey_jsonl_path = (
                session_path
                / "surveys"
                / SURVEY_JSONL_FILENAME
            )

            with survey_csv_path.open(
                    newline="",
                    encoding="utf-8"
            ) as file_handle:
                rows = list(
                    csv.DictReader(
                        file_handle
                    )
                )

            self.assertEqual(
                rows[0]["decision_confidence"],
                "MODERATE"
            )
            self.assertIn(
                "occupancy_percent",
                rows[0]["ranked_results"]
            )

            payload = json.loads(
                survey_jsonl_path.read_text(
                    encoding="utf-8"
                ).strip()
            )

            self.assertEqual(
                payload["smart_recommendation_hz"],
                90e6
            )

    def test_stop_writes_summary_json_and_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = self._logger(
                temp_dir
            )
            session_path = logger.start()
            logger.log_frame(
                self._frame()
            )
            logger.log_survey(
                self._survey()
            )
            summary = logger.stop(
                operator_metadata={
                    "operator": "Sergei"
                },
                limitations=[
                    "Indoor receiver validation"
                ]
            )

            summary_json_path = (
                session_path
                / "summaries"
                / SUMMARY_JSON_FILENAME
            )
            summary_csv_path = (
                session_path
                / "summaries"
                / SUMMARY_CSV_FILENAME
            )

            self.assertEqual(
                summary.total_logged_frames,
                1
            )
            self.assertTrue(
                summary_json_path.exists()
            )
            self.assertTrue(
                summary_csv_path.exists()
            )

            payload = json.loads(
                summary_json_path.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(
                payload["total_surveys"],
                1
            )
            self.assertEqual(
                payload["operator_metadata"]["operator"],
                "Sergei"
            )

    def test_logger_rejects_records_before_start(self):
        logger = HardwareValidationLogger(
            HardwareValidationSession(
                self._config()
            )
        )

        with self.assertRaises(RuntimeError):
            logger.log_frame(
                self._frame()
            )


if __name__ == "__main__":
    unittest.main()
