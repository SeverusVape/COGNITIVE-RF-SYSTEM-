from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from VALIDATION.hardware.validation_controller import (
    HardwareValidationController,
    HardwareValidationSettings,
)


class HardwareValidationControllerTests(unittest.TestCase):

    @staticmethod
    def _settings(
            logging_interval_ms=1000
    ):
        return HardwareValidationSettings(
            configuration_id="CFG-HW-01",
            session_name="Controller test",
            test_band="88-92 MHz",
            operator_notes="Automated test",
            antenna_description="Test antenna",
            location_description="Test location",
            expected_signal_description="Synthetic metadata",
            sample_rate_hz=2.048e6,
            fft_size=8192,
            gain="auto",
            detector_configuration={
                "threshold_margin_db": 10.0
            },
            confirmation_configuration={
                "required_hits": 2
            },
            logging_interval_ms=logging_interval_ms,
            survey_defaults={
                "settling_delay_ms": 500
            }
        )

    @staticmethod
    def _datetime_provider():
        start = datetime(
            2026,
            7,
            24,
            18,
            0,
            tzinfo=timezone.utc
        )
        counter = {
            "value": 0
        }

        def provide():
            value = start + timedelta(
                seconds=counter["value"]
            )
            counter["value"] += 1
            return value

        return provide

    @staticmethod
    def _frame_arguments():
        return {
            "freqs_mhz": np.array(
                [
                    89.9,
                    90.0,
                    90.1
                ]
            ),
            "power_db": np.array(
                [
                    20.0,
                    45.0,
                    30.0
                ]
            ),
            "threshold_db": 31.0,
            "occupancy_percent": 8.0,
            "raw_peaks": [
                (90.0, 45.0, 10.0)
            ],
            "confirmed_peaks": [
                (90.0, 45.0, 10.0)
            ],
            "detector_runtime_ms": 1.5,
        }

    def _controller(
            self,
            temp_dir,
            statuses=None,
            monotonic_provider=None,
            logging_interval_ms=1000,
            center_frequency_provider=None,
            status_callback=None,
            decision_mode_provider=None,
            git_sha_provider=None
    ):
        return HardwareValidationController(
            settings=self._settings(
                logging_interval_ms=logging_interval_ms
            ),
            center_frequency_provider=(
                center_frequency_provider
                or (lambda: 90e6)
            ),
            survey_frequencies_provider=lambda: [
                88.0,
                89.0,
                90.0
            ],
            decision_mode_provider=decision_mode_provider,
            status_callback=(
                status_callback
                if status_callback is not None
                else (
                    None
                    if statuses is None
                    else lambda state, message, path: statuses.append(
                        (
                            state,
                            message,
                            path
                        )
                    )
                )
            ),
            results_root=temp_dir,
            datetime_provider=self._datetime_provider(),
            monotonic_provider=monotonic_provider,
            git_sha_provider=git_sha_provider
        )

    def test_start_and_stop_manage_session_and_status(self):
        statuses = []

        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir,
                statuses=statuses
            )

            self.assertTrue(
                controller.start()
            )
            self.assertTrue(
                controller.active
            )
            output_directory = controller.session_directory
            self.assertTrue(
                controller.stop()
            )

        self.assertFalse(
            controller.active
        )
        self.assertEqual(
            statuses[0][0],
            "inactive"
        )
        self.assertEqual(
            statuses[1][0],
            "recording"
        )
        self.assertEqual(
            statuses[-1][0],
            "saved"
        )
        self.assertEqual(
            statuses[-1][2],
            output_directory
        )

    def test_duplicate_start_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir
            )

            self.assertTrue(
                controller.start()
            )
            first_directory = controller.session_directory
            self.assertFalse(
                controller.start()
            )

        self.assertEqual(
            controller.session_directory,
            first_directory
        )

    def test_stop_while_inactive_is_safe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir
            )

            self.assertFalse(
                controller.stop()
            )

    def test_inactive_controller_ignores_frame_and_survey_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir
            )

            frame_written = controller.log_frame(
                **self._frame_arguments()
            )
            survey_written = controller.log_survey(
                recommendation={
                    "frequency": 90.0,
                    "occupancy": 8.0
                },
                sorted_results=[
                    (90.0, 8.0)
                ],
                points_scanned=1,
                average_occupancy=8.0,
                decision_mode="SMART"
            )

            self.assertFalse(
                frame_written
            )
            self.assertFalse(
                survey_written
            )
            self.assertEqual(
                controller.frame_index,
                0
            )
            self.assertEqual(
                controller.survey_index,
                0
            )
            self.assertIsNone(
                controller.session_directory
            )
            self.assertEqual(
                list(
                    Path(temp_dir).iterdir()
                ),
                []
            )

    def test_logging_interval_controls_frame_evidence(self):
        times = iter(
            [
                1.0,
                1.5,
                2.1
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir,
                monotonic_provider=lambda: next(times)
            )
            controller.start()

            self.assertTrue(
                controller.log_frame(
                    **self._frame_arguments()
                )
            )
            self.assertFalse(
                controller.log_frame(
                    **self._frame_arguments()
                )
            )
            self.assertTrue(
                controller.log_frame(
                    **self._frame_arguments()
                )
            )

        self.assertEqual(
            controller.frame_index,
            2
        )

    def test_invalid_frame_is_recorded_without_advancing_index(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir,
                monotonic_provider=lambda: 1.0
            )
            controller.start()
            arguments = self._frame_arguments()
            arguments["freqs_mhz"] = np.array([])
            arguments["power_db"] = np.array([])

            self.assertFalse(
                controller.log_frame(
                    **arguments
                )
            )
            session_directory = (
                controller.session_directory
            )
            self.assertTrue(
                controller.stop()
            )
            event_log = (
                session_directory
                / "validation.log"
            ).read_text(
                encoding="utf-8"
            )

        self.assertEqual(
            controller.frame_index,
            0
        )
        self.assertTrue(
            any(
                "Skipped invalid validation frame"
                in error
                for error in controller.errors
            )
        )
        self.assertIn(
            "Skipped invalid validation frame",
            event_log
        )

    def test_survey_logging_uses_provided_canonical_frequencies(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir
            )
            controller.start()

            self.assertTrue(
                controller.log_survey(
                    recommendation={
                        "frequency": 90.0,
                        "occupancy": 8.0
                    },
                    sorted_results=[
                        (90.0, 8.0),
                        (88.0, 12.0)
                    ],
                    points_scanned=3,
                    average_occupancy=10.0,
                    decision_mode="SMART"
                )
            )

        self.assertEqual(
            controller.survey_index,
            1
        )

    def test_shutdown_stops_active_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir
            )
            controller.start()
            session_directory = (
                controller.session_directory
            )

            self.assertTrue(
                controller.shutdown()
            )
            event_log = (
                session_directory
                / "validation.log"
            ).read_text(
                encoding="utf-8"
            )

        self.assertFalse(
            controller.active
        )
        self.assertIn(
            "Application shutdown requested while validation was active.",
            event_log
        )

    def test_capture_error_is_contained_and_reported(self):
        center_frequency = [90e6]

        def center_frequency_provider():
            if center_frequency:
                return center_frequency.pop()

            raise RuntimeError(
                "receiver state unavailable"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            status_updates = []
            controller = self._controller(
                temp_dir,
                center_frequency_provider=(
                    center_frequency_provider
                ),
                status_callback=lambda *values: (
                    status_updates.append(values)
                )
            )
            self.assertTrue(
                controller.start()
            )

            self.assertFalse(
                controller.log_frame(
                    **self._frame_arguments()
                )
            )

        self.assertEqual(
            controller.frame_index,
            0
        )
        self.assertTrue(
            any(
                update[0] == "error"
                and "receiver state unavailable"
                in update[1]
                for update in status_updates
            )
        )

    def test_start_snapshots_runtime_mode_and_git_sha(self):
        commit_sha = "b" * 40

        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir,
                decision_mode_provider=(
                    lambda: "Smart Recommendation"
                ),
                git_sha_provider=lambda: commit_sha
            )
            self.assertTrue(
                controller.start()
            )
            config_path = (
                controller.session_directory
                / "session_config.json"
            )
            payload = json.loads(
                config_path.read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(
            payload["active_decision_mode"],
            "SMART"
        )
        self.assertEqual(
            payload["smart_mode_state"],
            "SMART"
        )
        self.assertEqual(
            payload["git_commit_sha"],
            commit_sha
        )


if __name__ == "__main__":
    unittest.main()
