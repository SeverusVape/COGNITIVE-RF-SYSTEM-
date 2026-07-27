"""Offline detector comparison on immutable recorded real-RF datasets."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from itertools import combinations
import json
from pathlib import Path
import shutil
import sys
from time import perf_counter

import numpy as np

from VALIDATION.detector_evaluation import (
    DetectorAdapter,
    build_detector_adapters,
)
from VALIDATION.real_rf.dataset import (
    load_dataset,
    validate_identifier,
)


DEFAULT_REPORT_ROOT = (
    Path(__file__).resolve().parent
    / "reports"
)


@dataclass(frozen=True)
class NormalizedDetection:
    frequency_mhz: float
    power_db: float
    bandwidth_khz: float


@dataclass(frozen=True)
class DetectorFrameResult:
    detector: str
    dataset_id: str
    repetition: int
    frame_index: int
    runtime_ms: float
    detections: tuple[NormalizedDetection, ...]
    threshold_min_db: float
    threshold_median_db: float
    threshold_max_db: float


@dataclass(frozen=True)
class PairwiseFrameComparison:
    dataset_id: str
    repetition: int
    frame_index: int
    detector_a: str
    detector_b: str
    detector_a_count: int
    detector_b_count: int
    matched_count: int
    detector_a_only_count: int
    detector_b_only_count: int


def _normalize_detector_result(
        *,
        detector,
        dataset_id,
        repetition,
        frame_index,
        runtime_ms,
        peaks,
        threshold,
        expected_shape
):
    threshold = np.asarray(
        threshold,
        dtype=float
    )

    if threshold.shape != expected_shape:
        raise ValueError(
            f"{detector} threshold shape does not match detector input."
        )

    if np.any(np.isnan(threshold)):
        raise ValueError(
            f"{detector} threshold contains NaN values."
        )

    finite_threshold = threshold[
        np.isfinite(threshold)
    ]

    if finite_threshold.size == 0:
        raise ValueError(
            f"{detector} threshold has no finite values."
        )

    normalized_detections = []

    for peak in peaks:
        if not isinstance(peak, (list, tuple)) or len(peak) != 3:
            raise ValueError(
                f"{detector} returned an invalid detection tuple."
            )

        values = tuple(float(value) for value in peak)

        if not all(np.isfinite(values)):
            raise ValueError(
                f"{detector} returned a non-finite detection."
            )

        if values[2] < 0:
            raise ValueError(
                f"{detector} returned a negative bandwidth."
            )

        normalized_detections.append(
            NormalizedDetection(
                frequency_mhz=values[0],
                power_db=values[1],
                bandwidth_khz=values[2]
            )
        )

    result = DetectorFrameResult(
        detector=detector,
        dataset_id=dataset_id,
        repetition=repetition,
        frame_index=frame_index,
        runtime_ms=float(runtime_ms),
        detections=tuple(normalized_detections),
        threshold_min_db=float(np.min(finite_threshold)),
        threshold_median_db=float(np.median(finite_threshold)),
        threshold_max_db=float(np.max(finite_threshold))
    )

    threshold.setflags(write=False)

    return result, threshold


def _match_detection_counts(
        detections_a,
        detections_b,
        tolerance_hz
):
    if not np.isfinite(tolerance_hz) or tolerance_hz < 0:
        raise ValueError(
            "Detection matching tolerance must be finite and non-negative."
        )

    candidates = []

    for index_a, detection_a in enumerate(detections_a):
        for index_b, detection_b in enumerate(detections_b):
            error_hz = abs(
                detection_a.frequency_mhz
                - detection_b.frequency_mhz
            ) * 1e6

            if error_hz <= tolerance_hz:
                candidates.append(
                    (error_hz, index_a, index_b)
                )

    matched_a = set()
    matched_b = set()

    for _, index_a, index_b in sorted(candidates):
        if index_a in matched_a or index_b in matched_b:
            continue

        matched_a.add(index_a)
        matched_b.add(index_b)

    matched_count = len(matched_a)

    return (
        matched_count,
        len(detections_a) - matched_count,
        len(detections_b) - matched_count
    )


def evaluate_dataset(
        dataset,
        *,
        detectors=None,
        repetitions=2
):
    """Run every detector on identical immutable replay frames."""

    if detectors is None:
        detectors = build_detector_adapters()

    detectors = tuple(detectors)

    if not detectors:
        raise ValueError("At least one detector adapter is required.")

    if (
            isinstance(repetitions, bool)
            or not isinstance(repetitions, int)
            or repetitions < 1
    ):
        raise ValueError("Repetitions must be a positive integer.")

    detector_names = []

    for detector in detectors:
        if not isinstance(detector, DetectorAdapter):
            raise TypeError(
                "Detectors must use the existing DetectorAdapter contract."
            )

        if detector.name in detector_names:
            raise ValueError("Detector names must be unique.")

        detector_names.append(
            validate_identifier(
                "Detector name",
                detector.name
            )
        )

    frame_results = []
    thresholds = {
        detector.name: []
        for detector in detectors
    }
    pairwise_results = []
    first_outputs = {}
    consistency = {
        detector.name: True
        for detector in detectors
    }

    bin_width_hz = (
        dataset.metadata.sample_rate_hz
        / dataset.metadata.fft_size
    )

    for repetition in range(repetitions):
        for replay_frame in dataset.replay():
            frame_output = {}

            for detector in detectors:
                start = perf_counter()
                peaks, threshold = detector.callback(
                    replay_frame.power_db,
                    replay_frame.freqs_mhz
                )
                runtime_ms = (
                    perf_counter()
                    - start
                ) * 1000

                result, normalized_threshold = (
                    _normalize_detector_result(
                        detector=detector.name,
                        dataset_id=dataset.metadata.dataset_id,
                        repetition=repetition,
                        frame_index=replay_frame.frame_index,
                        runtime_ms=runtime_ms,
                        peaks=peaks,
                        threshold=threshold,
                        expected_shape=replay_frame.power_db.shape
                    )
                )

                frame_results.append(result)
                thresholds[detector.name].append(
                    normalized_threshold.copy()
                )
                frame_output[detector.name] = result

                output_key = (
                    detector.name,
                    replay_frame.frame_index
                )
                deterministic_value = (
                    result.detections,
                    normalized_threshold
                )

                if repetition == 0:
                    first_outputs[output_key] = deterministic_value
                else:
                    first_detections, first_threshold = first_outputs[
                        output_key
                    ]
                    consistency[detector.name] = (
                        consistency[detector.name]
                        and result.detections == first_detections
                        and np.array_equal(
                            normalized_threshold,
                            first_threshold
                        )
                    )

            for detector_a, detector_b in combinations(
                    detectors,
                    2
            ):
                result_a = frame_output[detector_a.name]
                result_b = frame_output[detector_b.name]
                matched, only_a, only_b = _match_detection_counts(
                    result_a.detections,
                    result_b.detections,
                    tolerance_hz=bin_width_hz
                )
                pairwise_results.append(
                    PairwiseFrameComparison(
                        dataset_id=dataset.metadata.dataset_id,
                        repetition=repetition,
                        frame_index=replay_frame.frame_index,
                        detector_a=detector_a.name,
                        detector_b=detector_b.name,
                        detector_a_count=len(
                            result_a.detections
                        ),
                        detector_b_count=len(
                            result_b.detections
                        ),
                        matched_count=matched,
                        detector_a_only_count=only_a,
                        detector_b_only_count=only_b
                    )
                )

    return {
        "frame_results": tuple(frame_results),
        "thresholds": {
            detector: np.asarray(values)
            for detector, values in thresholds.items()
        },
        "pairwise_results": tuple(pairwise_results),
        "consistency": consistency,
        "repetitions": repetitions,
        "matching_tolerance_hz": float(bin_width_hz)
    }


def _result_payload(result):
    payload = asdict(result)
    payload["detections"] = [
        asdict(detection)
        for detection in result.detections
    ]
    return payload


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


def _write_csv(path, rows):
    rows = list(rows)

    if not rows:
        return

    with path.open(
            "w",
            newline="",
            encoding="utf-8"
    ) as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=list(rows[0])
        )
        writer.writeheader()
        writer.writerows(rows)


def write_comparison_reports(
        dataset,
        evaluation,
        output_root,
        *,
        force=False
):
    """Write reports separately from the immutable source dataset."""

    output_root = Path(output_root)
    report_directory = (
        output_root
        / dataset.metadata.dataset_id
    )

    if report_directory.exists():
        if not force:
            raise FileExistsError(
                "Comparison report already exists: "
                f"{report_directory}"
            )

        shutil.rmtree(
            report_directory
        )

    report_directory.mkdir(
        parents=True
    )

    frame_results = evaluation["frame_results"]
    detector_names = sorted(
        {
            result.detector
            for result in frame_results
        }
    )

    detection_rows = []

    for result in frame_results:
        if result.detections:
            for detection_index, detection in enumerate(
                    result.detections
            ):
                detection_rows.append(
                    {
                        "dataset_id": result.dataset_id,
                        "detector": result.detector,
                        "repetition": result.repetition,
                        "frame_index": result.frame_index,
                        "detection_index": detection_index,
                        "frequency_mhz": detection.frequency_mhz,
                        "power_db": detection.power_db,
                        "bandwidth_khz": detection.bandwidth_khz,
                        "runtime_ms": result.runtime_ms
                    }
                )
        else:
            detection_rows.append(
                {
                    "dataset_id": result.dataset_id,
                    "detector": result.detector,
                    "repetition": result.repetition,
                    "frame_index": result.frame_index,
                    "detection_index": "",
                    "frequency_mhz": "",
                    "power_db": "",
                    "bandwidth_khz": "",
                    "runtime_ms": result.runtime_ms
                }
            )

    _write_csv(
        report_directory / "detections.csv",
        detection_rows
    )

    pairwise_payloads = [
        asdict(result)
        for result in evaluation["pairwise_results"]
    ]
    _write_csv(
        report_directory / "pairwise_comparison.csv",
        pairwise_payloads
    )

    detector_summaries = {}

    for detector_name in detector_names:
        detector_results = [
            result
            for result in frame_results
            if result.detector == detector_name
        ]
        runtime_values = np.asarray(
            [
                result.runtime_ms
                for result in detector_results
            ],
            dtype=float
        )
        detection_counts = np.asarray(
            [
                len(result.detections)
                for result in detector_results
            ],
            dtype=float
        )
        threshold_filename = (
            f"{detector_name}_thresholds.npz"
        )

        np.savez_compressed(
            report_directory / threshold_filename,
            thresholds=evaluation["thresholds"][detector_name]
        )

        detector_summary = {
            "detector": detector_name,
            "dataset_id": dataset.metadata.dataset_id,
            "frame_evaluations": len(detector_results),
            "mean_detection_count": float(
                np.mean(detection_counts)
            ),
            "mean_runtime_ms": float(
                np.mean(runtime_values)
            ),
            "median_runtime_ms": float(
                np.median(runtime_values)
            ),
            "maximum_runtime_ms": float(
                np.max(runtime_values)
            ),
            "repeated_run_consistent": evaluation[
                "consistency"
            ][detector_name],
            "threshold_array_file": threshold_filename,
            "frames": [
                _result_payload(result)
                for result in detector_results
            ]
        }
        detector_summaries[detector_name] = detector_summary
        _write_json(
            report_directory
            / f"{detector_name}_results.json",
            detector_summary
        )

    combined_report = {
        "dataset": dataset.metadata.to_dict(),
        "repetitions": evaluation["repetitions"],
        "matching_tolerance_hz": evaluation[
            "matching_tolerance_hz"
        ],
        "ground_truth_available": False,
        "interpretation_boundary": (
            "Detector agreement is not ground truth. This report does "
            "not calculate accuracy, probability of detection, or "
            "false-alarm probability and does not select a winner."
        ),
        "detectors": detector_summaries,
        "pairwise_frames": pairwise_payloads
    }
    _write_json(
        report_directory / "comparison.json",
        combined_report
    )

    summary_lines = [
        "SPECTRA REAL-RF DETECTOR COMPARISON",
        "",
        f"Dataset: {dataset.metadata.dataset_id}",
        f"Scenario: {dataset.metadata.scenario}",
        (
            "Frames: "
            f"{dataset.metadata.frame_count} "
            f"({evaluation['repetitions']} replay repetitions)"
        ),
        "",
        "DETECTOR OBSERVATIONS"
    ]

    for detector_name in detector_names:
        summary = detector_summaries[detector_name]
        summary_lines.extend(
            [
                (
                    f"- {detector_name}: mean detections "
                    f"{summary['mean_detection_count']:.3f}; "
                    f"mean runtime "
                    f"{summary['mean_runtime_ms']:.3f} ms; "
                    "repeated-run consistency "
                    f"{summary['repeated_run_consistent']}"
                )
            ]
        )

    summary_lines.extend(
        [
            "",
            "INTERPRETATION BOUNDARY",
            combined_report["interpretation_boundary"],
            ""
        ]
    )
    (
        report_directory
        / "summary.txt"
    ).write_text(
        "\n".join(summary_lines),
        encoding="utf-8"
    )

    return report_directory


def compare_dataset(
        dataset_directory,
        *,
        output_root=DEFAULT_REPORT_ROOT,
        detectors=None,
        repetitions=2,
        force=False
):
    dataset = load_dataset(dataset_directory)
    evaluation = evaluate_dataset(
        dataset,
        detectors=detectors,
        repetitions=repetitions
    )
    return write_comparison_reports(
        dataset,
        evaluation,
        output_root,
        force=force
    )


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Replay one immutable real-RF dataset through the "
            "standalone Adaptive and OS-CFAR detector adapters."
        )
    )
    parser.add_argument(
        "dataset_directory",
        type=Path
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_REPORT_ROOT
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=2
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Remove and regenerate an existing report directory."
        )
    )
    return parser


def main(argv=None):
    arguments = build_argument_parser().parse_args(argv)

    try:
        report_directory = compare_dataset(
            arguments.dataset_directory,
            output_root=arguments.output_root,
            repetitions=arguments.repetitions,
            force=arguments.force
        )
    except FileExistsError as error:
        _, _, report_path = str(error).partition(
            ": "
        )
        print(
            "Comparison reports already exist:",
            file=sys.stderr
        )
        print(
            f"\n{report_path}\n",
            file=sys.stderr
        )
        print(
            "Use:\n\n"
            "python3 -m VALIDATION.real_rf.comparison "
            f"{arguments.dataset_directory} --force\n\n"
            "to overwrite the existing reports.",
            file=sys.stderr
        )
        return 1
    except FileNotFoundError:
        print(
            f"Dataset not found: {arguments.dataset_directory}",
            file=sys.stderr
        )
        return 1
    except PermissionError as error:
        print(
            "Permission denied while preparing comparison reports: "
            f"{error}",
            file=sys.stderr
        )
        return 1
    except OSError as error:
        print(
            "Unable to prepare comparison reports: "
            f"{error}",
            file=sys.stderr
        )
        return 1
    except (TypeError, ValueError) as error:
        print(
            f"Invalid comparison input: {error}",
            file=sys.stderr
        )
        return 1

    print("REAL-RF DETECTOR COMPARISON COMPLETE")

    if arguments.force:
        print(
            "Force mode: existing reports were replaced if present."
        )

    print(f"Reports: {report_directory}")
    print("No detector winner was selected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
