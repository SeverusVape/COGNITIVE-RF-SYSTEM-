from datetime import datetime, timedelta, timezone
import csv
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from VALIDATION.hardware.validation_controller import (
    HardwareValidationController,
    HardwareValidationSettings,
)


class HardwareValidationIntegrationTests(unittest.TestCase):

    @staticmethod
    def _datetime_provider():
        start = datetime(
            2026,
            7,
            24,
            18,
            30,
            tzinfo=timezone.utc
        )
        counter = {
            "value": 0
        }

        def provide():
            timestamp = start + timedelta(
                seconds=counter["value"]
            )
            counter["value"] += 1
            return timestamp

        return provide

    @staticmethod
    def _settings():
        return HardwareValidationSettings(
            configuration_id="CFG-HW-INTEGRATION",
            session_name="Simulated integration session",
            test_band="88-92 MHz",
            operator_notes="Temporary-directory test",
            antenna_description="Synthetic source",
            location_description="Automated test environment",
            expected_signal_description="Two deterministic peaks",
            sample_rate_hz=2.048e6,
            fft_size=8,
            gain=20.0,
            detector_configuration={
                "threshold_margin_db": 10.0
            },
            confirmation_configuration={
                "required_hits": 2,
                "window_frames": 3
            },
            logging_interval_ms=1000,
            survey_defaults={
                "settling_delay_ms": 500
            },
            update_interval_ms=100
        )

    @staticmethod
    def _frame_arguments(
            occupancy_percent,
            detector_runtime_ms
    ):
        return {
            "freqs_mhz": np.array(
                [
                    89.8,
                    89.9,
                    90.0,
                    90.1
                ]
            ),
            "power_db": np.array(
                [
                    20.0,
                    31.0,
                    45.0,
                    25.0
                ]
            ),
            "threshold_db": 30.0,
            "occupancy_percent": occupancy_percent,
            "raw_peaks": [
                (90.0, 45.0, 20.0),
                (89.9, 31.0, 10.0)
            ],
            "confirmed_peaks": [
                (90.0, 45.0, 20.0)
            ],
            "detector_runtime_ms": detector_runtime_ms,
            "smart_recommendation_mhz": 90.0,
            "application_mode": "survey"
        }

    def test_complete_simulated_session_generates_consistent_evidence(self):
        monotonic_times = iter(
            [
                1.0,
                2.1,
                3.2
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            controller = HardwareValidationController(
                settings=self._settings(),
                center_frequency_provider=lambda: 90e6,
                survey_frequencies_provider=lambda: [
                    88.0,
                    89.0,
                    90.0,
                    91.0,
                    92.0
                ],
                decision_mode_provider=(
                    lambda: "Smart Recommendation"
                ),
                results_root=temp_dir,
                datetime_provider=self._datetime_provider(),
                monotonic_provider=(
                    lambda: next(monotonic_times)
                ),
                git_sha_provider=lambda: "a" * 40
            )

            self.assertTrue(
                controller.start()
            )

            for occupancy, runtime in (
                    (8.0, 1.0),
                    (10.0, 1.5),
                    (12.0, 2.0)
            ):
                self.assertTrue(
                    controller.log_frame(
                        **self._frame_arguments(
                            occupancy,
                            runtime
                        )
                    )
                )

            self.assertTrue(
                controller.log_survey(
                    recommendation={
                        "frequency": 90.0,
                        "occupancy": 8.0,
                        "score": 70.0,
                        "runner_up_frequency": 89.0,
                        "runner_up_score": 65.0,
                        "score_margin": 5.0,
                        "decision_confidence": "MODERATE"
                    },
                    sorted_results=[
                        (92.0, 14.0),
                        (89.0, 11.0),
                        (90.0, 8.0)
                    ],
                    points_scanned=5,
                    average_occupancy=11.0,
                    decision_mode="SMART"
                )
            )

            session_directory = Path(
                controller.session_directory
            )

            self.assertTrue(
                controller.stop()
            )

            with (
                    session_directory
                    / "frames"
                    / "frame_records.csv"
            ).open(
                    newline="",
                    encoding="utf-8"
            ) as file_handle:
                frame_rows = list(
                    csv.DictReader(
                        file_handle
                    )
                )

            frame_jsonl = [
                json.loads(line)
                for line in (
                    session_directory
                    / "frames"
                    / "frame_records.jsonl"
                ).read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            survey_jsonl = [
                json.loads(line)
                for line in (
                    session_directory
                    / "surveys"
                    / "survey_records.jsonl"
                ).read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            config = json.loads(
                (
                    session_directory
                    / "session_config.json"
                ).read_text(
                    encoding="utf-8"
                )
            )
            summary = json.loads(
                (
                    session_directory
                    / "summaries"
                    / "session_summary.json"
                ).read_text(
                    encoding="utf-8"
                )
            )
            summary_markdown = (
                session_directory
                / "summaries"
                / "summary.md"
            ).read_text(
                encoding="utf-8"
            )

        self.assertEqual(
            len(frame_rows),
            3
        )
        self.assertEqual(
            len(frame_jsonl),
            3
        )
        self.assertEqual(
            len(survey_jsonl),
            1
        )
        self.assertEqual(
            config["active_decision_mode"],
            "SMART"
        )
        self.assertEqual(
            config["gain_mode"],
            "manual"
        )
        self.assertEqual(
            config["gain_db"],
            20.0
        )
        self.assertEqual(
            config["git_commit_sha"],
            "a" * 40
        )
        self.assertEqual(
            survey_jsonl[0]["decision_mode"],
            "SMART"
        )
        self.assertEqual(
            survey_jsonl[0]["winner_score"],
            70.0
        )
        self.assertEqual(
            summary["total_logged_frames"],
            len(frame_jsonl)
        )
        self.assertEqual(
            summary["total_surveys"],
            len(survey_jsonl)
        )
        self.assertEqual(
            summary["average_occupancy_percent"],
            10.0
        )
        self.assertEqual(
            summary["average_detector_runtime_ms"],
            1.5
        )
        self.assertEqual(
            summary["survey_completion_state_counts"],
            {
                "success": 1
            }
        )
        self.assertEqual(
            summary["errors_encountered"],
            []
        )
        self.assertIn(
            "Logged frames: 3",
            summary_markdown
        )
        self.assertIn(
            "Survey records: 1",
            summary_markdown
        )


if __name__ == "__main__":
    unittest.main()
