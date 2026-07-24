from datetime import datetime
import unittest

import numpy as np

from VALIDATION.hardware.validation_capture import (
    build_frame_record,
    build_session_config,
    build_survey_record,
    frequency_list_hz,
)


class HardwareValidationCaptureTests(unittest.TestCase):

    def test_frequency_list_converts_peak_mhz_to_hz(self):
        self.assertEqual(
            frequency_list_hz(
                [
                    (90.125, 45.0, 20.0),
                    (91.5, 40.0, 15.0)
                ]
            ),
            [
                90125000.0,
                91500000.0
            ]
        )

    def test_build_session_config_captures_frozen_settings(self):
        config = build_session_config(
            timestamp=datetime(
                2026,
                7,
                24,
                14,
                30,
                0
            ),
            configuration_id="CFG-HW-01",
            session_name="Brooklyn FM survey",
            test_band="88-92 MHz",
            operator_notes="Indoor window placement",
            antenna_description="RTL-SDR dipole",
            location_description="Bay Ridge",
            expected_signal_description="FM broadcast carriers",
            center_frequency_hz=90e6,
            sample_rate_hz=2.048e6,
            fft_size=8192,
            gain="auto",
            detector_configuration={
                "minimum_peak_distance_khz": 75.0
            },
            confirmation_configuration={
                "required_hits": 2
            },
            validation_log_interval_ms=1000,
            survey_defaults={
                "settling_delay_ms": 500
            }
        )

        payload = config.to_dict()

        self.assertEqual(
            payload["validation_id"],
            "VAL-20260724-143000"
        )
        self.assertEqual(
            payload["gain_mode"],
            "auto"
        )
        self.assertIsNone(
            payload["gain_db"]
        )
        self.assertEqual(
            payload["validation_log_interval_ms"],
            1000
        )

    def test_build_frame_record_uses_application_measurements(self):
        record = build_frame_record(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-001",
            frame_index=1,
            timestamp="2026-07-24T14:30:01-04:00",
            center_frequency_hz=90e6,
            freqs_mhz=np.array(
                [
                    89.9,
                    90.0,
                    90.1
                ]
            ),
            power_db=np.array(
                [
                    20.0,
                    45.0,
                    30.0
                ]
            ),
            threshold_db=31.5,
            occupancy_percent=8.25,
            raw_peaks=[
                (90.0, 45.0, 10.0)
            ],
            confirmed_peaks=[
                (90.0, 45.0, 10.0)
            ],
            detector_runtime_ms=1.2345,
            smart_recommendation_mhz=89.0,
            application_mode="survey"
        )

        payload = record.to_dict()

        self.assertEqual(
            payload["strongest_frequency_hz"],
            90000000.0
        )
        self.assertEqual(
            payload["raw_candidate_count"],
            1
        )
        self.assertEqual(
            payload["confirmed_signal_count"],
            1
        )
        self.assertEqual(
            payload["detector_runtime_ms"],
            1.234
        )
        self.assertEqual(
            payload["smart_recommendation_hz"],
            89000000.0
        )

    def test_build_survey_record_captures_decision_evidence(self):
        record = build_survey_record(
            validation_id="VAL-20260724-143000",
            session_id="SESSION-001",
            survey_index=1,
            timestamp="2026-07-24T14:31:00-04:00",
            survey_frequencies_mhz=[
                88.0,
                89.0,
                90.0
            ],
            sorted_results=[
                (88.0, 12.0),
                (90.0, 8.0)
            ],
            points_scanned=3,
            recommendation={
                "frequency": 90.0,
                "occupancy": 8.0,
                "score": 69.0,
                "runner_up_frequency": 88.0,
                "runner_up_score": 63.9,
                "score_margin": 5.1,
                "decision_confidence": "MODERATE"
            },
            decision_mode="SMART",
            average_occupancy=10.0
        )

        payload = record.to_dict()

        self.assertEqual(
            payload["start_frequency_hz"],
            88000000.0
        )
        self.assertEqual(
            payload["stop_frequency_hz"],
            90000000.0
        )
        self.assertEqual(
            payload["step_frequency_hz"],
            1000000.0
        )
        self.assertEqual(
            payload["winner_score"],
            69.0
        )
        self.assertEqual(
            payload["runner_up_frequency_hz"],
            88000000.0
        )
        self.assertIn(
            "Average occupancy: 10.0%",
            payload["notes"]
        )


if __name__ == "__main__":
    unittest.main()
