"""Run AV-NF-01 against the existing adaptive local-noise-floor code."""

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

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SDR.detection import build_local_detection_threshold, estimate_local_noise_floor
from UTILS.config import NUM_SAMPLES, SAMPLE_RATE

VALIDATION_ID = "AV-NF-01"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_102_028
CONDITIONS = ("flat", "curved", "stepped")
REPETITIONS = 100
WINDOW_KHZ = 250.0
PERCENTILE = 30.0
MARGIN_DB = 10.0
NOISE_SIGMA_DB = 1.5
PEAK_COUNT = 7
PEAK_WIDTH_BINS = 3
MAE_LIMIT_DB = 1.25
P95_TRIAL_MAE_LIMIT_DB = 1.50
PEAK_EFFECT_P95_LIMIT_DB = 0.25

FIELDS = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "condition", "sample_rate_hz", "fft_size",
    "bin_spacing_hz", "window_khz", "percentile", "margin_db",
    "noise_sigma_db", "injected_peak_count", "valid_bin_count",
    "mean_error_db", "mean_absolute_error_db", "maximum_absolute_error_db",
    "p95_absolute_bin_error_db", "peak_induced_mean_absolute_change_db",
    "peak_induced_maximum_change_db", "threshold_margin_error_db",
    "mae_limit_db", "p95_trial_mae_limit_db", "peak_effect_p95_limit_db",
    "passed", "notes",
)


def baseline_for(condition: str, normalized_axis: np.ndarray) -> np.ndarray:
    if condition == "flat":
        return np.full_like(normalized_axis, 20.0)
    if condition == "curved":
        return 20.0 + 6.0 * normalized_axis ** 2
    if condition == "stepped":
        return np.where(normalized_axis < 0.0, 20.0, 28.0)
    raise ValueError(condition)


def valid_mask(condition: str, count: int, half_window_bins: int) -> np.ndarray:
    mask = np.ones(count, dtype=bool)
    mask[:half_window_bins] = False
    mask[-half_window_bins:] = False
    if condition == "stepped":
        center = count // 2
        mask[center - half_window_bins:center + half_window_bins + 1] = False
    return mask


def add_narrow_peaks(
    values: np.ndarray, rng: np.random.Generator, half_window_bins: int
) -> tuple[np.ndarray, list[int]]:
    output = values.copy()
    candidates = np.arange(half_window_bins, len(values) - half_window_bins)
    centers = rng.choice(candidates, size=PEAK_COUNT, replace=False)
    for center in centers:
        excess = float(rng.uniform(15.0, 30.0))
        left = int(center) - PEAK_WIDTH_BINS // 2
        right = left + PEAK_WIDTH_BINS
        output[left:right] += excess
    return output, [int(center) for center in centers]


