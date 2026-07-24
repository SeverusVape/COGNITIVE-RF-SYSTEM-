from datetime import datetime, timedelta, timezone
import tempfile
import unittest

from VALIDATION.hardware.validation_models import (
    ValidationFrameRecord,
    ValidationSessionConfig,
    ValidationSurveyRecord,
)
from VALIDATION.hardware.validation_session import (
    HardwareValidationSession,
    generate_session_id,
    generate_validation_id,
)


class HardwareValidationSessionTests(unittest.TestCase):

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
            detector_name="adaptive"
        )

    @staticmethod
    def _frame(
            frame_index=1,
            raw_candidate_count=2,
            confirmed_signal_count=1,
            detector_runtime_ms=1.5,
            occupancy_percent=8.0,
            strongest_fft_bin_power_db=42.0,
            smart_recommendation_hz=90e6
    ):
        return ValidationFrameRecord(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-20260724-143000-test",
            frame_index=frame_index,
            timestamp="2026-07-24T14:30:01-04:00",
            center_frequency_hz=90e6,
            strongest_fft_bin_frequency_hz=90.1e6,
            strongest_fft_bin_power_db=strongest_fft_bin_power_db,
            average_power_db=21.0,
            threshold_db=31.0,
            occupancy_percent=occupancy_percent,
            raw_candidate_count=raw_candidate_count,
            confirmed_signal_count=confirmed_signal_count,
            detector_runtime_ms=detector_runtime_ms,
            confirmed_frequencies_hz=[
                90.1e6
            ],
            candidate_frequencies_hz=[
                90.1e6,
                90.4e6
            ],
            smart_recommendation_hz=smart_recommendation_hz
        )

    @staticmethod
    def _survey(
            survey_index=1,
            smart_recommendation_hz=90e6,
            completion_status="success"
    ):
        return ValidationSurveyRecord(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-20260724-143000-test",
            survey_index=survey_index,
            timestamp="2026-07-24T14:31:00-04:00",
            start_frequency_hz=88e6,
            stop_frequency_hz=92e6,
            step_frequency_hz=1e6,
            number_of_points=5,
            best_frequency_hz=smart_recommendation_hz,
            smart_recommendation_hz=smart_recommendation_hz,
            completion_status=completion_status
        )

    def test_identifier_helpers_use_stable_formats(self):
        timestamp = datetime(
            2026,
            7,
            24,
            14,
            30,
            0
        )

        self.assertEqual(
            generate_validation_id(timestamp),
            "VAL-20260724-143000"
        )
        self.assertEqual(
            generate_session_id(timestamp, suffix="lab run"),
            "SESSION-20260724-143000-lab-run"
        )

    def test_start_creates_collision_safe_evidence_folders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_session = HardwareValidationSession(
                self._config(),
                results_root=temp_dir
            )
            first_path = first_session.start()

            second_session = HardwareValidationSession(
                self._config(),
                results_root=temp_dir
            )
            second_path = second_session.start()

            self.assertNotEqual(
                first_path,
                second_path
            )
            self.assertTrue(
                second_path.name.endswith("_02")
            )

            for child_name in (
                    "frames",
                    "surveys",
                    "summaries",
                    "artifacts"
            ):
                self.assertTrue(
                    (
                        first_path
                        / child_name
                    ).is_dir()
                )

    def test_registering_records_updates_summary_metrics(self):
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
                start + timedelta(seconds=5)
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            session = HardwareValidationSession(
                self._config(),
                results_root=temp_dir,
                timestamp_provider=lambda: next(timestamps)
            )
            session.start()
            session.register_frame(
                self._frame(frame_index=1)
            )
            session.register_invalid_frame(
                "Skipped invalid validation frame."
            )
            session.register_frame(
                self._frame(
                    frame_index=2,
                    raw_candidate_count=4,
                    confirmed_signal_count=2,
                    detector_runtime_ms=2.5,
                    occupancy_percent=10.0,
                    strongest_fft_bin_power_db=45.0
                )
            )
            session.register_survey(
                self._survey(survey_index=1)
            )
            session.register_survey(
                self._survey(
                    survey_index=2,
                    smart_recommendation_hz=91e6,
                    completion_status="cancelled"
                )
            )
            summary = session.stop(
                operator_metadata={
                    "operator": "Sergei"
                },
                limitations=[
                    "Indoor antenna placement"
                ]
            )

        payload = summary.to_dict()

        self.assertFalse(
            session.active
        )
        self.assertTrue(
            session.stopped
        )
        self.assertEqual(
            payload["duration_seconds"],
            5.0
        )
        self.assertEqual(
            payload["total_logged_frames"],
            2
        )
        self.assertEqual(
            payload["valid_frame_count"],
            2
        )
        self.assertEqual(
            payload["skipped_invalid_frame_count"],
            1
        )
        self.assertEqual(
            payload["total_surveys"],
            2
        )
        self.assertEqual(
            payload["survey_completion_state_counts"],
            {
                "cancelled": 1,
                "success": 1
            }
        )
        self.assertEqual(
            payload["average_raw_candidate_count"],
            3.0
        )
        self.assertEqual(
            payload["average_confirmed_signal_count"],
            1.5
        )
        self.assertEqual(
            payload["average_detector_runtime_ms"],
            2.0
        )
        self.assertEqual(
            payload["average_occupancy_percent"],
            9.0
        )
        self.assertEqual(
            payload["strongest_observed_fft_bin_power_db"],
            45.0
        )
        self.assertEqual(
            payload["strongest_observed_fft_bin_frequency_hz"],
            90.1e6
        )
        self.assertEqual(
            payload["survey_recommendation_repeatability_percent"],
            50.0
        )
        self.assertEqual(
            payload["most_frequent_smart_recommendation_hz"],
            90e6
        )
        self.assertEqual(
            payload["warnings_encountered"],
            [
                "Skipped invalid validation frame."
            ]
        )
        self.assertEqual(
            payload["operator_metadata"]["operator"],
            "Sergei"
        )

    def test_session_rejects_records_before_start(self):
        session = HardwareValidationSession(
            self._config()
        )

        with self.assertRaises(RuntimeError):
            session.register_frame(
                self._frame()
            )

    def test_session_rejects_identity_mismatch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session = HardwareValidationSession(
                self._config(),
                results_root=temp_dir
            )
            session.start()

            with self.assertRaises(ValueError):
                session.register_frame(
                    ValidationFrameRecord(
                        **{
                            **self._frame().to_dict(),
                            "session_id": "SESSION-other"
                        }
                    )
                )

    def test_stopped_session_cannot_restart(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session = HardwareValidationSession(
                self._config(),
                results_root=temp_dir
            )
            session.start()
            session.stop()

            with self.assertRaises(RuntimeError):
                session.start()


if __name__ == "__main__":
    unittest.main()
