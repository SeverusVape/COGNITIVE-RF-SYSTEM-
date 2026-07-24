import json
import unittest

from VALIDATION.hardware.validation_models import (
    ValidationFrameRecord,
    ValidationSessionConfig,
    ValidationSessionSummary,
    ValidationSurveyRecord,
)


class HardwareValidationModelTests(unittest.TestCase):

    @staticmethod
    def _session_config():
        return ValidationSessionConfig(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-001",
            configuration_id="CFG-HW-01",
            session_name="Brooklyn FM survey",
            test_band="88–92 MHz",
            operator_notes="Indoor test",
            antenna_description="Dipole antenna",
            location_description="Fourth-floor residential window",
            expected_signal_description="Local FM broadcast carriers",
            start_timestamp="2026-07-24T14:30:00-04:00",
            center_frequency_hz=90e6,
            sample_rate_hz=2.048e6,
            fft_size=8192,
            gain_mode="auto",
            gain_db=None,
            detector_name="adaptive",
            detector_configuration={
                "threshold_margin_db": 10.0
            },
            confirmation_configuration={
                "required_hits": 2
            }
        )

    def test_session_config_is_json_serializable(self):
        config = self._session_config()

        payload = json.loads(
            config.to_json()
        )

        self.assertEqual(
            payload["validation_id"],
            "VAL-20260724-143000"
        )
        self.assertEqual(
            payload["fft_size"],
            8192
        )
        self.assertIsNone(
            payload["gain_db"]
        )

    def test_frame_record_preserves_frequency_lists(self):
        record = ValidationFrameRecord(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-001",
            frame_index=1,
            timestamp="2026-07-24T14:30:01-04:00",
            center_frequency_hz=90e6,
            strongest_fft_bin_frequency_hz=90.1e6,
            strongest_fft_bin_power_db=42.5,
            average_power_db=20.2,
            threshold_db=31.4,
            occupancy_percent=8.3,
            raw_candidate_count=2,
            confirmed_signal_count=1,
            detector_runtime_ms=1.25,
            confirmed_frequencies_hz=[90.1e6],
            candidate_frequencies_hz=[
                90.1e6,
                90.4e6
            ],
            smart_recommendation_hz=89e6,
            application_mode="survey"
        )

        payload = record.to_dict()

        self.assertEqual(
            payload["confirmed_frequencies_hz"],
            [90.1e6]
        )
        self.assertEqual(
            payload["raw_candidate_count"],
            2
        )
        self.assertEqual(
            payload["strongest_fft_bin_frequency_hz"],
            90.1e6
        )
        self.assertNotIn(
            "strongest_frequency_hz",
            payload
        )
        self.assertEqual(
            record.strongest_frequency_hz,
            90.1e6
        )

    def test_survey_record_captures_decision_evidence(self):
        record = ValidationSurveyRecord(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-001",
            survey_index=1,
            timestamp="2026-07-24T14:31:00-04:00",
            start_frequency_hz=88e6,
            stop_frequency_hz=92e6,
            step_frequency_hz=1e6,
            number_of_points=5,
            ranked_results=[
                {
                    "frequency_hz": 91e6,
                    "occupancy_percent": 14.2
                }
            ],
            best_frequency_hz=90e6,
            smart_recommendation_hz=90e6,
            survey_runtime_seconds=5.8,
            completion_status="success",
            decision_mode="SMART",
            recommended_occupancy_percent=8.0,
            winner_score=69.0,
            runner_up_frequency_hz=88e6,
            runner_up_score=63.9,
            score_margin=5.1,
            decision_confidence="MODERATE"
        )

        payload = record.to_dict()

        self.assertEqual(
            payload["completion_status"],
            "success"
        )
        self.assertEqual(
            payload["decision_confidence"],
            "MODERATE"
        )
        self.assertEqual(
            payload["ranked_results"][0]["frequency_hz"],
            91e6
        )

    def test_summary_supports_empty_optional_metrics(self):
        summary = ValidationSessionSummary(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-001",
            session_name="No-data session",
            test_band="88-92 MHz",
            configuration_id="CFG-HW-01",
            git_commit_sha="unknown",
            start_timestamp="2026-07-24T14:30:00-04:00",
            stop_timestamp="2026-07-24T14:30:02-04:00",
            duration_seconds=2.0,
            total_logged_frames=0,
            valid_frame_count=0,
            skipped_invalid_frame_count=0,
            total_surveys=0,
            survey_completion_state_counts={},
            average_raw_candidate_count=None,
            average_confirmed_signal_count=None,
            average_detector_runtime_ms=None,
            maximum_detector_runtime_ms=None,
            average_occupancy_percent=None
        )

        payload = summary.to_dict()

        self.assertEqual(
            payload["errors_encountered"],
            []
        )
        self.assertIsNone(
            payload["average_occupancy_percent"]
        )

    def test_non_json_safe_values_are_rejected(self):
        with self.assertRaises(TypeError):
            ValidationSessionConfig(
                **{
                    **self._session_config().to_dict(),
                    "detector_configuration": {
                        "invalid": object()
                    }
                }
            )

    def test_non_finite_values_are_rejected(self):
        with self.assertRaises(ValueError):
            ValidationFrameRecord(
                validation_id="VAL-20260724-143000",
                session_id="SESSION-001",
                frame_index=1,
                timestamp="2026-07-24T14:30:01-04:00",
                center_frequency_hz=90e6,
                strongest_fft_bin_frequency_hz=None,
                strongest_fft_bin_power_db=None,
                average_power_db=float("nan"),
                threshold_db=None,
                occupancy_percent=None,
                raw_candidate_count=0,
                confirmed_signal_count=0,
                detector_runtime_ms=None
            )


if __name__ == "__main__":
    unittest.main()