def run_trials() -> tuple[list[dict[str, object]], dict[str, dict[str, list[float]]]]:
    count = int(NUM_SAMPLES)
    sample_rate = float(SAMPLE_RATE)
    bin_spacing = sample_rate / count
    freqs_mhz = np.fft.fftshift(np.fft.fftfreq(count, d=1.0 / sample_rate)) / 1e6
    normalized = np.linspace(-1.0, 1.0, count)
    window_bins = max(3, round(WINDOW_KHZ / (bin_spacing / 1000.0)))
    if window_bins % 2 == 0:
        window_bins += 1
    half_window = window_bins // 2
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    rows: list[dict[str, object]] = []
    examples: dict[str, dict[str, list[float]]] = {}
    trial_id = 0

    for condition_index, condition in enumerate(CONDITIONS):
        baseline = baseline_for(condition, normalized)
        mask = valid_mask(condition, count, half_window)
        for repetition in range(REPETITIONS):
            seed = BASE_SEED + condition_index * 1000 + repetition
            rng = np.random.default_rng(seed)
            noisy = baseline + rng.normal(0.0, NOISE_SIGMA_DB, count)
            with_peaks, _ = add_narrow_peaks(noisy, rng, half_window)
            floor_clean = estimate_local_noise_floor(
                noisy, freqs_mhz, window_khz=WINDOW_KHZ, percentile=PERCENTILE
            )
            floor_peaks = estimate_local_noise_floor(
                with_peaks, freqs_mhz,
                window_khz=WINDOW_KHZ, percentile=PERCENTILE
            )
            threshold = build_local_detection_threshold(
                with_peaks, freqs_mhz, margin_db=MARGIN_DB,
                window_khz=WINDOW_KHZ, percentile=PERCENTILE
            )
            errors = floor_peaks[mask] - baseline[mask]
            absolute_errors = np.abs(errors)
            peak_change = np.abs(floor_peaks[mask] - floor_clean[mask])
            margin_error = float(np.max(np.abs(
                threshold[mask] - floor_peaks[mask] - MARGIN_DB
            )))
            mae = float(np.mean(absolute_errors))
            row_pass = mae <= MAE_LIMIT_DB and margin_error <= 1e-10
            rows.append({
                "validation_id": VALIDATION_ID,
                "configuration_id": CONFIGURATION_ID,
                "trial_id": trial_id + 1,
                "timestamp": timestamp,
                "random_seed": seed,
                "condition": condition,
                "sample_rate_hz": sample_rate,
                "fft_size": count,
                "bin_spacing_hz": bin_spacing,
                "window_khz": WINDOW_KHZ,
                "percentile": PERCENTILE,
                "margin_db": MARGIN_DB,
                "noise_sigma_db": NOISE_SIGMA_DB,
                "injected_peak_count": PEAK_COUNT,
                "valid_bin_count": int(np.sum(mask)),
                "mean_error_db": float(np.mean(errors)),
                "mean_absolute_error_db": mae,
                "maximum_absolute_error_db": float(np.max(absolute_errors)),
                "p95_absolute_bin_error_db": float(np.percentile(absolute_errors, 95)),
                "peak_induced_mean_absolute_change_db": float(np.mean(peak_change)),
                "peak_induced_maximum_change_db": float(np.max(peak_change)),
                "threshold_margin_error_db": margin_error,
                "mae_limit_db": MAE_LIMIT_DB,
                "p95_trial_mae_limit_db": P95_TRIAL_MAE_LIMIT_DB,
                "peak_effect_p95_limit_db": PEAK_EFFECT_P95_LIMIT_DB,
                "passed": str(row_pass).lower(),
                "notes": "Evaluation excludes filter edges and stepped-baseline transition",
            })
            if repetition == 0:
                stride = 8
                examples[condition] = {
                    "frequency_khz": (freqs_mhz[::stride] * 1000.0).tolist(),
                    "baseline_db": baseline[::stride].tolist(),
                    "observed_db": with_peaks[::stride].tolist(),
                    "estimated_db": floor_peaks[::stride].tolist(),
                }
            trial_id += 1
    return rows, examples


