"""Run AV-PD-02 noise-only false-alarm validation without SDR hardware."""

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
from SDR.fft_processing import compute_windowed_fft
from UTILS.config import NUM_SAMPLES, SAMPLE_RATE


VALIDATION_ID = "AV-PD-02"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_102_526
TRIALS_PER_CONDITION = 500
FALSE_ALARM_PROBABILITY_LIMIT = 0.05
MEAN_FALSE_PEAK_LIMIT = 0.10
PEAK_CAP_FRAME_FRACTION_LIMIT = 0.01
PEAK_CAP = 3
CONDITIONS = ("flat_noise", "uneven_baseline")

FIELDNAMES = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "condition", "sample_rate_hz", "fft_size",
    "bin_spacing_hz", "noise_model", "baseline_peak_to_peak_db",
    "false_peak_count", "any_false_alarm", "reached_peak_cap",
    "maximum_excess_db", "mean_excess_db", "median_local_floor_db",
    "median_threshold_db", "false_alarm_probability_limit",
    "mean_false_peak_limit", "peak_cap_frame_fraction_limit", "valid",
    "notes",
)


def make_noise(
        rng: np.random.Generator,
        condition: str,
        fft_size: int
) -> tuple[np.ndarray, str, float]:
    noise = (
        rng.normal(0.0, np.sqrt(0.5), fft_size)
        + 1j * rng.normal(0.0, np.sqrt(0.5), fft_size)
    )
    if condition == "flat_noise":
        return (
            noise,
            "circular complex Gaussian E[abs(n)^2]=1",
            0.0,
        )

    normalized_frequency = np.linspace(-1.0, 1.0, fft_size, endpoint=False)
    baseline_db = (
        4.0 * normalized_frequency
        + 6.0 * np.sin(1.25 * np.pi * normalized_frequency)
    )
    baseline_db -= float(np.mean(baseline_db))
    shaped_spectrum = np.fft.fftshift(np.fft.fft(noise))
    shaped_spectrum *= 10.0 ** (baseline_db / 20.0)
    shaped_noise = np.fft.ifft(np.fft.ifftshift(shaped_spectrum))
    shaped_noise /= np.sqrt(np.mean(np.abs(shaped_noise) ** 2))
    return (
        shaped_noise,
        "complex Gaussian shaped by deterministic 4 dB tilt plus 6 dB sinusoidal baseline",
        float(np.ptp(baseline_db)),
    )


def run_trials() -> list[dict[str, object]]:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    bin_spacing = sample_rate / fft_size
    frequency_axis_hz = np.fft.fftshift(
        np.fft.fftfreq(fft_size, d=1.0 / sample_rate)
    )
    frequency_axis_mhz = frequency_axis_hz / 1e6
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    rows: list[dict[str, object]] = []
    trial_id = 0

    for condition in CONDITIONS:
        for _ in range(TRIALS_PER_CONDITION):
            seed = BASE_SEED + trial_id
            rng = np.random.default_rng(seed)
            samples, noise_model, baseline_range = make_noise(
                rng, condition, fft_size
            )
            power_db = compute_windowed_fft(samples)
            peaks, threshold = detect_peaks(power_db, frequency_axis_mhz)
            excess_values = []
            for frequency_mhz, power, _ in peaks:
                index = int(np.argmin(np.abs(
                    frequency_axis_mhz - float(frequency_mhz)
                )))
                excess_values.append(float(power) - float(threshold[index]))

            false_peak_count = len(peaks)
            rows.append({
                "validation_id": VALIDATION_ID,
                "configuration_id": CONFIGURATION_ID,
                "trial_id": trial_id + 1,
                "timestamp": timestamp,
                "random_seed": seed,
                "condition": condition,
                "sample_rate_hz": sample_rate,
                "fft_size": fft_size,
                "bin_spacing_hz": bin_spacing,
                "noise_model": noise_model,
                "baseline_peak_to_peak_db": baseline_range,
                "false_peak_count": false_peak_count,
                "any_false_alarm": str(false_peak_count > 0).lower(),
                "reached_peak_cap": str(false_peak_count == PEAK_CAP).lower(),
                "maximum_excess_db": (
                    max(excess_values) if excess_values else "NA"
                ),
                "mean_excess_db": (
                    float(np.mean(excess_values)) if excess_values else "NA"
                ),
                "median_local_floor_db": float(np.median(threshold - 10.0)),
                "median_threshold_db": float(np.median(threshold)),
                "false_alarm_probability_limit": FALSE_ALARM_PROBABILITY_LIMIT,
                "mean_false_peak_limit": MEAN_FALSE_PEAK_LIMIT,
                "peak_cap_frame_fraction_limit": PEAK_CAP_FRAME_FRACTION_LIMIT,
                "valid": "true",
                "notes": (
                    "No intended signal; every returned candidate is counted as a false alarm"
                ),
            })
            trial_id += 1
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for condition in CONDITIONS:
        group = [row for row in rows if row["condition"] == condition]
        counts = np.asarray([
            int(row["false_peak_count"]) for row in group
        ], dtype=float)
        excess = np.asarray([
            float(row["maximum_excess_db"])
            for row in group if row["maximum_excess_db"] != "NA"
        ])
        frame_probability = float(np.mean(counts > 0))
        mean_false_peaks = float(np.mean(counts))
        peak_cap_fraction = float(np.mean(counts == PEAK_CAP))
        passed = (
            frame_probability <= FALSE_ALARM_PROBABILITY_LIMIT
            and mean_false_peaks <= MEAN_FALSE_PEAK_LIMIT
            and peak_cap_fraction <= PEAK_CAP_FRAME_FRACTION_LIMIT
        )
        summaries.append({
            "condition": condition,
            "trial_count": len(group),
            "frames_with_false_alarm": int(np.sum(counts > 0)),
            "frame_false_alarm_probability": frame_probability,
            "mean_false_peaks_per_frame": mean_false_peaks,
            "peak_cap_frame_fraction": peak_cap_fraction,
            "median_maximum_excess_db": (
                float(np.median(excess)) if len(excess) else "NA"
            ),
            "p95_maximum_excess_db": (
                float(np.percentile(excess, 95)) if len(excess) else "NA"
            ),
            "false_alarm_probability_limit": FALSE_ALARM_PROBABILITY_LIMIT,
            "mean_false_peak_limit": MEAN_FALSE_PEAK_LIMIT,
            "peak_cap_frame_fraction_limit": PEAK_CAP_FRAME_FRACTION_LIMIT,
            "result": "PASS" if passed else "FAIL",
        })
    return summaries


