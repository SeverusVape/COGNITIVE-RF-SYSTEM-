import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

from SDR.fft_processing import compute_windowed_fft
from UTILS.frequency_axis import build_frequency_axis
from VALIDATION.real_rf.dataset import (
    DATASET_SCHEMA_VERSION,
    METADATA_FILENAME,
    SAMPLES_FILENAME,
    RealRFDatasetMetadata,
    create_dataset,
    load_dataset,
)
from VALIDATION.real_rf.capture import (
    capture_dataset,
    parse_gain,
)
from VALIDATION.detector_evaluation import DetectorAdapter
from VALIDATION.real_rf.comparison import (
    compare_dataset,
    evaluate_dataset,
    main as comparison_main,
)


class RealRFDatasetTests(unittest.TestCase):
    def setUp(self):
        self.frames = np.asarray(
            [
                np.exp(
                    2j
                    * np.pi
                    * 0.125
                    * np.arange(16)
                ),
                np.exp(
                    2j
                    * np.pi
                    * -0.25
                    * np.arange(16)
                )
            ],
            dtype=np.complex64
        )

    def create_test_dataset(self, root):
        return create_dataset(
            root,
            dataset_id="RF-TEST-001",
            scenario="deterministic two-frame fixture",
            notes="unit test",
            center_frequency_hz=100e6,
            sample_rate_hz=2.048e6,
            gain="auto",
            iq_frames=self.frames,
            capture_duration_seconds=0.01,
            timestamp_utc="2026-07-26T12:00:00+00:00"
        )

    def test_dataset_round_trip_and_metadata_dimensions(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_test_dataset(directory)

            self.assertEqual(
                DATASET_SCHEMA_VERSION,
                dataset.metadata.schema_version
            )
            self.assertEqual(
                self.frames.shape[1],
                dataset.metadata.iq_samples_per_frame
            )
            self.assertEqual(
                self.frames.shape[1],
                dataset.metadata.fft_size
            )
            self.assertEqual(
                self.frames.size,
                dataset.metadata.sample_count
            )
            np.testing.assert_array_equal(
                self.frames,
                dataset.iq_frames
            )

    def test_dataset_creation_prevents_overwrite(self):
        with TemporaryDirectory() as directory:
            self.create_test_dataset(directory)

            with self.assertRaises(FileExistsError):
                self.create_test_dataset(directory)

    def test_dataset_id_rejects_path_traversal(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                create_dataset(
                    directory,
                    dataset_id="../outside",
                    scenario="invalid",
                    notes="",
                    center_frequency_hz=100e6,
                    sample_rate_hz=2.048e6,
                    gain="auto",
                    iq_frames=self.frames,
                    capture_duration_seconds=1.0
                )

            self.assertFalse(
                (
                    Path(directory).parent
                    / "outside"
                ).exists()
            )

    def test_loaded_iq_and_replay_arrays_are_read_only(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_test_dataset(directory)
            replay_frame = next(dataset.replay())

            self.assertFalse(dataset.iq_frames.flags.writeable)
            self.assertFalse(replay_frame.iq_samples.flags.writeable)
            self.assertFalse(replay_frame.power_db.flags.writeable)
            self.assertFalse(replay_frame.freqs_mhz.flags.writeable)

            with self.assertRaises(ValueError):
                replay_frame.power_db[0] = 0.0

    def test_replay_matches_existing_fft_and_frequency_axis(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_test_dataset(directory)
            replay_frames = tuple(dataset.replay())
            _, expected_frequencies = build_frequency_axis(
                self.frames.shape[1],
                2.048e6,
                100e6
            )

            self.assertEqual(2, len(replay_frames))

            for index, replay_frame in enumerate(replay_frames):
                np.testing.assert_allclose(
                    compute_windowed_fft(self.frames[index]),
                    replay_frame.power_db
                )
                np.testing.assert_allclose(
                    expected_frequencies,
                    replay_frame.freqs_mhz
                )

    def test_repeated_replay_is_deterministic(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_test_dataset(directory)
            first = tuple(dataset.replay())
            second = tuple(dataset.replay())

            for first_frame, second_frame in zip(first, second):
                np.testing.assert_array_equal(
                    first_frame.iq_samples,
                    second_frame.iq_samples
                )
                np.testing.assert_array_equal(
                    first_frame.power_db,
                    second_frame.power_db
                )
                np.testing.assert_array_equal(
                    first_frame.freqs_mhz,
                    second_frame.freqs_mhz
                )

    def test_rejects_invalid_iq_arrays(self):
        invalid_arrays = (
            np.ones(16, dtype=np.complex64),
            np.ones((1, 16), dtype=float),
            np.asarray(
                [[complex(np.nan, 0)] * 16],
                dtype=np.complex64
            )
        )

        with TemporaryDirectory() as directory:
            for index, samples in enumerate(invalid_arrays):
                with self.subTest(index=index):
                    with self.assertRaises(ValueError):
                        create_dataset(
                            directory,
                            dataset_id=f"invalid-{index}",
                            scenario="invalid",
                            notes="",
                            center_frequency_hz=100e6,
                            sample_rate_hz=2.048e6,
                            gain="auto",
                            iq_frames=samples,
                            capture_duration_seconds=1.0
                        )

    def test_rejects_corrupted_metadata_and_array_shape(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_test_dataset(directory)
            metadata_path = dataset.path / METADATA_FILENAME
            metadata = json.loads(
                metadata_path.read_text(
                    encoding="utf-8"
                )
            )
            metadata["frame_count"] = 3
            metadata_path.write_text(
                json.dumps(metadata),
                encoding="utf-8"
            )

            with self.assertRaises(ValueError):
                load_dataset(dataset.path)

        with TemporaryDirectory() as directory:
            dataset = self.create_test_dataset(directory)
            np.save(
                dataset.path / SAMPLES_FILENAME,
                self.frames[:1],
                allow_pickle=False
            )

            with self.assertRaises(ValueError):
                load_dataset(dataset.path)

    def test_metadata_rejects_fft_and_iq_size_mismatch(self):
        with self.assertRaises(ValueError):
            RealRFDatasetMetadata(
                schema_version=DATASET_SCHEMA_VERSION,
                dataset_id="RF-TEST-002",
                timestamp_utc="2026-07-26T12:00:00+00:00",
                scenario="invalid mismatch",
                notes="",
                center_frequency_hz=100e6,
                sample_rate_hz=2.048e6,
                gain="auto",
                iq_samples_per_frame=16,
                fft_size=8,
                frame_count=1,
                sample_count=16,
                capture_duration_seconds=1.0,
                detector_input_type="complex_iq_frames",
                preprocessing="compute_windowed_fft",
                window="hann_coherent_gain_compensated",
                array_file="samples.npy",
                array_dtype="complex64",
                array_shape=(1, 16)
            )


class FakeSDRManager:
    instances = []
    connected_on_start = True
    returned_frame = None

    def __init__(self, sample_rate, center_frequency, gain):
        self.sample_rate = sample_rate
        self.center_frequency = center_frequency
        self.gain = gain
        self.connected = self.connected_on_start
        self.closed = False
        self.read_count = 0
        self.__class__.instances.append(self)

    def read_samples(self, sample_count):
        self.read_count += 1

        if self.returned_frame is not None:
            return self.returned_frame

        return np.full(
            sample_count,
            complex(self.read_count, -self.read_count),
            dtype=np.complex64
        )

    def close(self):
        self.closed = True
        self.connected = False


class RealRFCaptureTests(unittest.TestCase):
    def setUp(self):
        FakeSDRManager.instances = []
        FakeSDRManager.connected_on_start = True
        FakeSDRManager.returned_frame = None

    def capture(self, directory):
        return capture_dataset(
            directory,
            dataset_id="RF-CAPTURE-001",
            scenario="mock hardware",
            notes="capture test",
            center_frequency_hz=101.1e6,
            sample_rate_hz=2.048e6,
            gain="auto",
            frame_count=3,
            iq_samples_per_frame=16,
            manager_factory=FakeSDRManager
        )

    def test_capture_uses_existing_manager_and_closes_receiver(self):
        with TemporaryDirectory() as directory:
            dataset = self.capture(directory)
            manager = FakeSDRManager.instances[-1]

            self.assertEqual(3, manager.read_count)
            self.assertTrue(manager.closed)
            self.assertEqual((3, 16), dataset.iq_frames.shape)
            self.assertEqual(101.1e6, manager.center_frequency)

    def test_capture_failure_does_not_create_dataset(self):
        FakeSDRManager.returned_frame = np.ones(
            15,
            dtype=np.complex64
        )

        with TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                self.capture(directory)

            manager = FakeSDRManager.instances[-1]
            self.assertTrue(manager.closed)
            self.assertFalse(
                (
                    Path(directory)
                    / "RF-CAPTURE-001"
                ).exists()
            )

    def test_connection_failure_closes_receiver(self):
        FakeSDRManager.connected_on_start = False

        with TemporaryDirectory() as directory:
            with self.assertRaises(RuntimeError):
                self.capture(directory)

            self.assertTrue(
                FakeSDRManager.instances[-1].closed
            )

    def test_capture_arguments_are_validated_before_hardware_access(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                capture_dataset(
                    directory,
                    dataset_id="invalid",
                    scenario="invalid",
                    notes="",
                    center_frequency_hz=100e6,
                    sample_rate_hz=2.048e6,
                    gain="auto",
                    frame_count=0,
                    iq_samples_per_frame=16,
                    manager_factory=FakeSDRManager
                )

        self.assertEqual([], FakeSDRManager.instances)

    def test_parse_gain_accepts_auto_and_finite_numeric_values(self):
        self.assertEqual("auto", parse_gain("AUTO"))
        self.assertEqual(12.5, parse_gain("12.5"))

        for value in ("invalid", "nan", "inf"):
            with self.subTest(value=value):
                with self.assertRaises(Exception):
                    parse_gain(value)


class RecordingDetector:
    def __init__(self, name, frequency_offset_mhz=0.0):
        self.name = name
        self.frequency_offset_mhz = frequency_offset_mhz
        self.input_records = []

    def callback(self, power_db, freqs_mhz):
        self.input_records.append(
            (
                power_db.copy(),
                freqs_mhz.copy(),
                power_db.flags.writeable,
                freqs_mhz.flags.writeable
            )
        )
        peak_index = int(np.argmax(power_db))
        peaks = [
            (
                float(freqs_mhz[peak_index])
                + self.frequency_offset_mhz,
                float(power_db[peak_index]),
                1.0
            )
        ]
        threshold = np.full_like(
            power_db,
            np.median(power_db)
        )
        return peaks, threshold

    def adapter(self):
        return DetectorAdapter(
            name=self.name,
            callback=self.callback
        )


class RealRFComparisonTests(unittest.TestCase):
    def create_dataset(self, root):
        sample_count = 128
        samples = np.arange(sample_count)
        frames = np.asarray(
            [
                np.exp(
                    2j
                    * np.pi
                    * 0.125
                    * samples
                ),
                np.exp(
                    2j
                    * np.pi
                    * -0.25
                    * samples
                )
            ],
            dtype=np.complex64
        )
        return create_dataset(
            root,
            dataset_id="RF-COMPARE-001",
            scenario="comparison fixture",
            notes="no ground truth",
            center_frequency_hz=100e6,
            sample_rate_hz=2.048e6,
            gain="auto",
            iq_frames=frames,
            capture_duration_seconds=0.01,
            timestamp_utc="2026-07-26T12:00:00+00:00"
        )

    def test_detectors_receive_identical_read_only_replay_inputs(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_dataset(directory)
            detector_a = RecordingDetector("detector_a")
            detector_b = RecordingDetector("detector_b")
            evaluation = evaluate_dataset(
                dataset,
                detectors=(
                    detector_a.adapter(),
                    detector_b.adapter()
                ),
                repetitions=2
            )

            self.assertEqual(4, len(detector_a.input_records))
            self.assertEqual(4, len(detector_b.input_records))

            for record_a, record_b in zip(
                    detector_a.input_records,
                    detector_b.input_records
            ):
                np.testing.assert_array_equal(
                    record_a[0],
                    record_b[0]
                )
                np.testing.assert_array_equal(
                    record_a[1],
                    record_b[1]
                )
                self.assertFalse(record_a[2])
                self.assertFalse(record_a[3])
                self.assertFalse(record_b[2])
                self.assertFalse(record_b[3])

            self.assertEqual(
                {
                    "detector_a": True,
                    "detector_b": True
                },
                evaluation["consistency"]
            )

    def test_reports_include_thresholds_and_no_winner_claim(self):
        with (
                TemporaryDirectory() as dataset_root,
                TemporaryDirectory() as report_root
        ):
            dataset = self.create_dataset(dataset_root)
            report_directory = compare_dataset(
                dataset.path,
                output_root=report_root,
                detectors=(
                    RecordingDetector(
                        "adaptive_test"
                    ).adapter(),
                    RecordingDetector(
                        "candidate_test",
                        frequency_offset_mhz=0.1
                    ).adapter()
                ),
                repetitions=2
            )

            expected_files = {
                "adaptive_test_results.json",
                "adaptive_test_thresholds.npz",
                "candidate_test_results.json",
                "candidate_test_thresholds.npz",
                "comparison.json",
                "detections.csv",
                "pairwise_comparison.csv",
                "summary.txt"
            }
            self.assertEqual(
                expected_files,
                {
                    path.name
                    for path in report_directory.iterdir()
                }
            )

            comparison = json.loads(
                (
                    report_directory
                    / "comparison.json"
                ).read_text(
                    encoding="utf-8"
                )
            )
            self.assertFalse(
                comparison["ground_truth_available"]
            )
            self.assertIn(
                "does not select a winner",
                comparison["interpretation_boundary"]
            )
            self.assertNotIn(
                "selected_detector",
                comparison
            )
            self.assertNotIn(
                "recommended detector",
                (
                    report_directory
                    / "summary.txt"
                ).read_text(
                    encoding="utf-8"
                ).lower()
            )

            thresholds = np.load(
                report_directory
                / "adaptive_test_thresholds.npz"
            )["thresholds"]
            self.assertEqual((4, 128), thresholds.shape)

            self.assertTrue(
                (dataset.path / SAMPLES_FILENAME).exists()
            )
            self.assertFalse(
                (dataset.path / "comparison.json").exists()
            )

    def test_report_creation_prevents_overwrite(self):
        with (
                TemporaryDirectory() as dataset_root,
                TemporaryDirectory() as report_root
        ):
            dataset = self.create_dataset(dataset_root)
            detectors = (
                RecordingDetector("detector").adapter(),
            )
            compare_dataset(
                dataset.path,
                output_root=report_root,
                detectors=detectors,
                repetitions=1
            )

            with self.assertRaises(FileExistsError):
                compare_dataset(
                    dataset.path,
                    output_root=report_root,
                    detectors=detectors,
                    repetitions=1
                )

    def test_force_replaces_existing_report_directory(self):
        with (
                TemporaryDirectory() as dataset_root,
                TemporaryDirectory() as report_root
        ):
            dataset = self.create_dataset(dataset_root)
            detectors = (
                RecordingDetector("detector").adapter(),
            )
            report_directory = compare_dataset(
                dataset.path,
                output_root=report_root,
                detectors=detectors,
                repetitions=1
            )
            stale_file = report_directory / "stale.txt"
            stale_file.write_text(
                "obsolete",
                encoding="utf-8"
            )

            replaced_directory = compare_dataset(
                dataset.path,
                output_root=report_root,
                detectors=detectors,
                repetitions=1,
                force=True
            )

            self.assertEqual(
                report_directory,
                replaced_directory
            )
            self.assertFalse(stale_file.exists())
            self.assertTrue(
                (
                    replaced_directory
                    / "comparison.json"
                ).is_file()
            )

    def test_cli_existing_reports_has_friendly_force_guidance(self):
        with (
                TemporaryDirectory() as dataset_root,
                TemporaryDirectory() as report_root
        ):
            dataset = self.create_dataset(dataset_root)
            compare_dataset(
                dataset.path,
                output_root=report_root,
                repetitions=1
            )
            stdout = StringIO()
            stderr = StringIO()

            with (
                    redirect_stdout(stdout),
                    redirect_stderr(stderr)
            ):
                exit_code = comparison_main(
                    [
                        str(dataset.path),
                        "--output-root",
                        report_root,
                        "--repetitions",
                        "1"
                    ]
                )

            self.assertEqual(1, exit_code)
            self.assertEqual("", stdout.getvalue())
            self.assertIn(
                "Comparison reports already exist",
                stderr.getvalue()
            )
            self.assertIn("--force", stderr.getvalue())
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_force_removal_permission_error_is_friendly(self):
        with (
                TemporaryDirectory() as dataset_root,
                TemporaryDirectory() as report_root
        ):
            dataset = self.create_dataset(dataset_root)
            compare_dataset(
                dataset.path,
                output_root=report_root,
                repetitions=1
            )
            stderr = StringIO()

            with (
                    patch(
                        "VALIDATION.real_rf.comparison.shutil.rmtree",
                        side_effect=PermissionError(
                            "removal blocked"
                        )
                    ),
                    redirect_stderr(stderr)
            ):
                exit_code = comparison_main(
                    [
                        str(dataset.path),
                        "--output-root",
                        report_root,
                        "--repetitions",
                        "1",
                        "--force"
                    ]
                )

            self.assertEqual(1, exit_code)
            self.assertIn(
                "Permission denied",
                stderr.getvalue()
            )
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_missing_dataset_is_friendly(self):
        with TemporaryDirectory() as directory:
            missing_dataset = (
                Path(directory)
                / "RF-MISSING"
            )
            stderr = StringIO()

            with redirect_stderr(stderr):
                exit_code = comparison_main(
                    [str(missing_dataset)]
                )

            self.assertEqual(1, exit_code)
            self.assertIn(
                "Dataset not found",
                stderr.getvalue()
            )
            self.assertNotIn("Traceback", stderr.getvalue())

    def test_existing_adapters_process_recorded_dataset(self):
        with TemporaryDirectory() as directory:
            dataset = self.create_dataset(directory)
            evaluation = evaluate_dataset(
                dataset,
                repetitions=1
            )

            self.assertEqual(
                {"adaptive", "os_cfar"},
                {
                    result.detector
                    for result in evaluation["frame_results"]
                }
            )
            self.assertEqual(
                {
                    "adaptive": True,
                    "os_cfar": True
                },
                evaluation["consistency"]
            )


if __name__ == "__main__":
    unittest.main()
