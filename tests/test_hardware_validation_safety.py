from datetime import datetime, timezone
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from SDR.detection import detect_peaks
from SDR.fft_processing import compute_windowed_fft
from VALIDATION.hardware.validation_controller import (
    HardwareValidationController,
    HardwareValidationSettings,
)


class HardwareValidationSafetyTests(unittest.TestCase):

    @staticmethod
    def _settings():
        return HardwareValidationSettings(
            configuration_id="CFG-HW-SAFETY",
            session_name="Safety regression test",
            test_band="99-101 MHz",
            operator_notes="Deterministic automated check",
            antenna_description="Synthetic input",
            location_description="Automated test environment",
            expected_signal_description="Deterministic complex tones",
            sample_rate_hz=2.048e6,
            fft_size=8192,
            gain="auto",
            logging_interval_ms=1000
        )

    @classmethod
    def _controller(
            cls,
            results_root,
            center_frequency_provider=lambda: 100e6,
            monotonic_provider=lambda: 1.0
    ):
        return HardwareValidationController(
            settings=cls._settings(),
            center_frequency_provider=center_frequency_provider,
            survey_frequencies_provider=lambda: [],
            decision_mode_provider=lambda: "FREE",
            results_root=results_root,
            datetime_provider=lambda: datetime(
                2026,
                7,
                24,
                18,
                0,
                tzinfo=timezone.utc
            ),
            monotonic_provider=monotonic_provider,
            git_sha_provider=lambda: "a" * 40
        )

    @staticmethod
    def _deterministic_spectrum():
        sample_rate_hz = 2.048e6
        sample_count = 8192
        center_frequency_hz = 100e6
        sample_indices = np.arange(
            sample_count
        )
        random_generator = np.random.default_rng(
            20260724
        )
        samples = (
            np.exp(
                2j
                * np.pi
                * 180e3
                * sample_indices
                / sample_rate_hz
            )
            + 0.55
            * np.exp(
                2j
                * np.pi
                * -310e3
                * sample_indices
                / sample_rate_hz
            )
            + 0.03
            * (
                random_generator.normal(
                    size=sample_count
                )
                + 1j
                * random_generator.normal(
                    size=sample_count
                )
            )
        )
        frequencies_hz = (
            np.fft.fftshift(
                np.fft.fftfreq(
                    sample_count,
                    d=1 / sample_rate_hz
                )
            )
            + center_frequency_hz
        )

        return (
            samples,
            frequencies_hz / 1e6
        )

    def test_inactive_mode_short_circuits_before_capture_work(self):
        def unexpected_provider_call():
            raise AssertionError(
                "Inactive validation accessed runtime state."
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir,
                center_frequency_provider=(
                    unexpected_provider_call
                ),
                monotonic_provider=(
                    unexpected_provider_call
                )
            )

            with patch(
                    "VALIDATION.hardware.validation_controller."
                    "build_frame_record"
            ) as build_frame_record_mock:
                written = controller.log_frame(
                    freqs_mhz=np.array(
                        [
                            99.9,
                            100.0
                        ]
                    ),
                    power_db=np.array(
                        [
                            20.0,
                            40.0
                        ]
                    ),
                    threshold_db=30.0,
                    occupancy_percent=10.0,
                    raw_peaks=[],
                    confirmed_peaks=[],
                    detector_runtime_ms=1.0
                )

            self.assertFalse(
                written
            )
            build_frame_record_mock.assert_not_called()

    def test_active_logging_does_not_mutate_detector_evidence(self):
        samples, frequencies_mhz = (
            self._deterministic_spectrum()
        )
        power_db = compute_windowed_fft(
            samples
        )
        raw_peaks_before, threshold_before = detect_peaks(
            power_db,
            frequencies_mhz
        )
        power_snapshot = power_db.copy()
        frequency_snapshot = frequencies_mhz.copy()
        threshold_snapshot = threshold_before.copy()
        peaks_snapshot = [
            tuple(peak)
            for peak in raw_peaks_before
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            controller = self._controller(
                temp_dir
            )
            self.assertTrue(
                controller.start()
            )
            self.assertTrue(
                controller.log_frame(
                    freqs_mhz=frequencies_mhz,
                    power_db=power_db,
                    threshold_db=float(
                        np.median(
                            threshold_before
                        )
                    ),
                    occupancy_percent=10.0,
                    raw_peaks=raw_peaks_before,
                    confirmed_peaks=raw_peaks_before,
                    detector_runtime_ms=1.0
                )
            )
            self.assertTrue(
                controller.stop()
            )

        np.testing.assert_array_equal(
            frequencies_mhz,
            frequency_snapshot
        )
        np.testing.assert_array_equal(
            power_db,
            power_snapshot
        )
        np.testing.assert_array_equal(
            threshold_before,
            threshold_snapshot
        )
        self.assertEqual(
            [
                tuple(peak)
                for peak in raw_peaks_before
            ],
            peaks_snapshot
        )

        repeated_peaks, repeated_threshold = detect_peaks(
            power_db,
            frequencies_mhz
        )

        np.testing.assert_array_equal(
            repeated_threshold,
            threshold_before
        )
        self.assertEqual(
            [
                tuple(peak)
                for peak in repeated_peaks
            ],
            peaks_snapshot
        )


if __name__ == "__main__":
    unittest.main()
