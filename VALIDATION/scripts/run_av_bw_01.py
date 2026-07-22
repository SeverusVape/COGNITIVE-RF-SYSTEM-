"""Run AV-BW-01 bandwidth-heuristic validation without SDR hardware."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/codex-matplotlib")

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from SDR.detection import detect_peaks
from UTILS.config import NUM_SAMPLES, SAMPLE_RATE


VALIDATION_ID = "AV-BW-01"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 4_201_326
CONTROLLED_WIDTHS_KHZ = (5.0, 10.0, 25.0, 50.0, 100.0, 200.0, 400.0)
SHAPES = ("gaussian", "flat_top_cosine_edge")
TRIALS_PER_CONDITION = 50
PEAK_LEVEL_DB = 45.0
BASELINE_LEVEL_DB = 5.0
BASELINE_NOISE_STD_DB = 0.20
WIDTH_TOLERANCE_KHZ = 1.0

TRIAL_FIELDS = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "sample_rate_hz", "fft_size", "bin_spacing_hz",
    "shape", "controlled_minus_15db_width_khz", "center_frequency_hz",
    "peak_level_db", "baseline_level_db", "returned_peak_count",
    "detected_frequency_hz", "frequency_error_hz",
    "estimated_minus_15db_width_khz", "width_error_khz",
    "absolute_width_error_khz", "relative_width_error_percent",
    "detected", "valid", "notes",
)


def build_controlled_spectrum(
        rng: np.random.Generator,
        frequency_axis_hz: np.ndarray,
        center_hz: float,
        width_khz: float,
        shape: str,
) -> np.ndarray:
    """Return a spectrum whose analytical -15 dB width is width_khz."""
    offset_hz = np.abs(frequency_axis_hz - center_hz)
    half_width_hz = width_khz * 500.0
    if shape == "gaussian":
        # The response is exactly peak-15 dB at +/- half_width_hz.
        response_db = PEAK_LEVEL_DB - 15.0 * (offset_hz / half_width_hz) ** 2
    elif shape == "flat_top_cosine_edge":
        # Flat central 50%, followed by a smooth cosine-like roll-off in dB.
        flat_half_hz = 0.5 * half_width_hz
        normalized_edge = np.clip(
            (offset_hz - flat_half_hz) / (half_width_hz - flat_half_hz),
            0.0,
            1.0,
        )
        response_db = PEAK_LEVEL_DB - 15.0 * (1.0 - np.cos(np.pi * normalized_edge)) / 2.0
        beyond = offset_hz > half_width_hz
        response_db[beyond] = PEAK_LEVEL_DB - 15.0 - (
            (offset_hz[beyond] - half_width_hz) / max(half_width_hz, 1.0)
        ) * 35.0
    else:
        raise ValueError(f"Unsupported shape: {shape}")

    noise = rng.normal(0.0, BASELINE_NOISE_STD_DB, len(frequency_axis_hz))
    baseline = BASELINE_LEVEL_DB + noise
    return np.maximum(response_db, baseline)


def run_trials() -> list[dict[str, object]]:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    bin_spacing_hz = sample_rate / fft_size
    frequency_axis_hz = np.fft.fftshift(
        np.fft.fftfreq(fft_size, d=1.0 / sample_rate)
    )
    frequency_axis_mhz = frequency_axis_hz / 1e6
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    rows: list[dict[str, object]] = []
    trial_id = 0

    for shape in SHAPES:
        for width_khz in CONTROLLED_WIDTHS_KHZ:
            for _ in range(TRIALS_PER_CONDITION):
                seed = BASE_SEED + trial_id
                rng = np.random.default_rng(seed)
                margin_hz = width_khz * 500.0 + 100_000.0
                center_hz = float(rng.uniform(
                    frequency_axis_hz[0] + margin_hz,
                    frequency_axis_hz[-1] - margin_hz,
                ))
                power_db = build_controlled_spectrum(
                    rng, frequency_axis_hz, center_hz, width_khz, shape
                )
                peaks, _ = detect_peaks(power_db, frequency_axis_mhz)
                nearest = min(
                    peaks,
                    key=lambda peak: abs(float(peak[0]) * 1e6 - center_hz),
                    default=None,
                )
                detected = nearest is not None and abs(
                    float(nearest[0]) * 1e6 - center_hz
                ) <= bin_spacing_hz
                measured = float(nearest[2]) if detected else "NA"
                error = measured - width_khz if detected else "NA"
                rows.append({
                    "validation_id": VALIDATION_ID,
                    "configuration_id": CONFIGURATION_ID,
                    "trial_id": trial_id + 1,
                    "timestamp": timestamp,
                    "random_seed": seed,
                    "sample_rate_hz": sample_rate,
                    "fft_size": fft_size,
                    "bin_spacing_hz": bin_spacing_hz,
                    "shape": shape,
                    "controlled_minus_15db_width_khz": width_khz,
                    "center_frequency_hz": center_hz,
                    "peak_level_db": PEAK_LEVEL_DB,
                    "baseline_level_db": BASELINE_LEVEL_DB,
                    "returned_peak_count": len(peaks),
                    "detected_frequency_hz": float(nearest[0]) * 1e6 if detected else "NA",
                    "frequency_error_hz": (
                        float(nearest[0]) * 1e6 - center_hz if detected else "NA"
                    ),
                    "estimated_minus_15db_width_khz": measured,
                    "width_error_khz": error,
                    "absolute_width_error_khz": abs(error) if detected else "NA",
                    "relative_width_error_percent": (
                        100.0 * error / width_khz if detected else "NA"
                    ),
                    "detected": str(detected).lower(),
                    "valid": "true",
                    "notes": "Controlled analytical -15 dB width; unchanged detector heuristic",
                })
                trial_id += 1
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for shape in SHAPES:
        for width_khz in CONTROLLED_WIDTHS_KHZ:
            group = [
                row for row in rows
                if row["shape"] == shape
                and float(row["controlled_minus_15db_width_khz"]) == width_khz
            ]
            detected = [row for row in group if row["detected"] == "true"]
            estimates = np.asarray([
                float(row["estimated_minus_15db_width_khz"]) for row in detected
            ])
            errors = estimates - width_khz
            has_estimates = len(estimates) > 0
            summaries.append({
                "shape": shape,
                "controlled_minus_15db_width_khz": width_khz,
                "trial_count": len(group),
                "detected_count": len(detected),
                "detection_probability": len(detected) / len(group),
                "mean_estimated_width_khz": (
                    float(np.mean(estimates)) if has_estimates else "NA"
                ),
                "standard_deviation_khz": (
                    float(np.std(estimates, ddof=1)) if len(estimates) > 1 else 0.0
                ) if has_estimates else "NA",
                "mean_bias_khz": float(np.mean(errors)) if has_estimates else "NA",
                "mean_absolute_error_khz": (
                    float(np.mean(np.abs(errors))) if has_estimates else "NA"
                ),
                "p95_absolute_error_khz": (
                    float(np.percentile(np.abs(errors), 95)) if has_estimates else "NA"
                ),
                "maximum_absolute_error_khz": (
                    float(np.max(np.abs(errors))) if has_estimates else "NA"
                ),
            })
    return summaries


def build_result(summaries: list[dict[str, object]]) -> dict[str, object]:
    measured = [row for row in summaries if row["p95_absolute_error_khz"] != "NA"]
    maximum_p95 = max(float(row["p95_absolute_error_khz"]) for row in measured)
    maximum_std = max(float(row["standard_deviation_khz"]) for row in measured)
    minimum_detection = min(float(row["detection_probability"]) for row in summaries)
    passed = (
        minimum_detection == 1.0
        and maximum_p95 <= WIDTH_TOLERANCE_KHZ
        and maximum_std <= WIDTH_TOLERANCE_KHZ
    )
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": sum(int(row["trial_count"]) for row in summaries),
        "shape_count": len(SHAPES),
        "width_count": len(CONTROLLED_WIDTHS_KHZ),
        "trials_per_condition": TRIALS_PER_CONDITION,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "bin_spacing_khz": float(SAMPLE_RATE) / int(NUM_SAMPLES) / 1000.0,
        "acceptance_tolerance_khz": WIDTH_TOLERANCE_KHZ,
        "minimum_detection_probability": minimum_detection,
        "maximum_p95_absolute_error_khz": maximum_p95,
        "maximum_repeatability_standard_deviation_khz": maximum_std,
        "result": "PASS" if passed else "FAIL",
        "claim_scope": "Repeatability and bias of the existing minus-15 dB bandwidth heuristic on controlled synthetic spectral shapes",
        "excluded_claims": "Regulatory occupied bandwidth, modulated-signal bandwidth, hardware bandwidth, and calibrated RF measurements",
    }


def write_csv(path: Path, rows: list[dict[str, object]], fields) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_accuracy(path: Path, summaries: list[dict[str, object]]) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    colors = ("#00AEEA", "#7C5CFC")
    for shape, color in zip(SHAPES, colors):
        group = [
            row for row in summaries
            if row["shape"] == shape and row["mean_estimated_width_khz"] != "NA"
        ]
        axis.errorbar(
            [float(row["controlled_minus_15db_width_khz"]) for row in group],
            [float(row["mean_estimated_width_khz"]) for row in group],
            yerr=[float(row["standard_deviation_khz"]) for row in group],
            marker="o", linewidth=2, capsize=4, color=color,
            label=shape.replace("_", " ").title(),
        )
    limits = (0.0, max(CONTROLLED_WIDTHS_KHZ) * 1.05)
    axis.plot(limits, limits, "--", color="#FFBF00", label="Ideal reference")
    axis.set(
        title="Estimated −15 dB Width vs Controlled Spectral Width",
        xlabel="Controlled −15 dB width (kHz)",
        ylabel="Estimated −15 dB width (kHz)",
        xlim=limits, ylim=limits,
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def plot_bias(path: Path, summaries: list[dict[str, object]]) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    colors = ("#00AEEA", "#7C5CFC")
    for shape, color in zip(SHAPES, colors):
        group = [
            row for row in summaries
            if row["shape"] == shape and row["mean_bias_khz"] != "NA"
        ]
        axis.plot(
            [float(row["controlled_minus_15db_width_khz"]) for row in group],
            [float(row["mean_bias_khz"]) for row in group],
            "o-", linewidth=2, color=color,
            label=shape.replace("_", " ").title(),
        )
    axis.axhline(0.0, color="#64748B", linestyle="--")
    axis.set(
        title="Bandwidth-Heuristic Bias",
        xlabel="Controlled −15 dB width (kHz)", ylabel="Mean error (kHz)",
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="best")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def plot_examples(path: Path) -> None:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    frequency_axis_hz = np.fft.fftshift(np.fft.fftfreq(fft_size, d=1.0 / sample_rate))
    frequency_axis_mhz = frequency_axis_hz / 1e6
    figure, axes = plt.subplots(1, 2, figsize=(10.0, 4.6))
    for axis, shape, seed in zip(axes, SHAPES, (BASE_SEED + 90_001, BASE_SEED + 90_002)):
        rng = np.random.default_rng(seed)
        center_hz = 80_125.0
        controlled_width = 100.0
        power_db = build_controlled_spectrum(
            rng, frequency_axis_hz, center_hz, controlled_width, shape
        )
        peaks, threshold = detect_peaks(power_db, frequency_axis_mhz)
        nearest = min(peaks, key=lambda peak: abs(float(peak[0]) * 1e6 - center_hz))
        mask = np.abs(frequency_axis_hz - center_hz) <= 110_000.0
        axis.plot((frequency_axis_hz[mask] - center_hz) / 1000.0, power_db[mask], color="#A900F5")
        axis.plot((frequency_axis_hz[mask] - center_hz) / 1000.0, threshold[mask], color="#F59E0B", label="Detection threshold")
        axis.axhline(float(nearest[1]) - 15.0, color="#00B894", linestyle="--", label="Peak −15 dB")
        axis.set(
            title=f"{shape.replace('_', ' ').title()}\nMeasured {float(nearest[2]):.2f} kHz",
            xlabel="Offset from center (kHz)", ylabel="Relative level (dB)",
        )
        axis.grid(True, alpha=0.22)
        axis.legend(loc="lower center")
    figure.suptitle("Controlled 100 kHz −15 dB Width Examples")
    figure.tight_layout(rect=(0, 0, 1, 0.93))
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{VALIDATION_ID}_{CONFIGURATION_ID}"
    rows = run_trials()
    summaries = summarize(rows)
    result = build_result(summaries)
    write_csv(args.output_dir / f"{prefix}_bandwidth_trials.csv", rows, TRIAL_FIELDS)
    write_csv(args.output_dir / f"{prefix}_bandwidth_summary.csv", summaries, summaries[0].keys())
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    plot_accuracy(args.output_dir / f"{prefix}_estimated_vs_controlled.png", summaries)
    plot_bias(args.output_dir / f"{prefix}_bias.png", summaries)
    plot_examples(args.output_dir / f"{prefix}_shape_examples.png")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