def summarize(rows: list[dict[str, object]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    conditions = []
    for condition in CONDITIONS:
        selected = [row for row in rows if row["condition"] == condition]
        maes = np.asarray([float(row["mean_absolute_error_db"]) for row in selected])
        peak_effects = np.asarray([
            float(row["peak_induced_mean_absolute_change_db"]) for row in selected
        ])
        margin_errors = np.asarray([
            float(row["threshold_margin_error_db"]) for row in selected
        ])
        mean_mae = float(np.mean(maes))
        p95_mae = float(np.percentile(maes, 95))
        p95_peak_effect = float(np.percentile(peak_effects, 95))
        passed = (
            mean_mae <= MAE_LIMIT_DB
            and p95_mae <= P95_TRIAL_MAE_LIMIT_DB
            and p95_peak_effect <= PEAK_EFFECT_P95_LIMIT_DB
            and float(np.max(margin_errors)) <= 1e-10
        )
        conditions.append({
            "condition": condition,
            "trial_count": len(selected),
            "mean_bias_db": float(np.mean([
                float(row["mean_error_db"]) for row in selected
            ])),
            "mean_mae_db": mean_mae,
            "p95_trial_mae_db": p95_mae,
            "mean_p95_bin_error_db": float(np.mean([
                float(row["p95_absolute_bin_error_db"]) for row in selected
            ])),
            "p95_peak_induced_change_db": p95_peak_effect,
            "maximum_threshold_margin_error_db": float(np.max(margin_errors)),
            "passed": passed,
        })
    overall_pass = all(bool(row["passed"]) for row in conditions)
    summary = {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": len(rows),
        "trials_per_condition": REPETITIONS,
        "conditions": len(CONDITIONS),
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "window_khz": WINDOW_KHZ,
        "percentile": PERCENTILE,
        "margin_db": MARGIN_DB,
        "noise_sigma_db": NOISE_SIGMA_DB,
        "mae_limit_db": MAE_LIMIT_DB,
        "p95_trial_mae_limit_db": P95_TRIAL_MAE_LIMIT_DB,
        "peak_effect_p95_limit_db": PEAK_EFFECT_P95_LIMIT_DB,
        "maximum_condition_mean_mae_db": max(float(row["mean_mae_db"]) for row in conditions),
        "maximum_condition_p95_trial_mae_db": max(float(row["p95_trial_mae_db"]) for row in conditions),
        "maximum_condition_p95_peak_effect_db": max(float(row["p95_peak_induced_change_db"]) for row in conditions),
        "result": "PASS" if overall_pass else "FAIL",
        "claim_scope": "Synthetic spectral-baseline tracking by the existing percentile estimator",
        "excluded_claims": "RTL-SDR noise figure; calibrated dBm; abrupt-step accuracy inside the estimator window",
    }
    return conditions, summary


def write_csv(path: Path, rows: list[dict[str, object]], fields=None) -> None:
    resolved = fields or FIELDS
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=resolved)
        writer.writeheader()
        writer.writerows(rows)


def plot_results(path: Path, rows, conditions, examples) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    data = [[float(row["mean_absolute_error_db"]) for row in rows if row["condition"] == c] for c in CONDITIONS]
    axes[0, 0].boxplot(data, tick_labels=[c.title() for c in CONDITIONS])
    axes[0, 0].axhline(MAE_LIMIT_DB, color="#ffbf00", linestyle="--", label="Mean MAE limit")
    axes[0, 0].set_title("Trial Mean Absolute Floor Error")
    axes[0, 0].set_ylabel("Error (dB)")
    axes[0, 0].legend()
    axes[0, 0].grid(True, axis="y", alpha=0.25)

    x = np.arange(len(CONDITIONS))
    axes[0, 1].bar(x - 0.18, [c["mean_mae_db"] for c in conditions], 0.36, label="Mean MAE", color="#00aeea")
    axes[0, 1].bar(x + 0.18, [c["p95_trial_mae_db"] for c in conditions], 0.36, label="95th percentile trial MAE", color="#7f8c98")
    axes[0, 1].set_xticks(x, [c.title() for c in CONDITIONS])
    axes[0, 1].set_title("Condition Error Summary")
    axes[0, 1].set_ylabel("Error (dB)")
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis="y", alpha=0.25)

    for axis, condition in zip(axes[1], ("curved", "stepped")):
        example = examples[condition]
        x_khz = np.asarray(example["frequency_khz"])
        axis.plot(x_khz, example["observed_db"], color="#CBD5E1", linewidth=0.7, label="Observed with peaks")
        axis.plot(x_khz, example["baseline_db"], color="#1fd98a", linewidth=1.5, label="Known baseline")
        axis.plot(x_khz, example["estimated_db"], color="#00aeea", linewidth=1.5, label="Estimated floor")
        axis.set_title(f"{condition.title()} Baseline Example")
        axis.set_xlabel("Frequency offset (kHz)")
        axis.set_ylabel("Relative level (dB)")
        axis.grid(True, alpha=0.2)
        axis.legend(fontsize=8)
    fig.suptitle("AV-NF-01: Adaptive Local Noise-Floor Validation")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    fig.text(0.01, 0.01, "CFG-S01 | 300 trials | Synthetic spectral baselines | Existing estimator", fontsize=8, color="#4b5563")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows, examples = run_trials()
    conditions, summary = summarize(rows)
    prefix = "AV-NF-01_CFG-S01"
    write_csv(args.output_dir / f"{prefix}_noise_floor_trials.csv", rows)
    write_csv(args.output_dir / f"{prefix}_condition_summary.csv", conditions, conditions[0].keys())
    (args.output_dir / f"{prefix}_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    plot_results(args.output_dir / f"{prefix}_noise_floor_validation.png", rows, conditions, examples)
    print(json.dumps(summary, indent=2))
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