def build_result(summaries: list[dict[str, object]]) -> dict[str, object]:
    passed = all(row["result"] == "PASS" for row in summaries)
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": sum(int(row["trial_count"]) for row in summaries),
        "trials_per_condition": TRIALS_PER_CONDITION,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "bin_spacing_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES),
        "false_alarm_probability_limit": FALSE_ALARM_PROBABILITY_LIMIT,
        "mean_false_peak_limit": MEAN_FALSE_PEAK_LIMIT,
        "peak_cap_frame_fraction_limit": PEAK_CAP_FRAME_FRACTION_LIMIT,
        "result": "PASS" if passed else "FAIL",
        "claim_scope": (
            "Noise-only specificity of the existing Hann FFT and raw adaptive peak detector"
        ),
        "excluded_claims": (
            "Temporal confirmation/history suppression; hardware RF environment; "
            "detector redesign"
        ),
    }


def write_csv(
        path: Path,
        rows: list[dict[str, object]],
        fieldnames=None
) -> None:
    names = fieldnames or FIELDNAMES
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)


def plot_results(path: Path, summaries: list[dict[str, object]]) -> None:
    labels = [str(row["condition"]).replace("_", " ").title() for row in summaries]
    probability = np.asarray([
        float(row["frame_false_alarm_probability"]) for row in summaries
    ]) * 100.0
    mean_peaks = np.asarray([
        float(row["mean_false_peaks_per_frame"]) for row in summaries
    ])
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    colors = ["#00aeea", "#8b5cf6"]
    axes[0].bar(labels, probability, color=colors)
    axes[0].axhline(
        FALSE_ALARM_PROBABILITY_LIMIT * 100.0,
        color="#ffbf00", linestyle="--", label="5% limit"
    )
    axes[0].set(
        title="Noise-Only Frame False-Alarm Probability",
        ylabel="Frames with at least one candidate (%)",
        ylim=(0, max(105.0, float(np.max(probability)) * 1.08)),
    )
    axes[0].legend(loc="upper right")
    axes[1].bar(labels, mean_peaks, color=colors)
    axes[1].axhline(
        MEAN_FALSE_PEAK_LIMIT,
        color="#ffbf00", linestyle="--", label="0.10 peak/frame limit"
    )
    axes[1].set(
        title="Returned False Candidates",
        ylabel="Mean candidates per frame",
        ylim=(0, max(3.2, float(np.max(mean_peaks)) * 1.08)),
    )
    axes[1].legend(loc="upper right")
    for axis in axes:
        axis.grid(True, axis="y", alpha=0.25)
    figure.suptitle("AV-PD-02: Noise-Only False-Alarm Characterization")
    figure.tight_layout(rect=(0, 0.05, 1, 0.93))
    figure.text(
        0.01, 0.01,
        "CFG-S01 | 500 deterministic frames per condition | raw detector candidates",
        color="#64748b",
    )
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
    write_csv(args.output_dir / f"{prefix}_false_alarm_trials.csv", rows)
    write_csv(
        args.output_dir / f"{prefix}_condition_summary.csv",
        summaries,
        fieldnames=summaries[0].keys(),
    )
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    plot_results(args.output_dir / f"{prefix}_false_alarm.png", summaries)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
