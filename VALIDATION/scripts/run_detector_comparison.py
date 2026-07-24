"""Run the frozen Phase 4 adaptive-versus-OS-CFAR comparison."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    "/tmp/codex-matplotlib"
)

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(REPOSITORY_ROOT)
    )

from SDR.os_cfar import OSCFARConfig
from UTILS.config import NUM_SAMPLES, SAMPLE_RATE
from VALIDATION.detector_evaluation import (
    REQUIRED_SCENARIOS,
    build_detector_adapters,
    build_phase3_trials,
    evaluate_trial
)


VALIDATION_ID = "DE-CMP-01"
CONFIGURATION_ID = "CFG-C01"
BASE_SEED = 3_104_204
TRIALS_PER_SCENARIO = 100
MATCH_TOLERANCE_BINS = 1.0
WARMUP_TRIALS_PER_DETECTOR = 5
LIVE_RUNTIME_LIMIT_MS = 100.0

OS_CFAR_CONFIG = OSCFARConfig(
    reference_cells=32,
    guard_cells=8,
    rank=48,
    threshold_scale=4.0,
    minimum_peak_distance_khz=75.0,
    maximum_peaks=3,
    bandwidth_drop_db=15.0
)

RAW_FIELDS = (
    "validation_id",
    "configuration_id",
    "timestamp",
    "detector",
    "scenario",
    "trial_index",
    "random_seed",
    "sample_rate_hz",
    "fft_size",
    "bin_spacing_hz",
    "expected_count",
    "detected_count",
    "true_positive_count",
    "false_positive_count",
    "false_negative_count",
    "frame_has_false_alarm",
    "frequency_errors_hz",
    "runtime_ms",
    "finite_threshold_median_db"
)

SUMMARY_FIELDS = (
    "validation_id",
    "configuration_id",
    "detector",
    "scenario",
    "trial_count",
    "expected_count",
    "detected_count",
    "true_positive_count",
    "false_positive_count",
    "false_negative_count",
    "probability_of_detection",
    "pd_ci95_low",
    "pd_ci95_high",
    "frame_false_alarm_rate",
    "pfa_ci95_low",
    "pfa_ci95_high",
    "precision",
    "recall",
    "mean_runtime_ms",
    "median_runtime_ms",
    "p95_runtime_ms",
    "runtime_standard_deviation_ms",
    "runtime_coefficient_of_variation",
    "mean_detected_count",
    "detected_count_standard_deviation",
    "median_absolute_frequency_error_hz",
    "p95_absolute_frequency_error_hz",
    "frequency_error_standard_deviation_hz",
    "mean_finite_threshold_median_db"
)

GATE_FIELDS = (
    "gate_id",
    "engineering_requirement",
    "criterion",
    "adaptive_value",
    "os_cfar_value",
    "passed",
    "interpretation"
)


def wilson_interval(
        successes,
        observations,
        z_score=1.959963984540054
):
    if observations == 0:
        return (
            None,
            None
        )

    proportion = successes / observations
    denominator = 1.0 + z_score ** 2 / observations
    center = (
        proportion
        + z_score ** 2
        / (2.0 * observations)
    ) / denominator
    half_width = (
        z_score
        * np.sqrt(
            proportion
            * (1.0 - proportion)
            / observations
            + z_score ** 2
            / (4.0 * observations ** 2)
        )
        / denominator
    )

    return (
        float(
            max(
                0.0,
                center - half_width
            )
        ),
        float(
            min(
                1.0,
                center + half_width
            )
        )
    )


def run_comparison():
    trials = build_phase3_trials(
        trials_per_scenario=TRIALS_PER_SCENARIO,
        base_seed=BASE_SEED,
        sample_rate=float(SAMPLE_RATE),
        fft_size=int(NUM_SAMPLES)
    )

    detectors = build_detector_adapters(
        os_cfar_config=OS_CFAR_CONFIG
    )

    for detector in detectors:
        for trial in trials[
                :WARMUP_TRIALS_PER_DETECTOR
        ]:
            detector.callback(
                trial.power_db,
                trial.freqs_mhz
            )

    tolerance_hz = (
        float(SAMPLE_RATE)
        / int(NUM_SAMPLES)
        * MATCH_TOLERANCE_BINS
    )

    results = []

    for trial_offset, trial in enumerate(
            trials
    ):
        ordered_detectors = (
            detectors
            if trial_offset % 2 == 0
            else tuple(
                reversed(
                    detectors
                )
            )
        )

        for detector in ordered_detectors:
            results.append(
                evaluate_trial(
                    trial,
                    detector,
                    tolerance_hz=tolerance_hz
                )
            )

    return (
        trials,
        tuple(
            results
        )
    )


def build_raw_rows(
        results,
        timestamp
):
    bin_spacing_hz = (
        float(SAMPLE_RATE)
        / int(NUM_SAMPLES)
    )

    return [
        {
            "validation_id": VALIDATION_ID,
            "configuration_id": CONFIGURATION_ID,
            "timestamp": timestamp,
            "detector": result.detector,
            "scenario": result.scenario,
            "trial_index": result.trial_index,
            "random_seed": result.random_seed,
            "sample_rate_hz": float(
                SAMPLE_RATE
            ),
            "fft_size": int(
                NUM_SAMPLES
            ),
            "bin_spacing_hz": bin_spacing_hz,
            "expected_count": result.expected_count,
            "detected_count": result.detected_count,
            "true_positive_count": (
                result.true_positive_count
            ),
            "false_positive_count": (
                result.false_positive_count
            ),
            "false_negative_count": (
                result.false_negative_count
            ),
            "frame_has_false_alarm": str(
                result.frame_has_false_alarm
            ).lower(),
            "frequency_errors_hz": (
                ";".join(
                    f"{error:.9f}"
                    for error in result.frequency_errors_hz
                )
                if result.frequency_errors_hz
                else "NA"
            ),
            "runtime_ms": result.runtime_ms,
            "finite_threshold_median_db": (
                result.finite_threshold_median_db
            )
        }
        for result in results
    ]


def summarize_results(
        results
):
    groups = defaultdict(
        list
    )

    for result in results:
        groups[
            (
                result.detector,
                result.scenario
            )
        ].append(
            result
        )

    rows = []

    for (
            detector,
            scenario
    ) in sorted(
            groups
    ):
        group = groups[
            (
                detector,
                scenario
            )
        ]

        expected_count = sum(
            result.expected_count
            for result in group
        )
        detected_count = sum(
            result.detected_count
            for result in group
        )
        true_positives = sum(
            result.true_positive_count
            for result in group
        )
        false_positives = sum(
            result.false_positive_count
            for result in group
        )
        false_negatives = sum(
            result.false_negative_count
            for result in group
        )
        false_alarm_frames = sum(
            result.frame_has_false_alarm
            for result in group
        )

        pd_low, pd_high = wilson_interval(
            true_positives,
            expected_count
        )
        pfa_low, pfa_high = wilson_interval(
            false_alarm_frames,
            len(group)
        )

        runtimes = np.asarray(
            [
                result.runtime_ms
                for result in group
            ],
            dtype=float
        )
        detected_counts = np.asarray(
            [
                result.detected_count
                for result in group
            ],
            dtype=float
        )
        errors = np.asarray(
            [
                error
                for result in group
                for error in result.frequency_errors_hz
            ],
            dtype=float
        )
        thresholds = np.asarray(
            [
                result.finite_threshold_median_db
                for result in group
            ],
            dtype=float
        )

        runtime_mean = float(
            np.mean(
                runtimes
            )
        )

        rows.append({
            "validation_id": VALIDATION_ID,
            "configuration_id": CONFIGURATION_ID,
            "detector": detector,
            "scenario": scenario,
            "trial_count": len(group),
            "expected_count": expected_count,
            "detected_count": detected_count,
            "true_positive_count": true_positives,
            "false_positive_count": false_positives,
            "false_negative_count": false_negatives,
            "probability_of_detection": (
                true_positives / expected_count
                if expected_count
                else "NA"
            ),
            "pd_ci95_low": (
                pd_low
                if pd_low is not None
                else "NA"
            ),
            "pd_ci95_high": (
                pd_high
                if pd_high is not None
                else "NA"
            ),
            "frame_false_alarm_rate": (
                false_alarm_frames
                / len(group)
            ),
            "pfa_ci95_low": pfa_low,
            "pfa_ci95_high": pfa_high,
            "precision": (
                true_positives
                / (
                    true_positives
                    + false_positives
                )
                if (
                    true_positives
                    + false_positives
                )
                else "NA"
            ),
            "recall": (
                true_positives
                / (
                    true_positives
                    + false_negatives
                )
                if (
                    true_positives
                    + false_negatives
                )
                else "NA"
            ),
            "mean_runtime_ms": runtime_mean,
            "median_runtime_ms": float(
                np.median(
                    runtimes
                )
            ),
            "p95_runtime_ms": float(
                np.percentile(
                    runtimes,
                    95
                )
            ),
            "runtime_standard_deviation_ms": float(
                np.std(
                    runtimes
                )
            ),
            "runtime_coefficient_of_variation": (
                float(
                    np.std(
                        runtimes
                    )
                    / runtime_mean
                )
                if runtime_mean > 0
                else 0.0
            ),
            "mean_detected_count": float(
                np.mean(
                    detected_counts
                )
            ),
            "detected_count_standard_deviation": float(
                np.std(
                    detected_counts
                )
            ),
            "median_absolute_frequency_error_hz": (
                float(
                    np.median(
                        np.abs(
                            errors
                        )
                    )
                )
                if len(errors)
                else "NA"
            ),
            "p95_absolute_frequency_error_hz": (
                float(
                    np.percentile(
                        np.abs(
                            errors
                        ),
                        95
                    )
                )
                if len(errors)
                else "NA"
            ),
            "frequency_error_standard_deviation_hz": (
                float(
                    np.std(
                        errors
                    )
                )
                if len(errors)
                else "NA"
            ),
            "mean_finite_threshold_median_db": float(
                np.mean(
                    thresholds
                )
            )
        })

    return rows


def _summary_lookup(
        summary_rows
):
    return {
        (
            row["detector"],
            row["scenario"]
        ): row
        for row in summary_rows
    }


def _numeric(
        row,
        field
):
    value = row[field]

    if value == "NA":
        raise ValueError(
            f"{field} is unavailable for "
            f"{row['detector']} / {row['scenario']}."
        )

    return float(
        value
    )


def evaluate_gates(
        summary_rows
):
    lookup = _summary_lookup(
        summary_rows
    )

    def metric(
            detector,
            scenario,
            field
    ):
        return _numeric(
            lookup[
                (
                    detector,
                    scenario
                )
            ],
            field
        )

    gates = []

    adaptive_noise = metric(
        "adaptive",
        "noise_only",
        "frame_false_alarm_rate"
    )
    os_noise = metric(
        "os_cfar",
        "noise_only",
        "frame_false_alarm_rate"
    )
    noise_limit = max(
        0.01,
        adaptive_noise * 0.50
    )

    gates.append({
        "gate_id": "G1",
        "engineering_requirement": (
            "Material noise-only false-alarm reduction"
        ),
        "criterion": (
            "OS-CFAR frame Pfa <= max(0.01, 50% of adaptive Pfa)"
        ),
        "adaptive_value": adaptive_noise,
        "os_cfar_value": os_noise,
        "passed": os_noise <= noise_limit,
        "interpretation": (
            "Tests whether OS-CFAR addresses the measured "
            "raw-specificity weakness."
        )
    })

    relative_gates = (
        (
            "G2",
            "Single-carrier sensitivity",
            "single_carrier",
            "probability_of_detection",
            0.05
        ),
        (
            "G3",
            "Weak carrier beside strong carrier",
            "weak_beside_strong",
            "recall",
            0.10
        ),
        (
            "G4",
            "Closely spaced carrier performance",
            "closely_spaced_carriers",
            "recall",
            0.05
        )
    )

    for (
            gate_id,
            requirement,
            scenario,
            field,
            allowed_loss
    ) in relative_gates:
        adaptive_value = metric(
            "adaptive",
            scenario,
            field
        )
        os_value = metric(
            "os_cfar",
            scenario,
            field
        )

        gates.append({
            "gate_id": gate_id,
            "engineering_requirement": requirement,
            "criterion": (
                f"OS-CFAR >= adaptive - {allowed_loss:.2f}"
            ),
            "adaptive_value": adaptive_value,
            "os_cfar_value": os_value,
            "passed": (
                os_value
                >= adaptive_value
                - allowed_loss
            ),
            "interpretation": (
                "Bounds the permitted sensitivity loss "
                "against the production baseline."
            )
        })

    robustness_scenarios = (
        "fft_edge",
        "multiple_carriers",
        "variable_noise_floor",
        "monte_carlo"
    )

    adaptive_robustness = float(
        np.mean([
            metric(
                "adaptive",
                scenario,
                "recall"
            )
            for scenario in robustness_scenarios
        ])
    )
    os_robustness = float(
        np.mean([
            metric(
                "os_cfar",
                scenario,
                "recall"
            )
            for scenario in robustness_scenarios
        ])
    )

    gates.append({
        "gate_id": "G5",
        "engineering_requirement": (
            "Robustness across non-ideal scenarios"
        ),
        "criterion": (
            "Mean OS-CFAR recall across edge, multiple, "
            "variable-floor, and Monte Carlo scenarios "
            ">= adaptive - 0.05"
        ),
        "adaptive_value": adaptive_robustness,
        "os_cfar_value": os_robustness,
        "passed": (
            os_robustness
            >= adaptive_robustness
            - 0.05
        ),
        "interpretation": (
            "Prevents selection based on one favorable scenario."
        )
    })

    adaptive_runtime = max(
        metric(
            "adaptive",
            scenario,
            "p95_runtime_ms"
        )
        for scenario in REQUIRED_SCENARIOS
    )
    os_runtime = max(
        metric(
            "os_cfar",
            scenario,
            "p95_runtime_ms"
        )
        for scenario in REQUIRED_SCENARIOS
    )

    gates.append({
        "gate_id": "G6",
        "engineering_requirement": (
            "Runtime compatible with the live processing interval"
        ),
        "criterion": (
            f"Worst scenario p95 runtime <= "
            f"{LIVE_RUNTIME_LIMIT_MS:.1f} ms"
        ),
        "adaptive_value": adaptive_runtime,
        "os_cfar_value": os_runtime,
        "passed": os_runtime <= LIVE_RUNTIME_LIMIT_MS,
        "interpretation": (
            "Runtime is measured after warmup and excludes FFT "
            "generation and file output."
        )
    })

    return [
        {
            **gate,
            "passed": str(
                gate["passed"]
            ).lower()
        }
        for gate in gates
    ]


def write_csv(
        path,
        rows,
        fieldnames
):
    with path.open(
            "w",
            newline="",
            encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(
            rows
        )


def plot_detection_performance(
        path,
        summary_rows
):
    lookup = _summary_lookup(
        summary_rows
    )
    scenarios = [
        scenario
        for scenario in REQUIRED_SCENARIOS
        if scenario != "noise_only"
    ]
    labels = [
        scenario.replace(
            "_",
            " "
        )
        for scenario in scenarios
    ]
    positions = np.arange(
        len(scenarios)
    )
    width = 0.36

    figure, axis = plt.subplots(
        figsize=(
            12,
            6
        )
    )

    for offset, detector, color in (
            (
                -width / 2,
                "adaptive",
                "#00A7C7"
            ),
            (
                width / 2,
                "os_cfar",
                "#7C5CFC"
            )
    ):
        values = [
            _numeric(
                lookup[
                    (
                        detector,
                        scenario
                    )
                ],
                "recall"
            )
            for scenario in scenarios
        ]

        axis.bar(
            positions + offset,
            values,
            width,
            label=detector.replace(
                "_",
                " "
            ).title(),
            color=color
        )

    axis.set(
        title=(
            "Phase 4 Detection Recall on Identical Synthetic Inputs"
        ),
        ylabel="Recall",
        ylim=(
            0,
            1.05
        ),
        xticks=positions,
        xticklabels=labels
    )
    axis.tick_params(
        axis="x",
        rotation=25
    )
    axis.grid(
        axis="y",
        alpha=0.25
    )
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=180
    )
    plt.close(
        figure
    )


def plot_false_alarm_comparison(
        path,
        summary_rows
):
    lookup = _summary_lookup(
        summary_rows
    )
    scenarios = list(
        REQUIRED_SCENARIOS
    )
    labels = [
        scenario.replace(
            "_",
            " "
        )
        for scenario in scenarios
    ]
    positions = np.arange(
        len(scenarios)
    )
    width = 0.36

    figure, axis = plt.subplots(
        figsize=(
            12,
            6
        )
    )

    for offset, detector, color in (
            (
                -width / 2,
                "adaptive",
                "#00A7C7"
            ),
            (
                width / 2,
                "os_cfar",
                "#7C5CFC"
            )
    ):
        values = [
            _numeric(
                lookup[
                    (
                        detector,
                        scenario
                    )
                ],
                "frame_false_alarm_rate"
            )
            for scenario in scenarios
        ]

        axis.bar(
            positions + offset,
            values,
            width,
            label=detector.replace(
                "_",
                " "
            ).title(),
            color=color
        )

    axis.set(
        title=(
            "Phase 4 Frames Containing Unmatched Detector Responses"
        ),
        ylabel="Frame false-alarm rate",
        ylim=(
            0,
            1.05
        ),
        xticks=positions,
        xticklabels=labels
    )
    axis.tick_params(
        axis="x",
        rotation=25
    )
    axis.grid(
        axis="y",
        alpha=0.25
    )
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=180
    )
    plt.close(
        figure
    )


def plot_runtime(
        path,
        results
):
    adaptive = [
        result.runtime_ms
        for result in results
        if result.detector == "adaptive"
    ]
    os_cfar = [
        result.runtime_ms
        for result in results
        if result.detector == "os_cfar"
    ]

    figure, axis = plt.subplots(
        figsize=(
            8,
            6
        )
    )
    boxes = axis.boxplot(
        (
            adaptive,
            os_cfar
        ),
        tick_labels=(
            "Adaptive",
            "OS-CFAR"
        ),
        patch_artist=True,
        showfliers=False
    )

    for patch, color in zip(
            boxes["boxes"],
            (
                "#00A7C7",
                "#7C5CFC"
            )
    ):
        patch.set_facecolor(
            color
        )
        patch.set_alpha(
            0.8
        )

    axis.axhline(
        LIVE_RUNTIME_LIMIT_MS,
        color="#E64980",
        linestyle="--",
        label=(
            f"{LIVE_RUNTIME_LIMIT_MS:.0f} ms live interval"
        )
    )
    axis.set(
        title="Phase 4 Detector Runtime Distribution",
        ylabel="Runtime per FFT frame (ms)"
    )
    axis.grid(
        axis="y",
        alpha=0.25
    )
    axis.legend()
    figure.tight_layout()
    figure.savefig(
        path,
        dpi=180
    )
    plt.close(
        figure
    )


def write_protocol(
        path
):
    payload = {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "protocol_status": (
            "Frozen before comparative execution"
        ),
        "sample_rate_hz": float(
            SAMPLE_RATE
        ),
        "fft_size": int(
            NUM_SAMPLES
        ),
        "bin_spacing_hz": (
            float(SAMPLE_RATE)
            / int(NUM_SAMPLES)
        ),
        "base_seed": BASE_SEED,
        "trials_per_scenario": (
            TRIALS_PER_SCENARIO
        ),
        "scenarios": REQUIRED_SCENARIOS,
        "matching_tolerance_bins": (
            MATCH_TOLERANCE_BINS
        ),
        "warmup_trials_per_detector": (
            WARMUP_TRIALS_PER_DETECTOR
        ),
        "runtime_limit_ms": (
            LIVE_RUNTIME_LIMIT_MS
        ),
        "adaptive_configuration": (
            "Production SDR/detection.py unchanged"
        ),
        "os_cfar_configuration": {
            "reference_cells_per_side": (
                OS_CFAR_CONFIG.reference_cells
            ),
            "guard_cells_per_side": (
                OS_CFAR_CONFIG.guard_cells
            ),
            "rank_one_based": (
                OS_CFAR_CONFIG.rank
            ),
            "threshold_scale_linear": (
                OS_CFAR_CONFIG.threshold_scale
            ),
            "minimum_peak_distance_khz": (
                OS_CFAR_CONFIG.minimum_peak_distance_khz
            ),
            "maximum_peaks": (
                OS_CFAR_CONFIG.maximum_peaks
            ),
            "bandwidth_drop_db": (
                OS_CFAR_CONFIG.bandwidth_drop_db
            )
        },
        "decision_boundary": (
            "Synthetic eligibility for Phase 5 hardware validation only; "
            "not production selection"
        )
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2
        )
        + "\n",
        encoding="utf-8"
    )


def write_engineering_summary(
        path,
        summary_rows,
        gates
):
    lookup = _summary_lookup(
        summary_rows
    )
    passed_count = sum(
        gate["passed"] == "true"
        for gate in gates
    )
    all_passed = passed_count == len(
        gates
    )

    lines = [
        "# SPECTRA Phase 4 Detector Comparison",
        "",
        f"**Validation:** {VALIDATION_ID} / {CONFIGURATION_ID}",
        "",
        "## Outcome",
        "",
        (
            f"The experimental OS-CFAR detector passed "
            f"{passed_count} of {len(gates)} predeclared synthetic gates."
        ),
        "",
        (
            "**Phase 5 status:** "
            + (
                "Eligible for hardware comparison."
                if all_passed
                else (
                    "Synthetic decision gates are not all satisfied. "
                    "Do not replace the production detector."
                )
            )
        ),
        "",
        "This outcome is not a production-detector selection. Hardware evidence "
        "and full regression review remain mandatory.",
        "",
        "## Frozen Method",
        "",
        f"- {TRIALS_PER_SCENARIO} trials for each of "
        f"{len(REQUIRED_SCENARIOS)} scenarios",
        f"- {TRIALS_PER_SCENARIO * len(REQUIRED_SCENARIOS)} shared spectra",
        "- Both detectors received the exact same read-only FFT arrays",
        f"- Base seed: {BASE_SEED}",
        f"- Match tolerance: {MATCH_TOLERANCE_BINS:.1f} FFT bin",
        f"- {WARMUP_TRIALS_PER_DETECTOR} warmup calls per detector",
        "- Detector execution order alternated by trial",
        "",
        "## Decision Gates",
        "",
        "| Gate | Requirement | Adaptive | OS-CFAR | Result |",
        "| --- | --- | ---: | ---: | --- |"
    ]

    for gate in gates:
        lines.append(
            f"| {gate['gate_id']} | "
            f"{gate['engineering_requirement']} | "
            f"{float(gate['adaptive_value']):.4f} | "
            f"{float(gate['os_cfar_value']):.4f} | "
            f"{'PASS' if gate['passed'] == 'true' else 'FAIL'} |"
        )

    lines.extend([
        "",
        "## Scenario Metrics",
        "",
        "| Scenario | Detector | Pd | Pfa | Precision | Recall | p95 runtime (ms) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |"
    ])

    for scenario in REQUIRED_SCENARIOS:
        for detector in (
                "adaptive",
                "os_cfar"
        ):
            row = lookup[
                (
                    detector,
                    scenario
                )
            ]

            def format_metric(
                    field
            ):
                value = row[field]
                return (
                    "NA"
                    if value == "NA"
                    else f"{float(value):.4f}"
                )

            lines.append(
                f"| {scenario.replace('_', ' ')} | "
                f"{detector} | "
                f"{format_metric('probability_of_detection')} | "
                f"{format_metric('frame_false_alarm_rate')} | "
                f"{format_metric('precision')} | "
                f"{format_metric('recall')} | "
                f"{float(row['p95_runtime_ms']):.3f} |"
            )

    lines.extend([
        "",
        "## Engineering Limitations",
        "",
        "- Inputs are deterministic synthetic unmodulated tones and noise.",
        "- Relative FFT levels are not calibrated dBm.",
        "- Raw peak outputs are compared before temporal confirmation.",
        "- The three-peak cap remains part of both public detector interfaces.",
        "- Runtime results apply only to this development computer and software "
        "environment.",
        "- No claim about live RF performance is made by Phase 4.",
        ""
    ])

    path.write_text(
        "\n".join(
            lines
        ),
        encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True
    )
    args = parser.parse_args()
    args.output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    prefix = (
        f"{VALIDATION_ID}_{CONFIGURATION_ID}"
    )
    timestamp = datetime.now(
        timezone.utc
    ).astimezone().isoformat()

    write_protocol(
        args.output_dir
        / f"{prefix}_frozen_protocol.json"
    )

    _, results = run_comparison()
    raw_rows = build_raw_rows(
        results,
        timestamp
    )
    summary_rows = summarize_results(
        results
    )
    gates = evaluate_gates(
        summary_rows
    )

    write_csv(
        args.output_dir
        / f"{prefix}_raw_trials.csv",
        raw_rows,
        RAW_FIELDS
    )
    write_csv(
        args.output_dir
        / f"{prefix}_scenario_summary.csv",
        summary_rows,
        SUMMARY_FIELDS
    )
    write_csv(
        args.output_dir
        / f"{prefix}_decision_gates.csv",
        gates,
        GATE_FIELDS
    )

    plot_detection_performance(
        args.output_dir
        / f"{prefix}_detection_recall.png",
        summary_rows
    )
    plot_false_alarm_comparison(
        args.output_dir
        / f"{prefix}_false_alarm_rate.png",
        summary_rows
    )
    plot_runtime(
        args.output_dir
        / f"{prefix}_runtime_distribution.png",
        results
    )
    write_engineering_summary(
        args.output_dir
        / f"{prefix}_engineering_summary.md",
        summary_rows,
        gates
    )

    payload = {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "shared_spectrum_count": (
            TRIALS_PER_SCENARIO
            * len(REQUIRED_SCENARIOS)
        ),
        "detector_evaluation_count": len(
            results
        ),
        "passed_gate_count": sum(
            gate["passed"] == "true"
            for gate in gates
        ),
        "gate_count": len(
            gates
        ),
        "all_synthetic_gates_passed": all(
            gate["passed"] == "true"
            for gate in gates
        )
    }

    (
        args.output_dir
        / f"{prefix}_result.json"
    ).write_text(
        json.dumps(
            payload,
            indent=2
        )
        + "\n",
        encoding="utf-8"
    )

    print(
        json.dumps(
            payload,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
