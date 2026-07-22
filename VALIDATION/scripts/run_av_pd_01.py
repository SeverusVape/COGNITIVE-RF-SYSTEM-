"""Run AV-PD-01 peak-detection probability validation without SDR hardware."""

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


VALIDATION_ID = "AV-PD-01"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_102_126
SNR_LEVELS_DB = (-40.0, -36.0, -32.0, -30.0, -28.0, -26.0, -24.0, -22.0, -20.0)
TRIALS_PER_SNR = 100
MATCH_TOLERANCE_BINS = 1.0
LOW_SNR_DB = -40.0
HIGH_SNR_DB = -22.0
MINIMUM_DETECTION_RISE = 0.80
MINIMUM_HIGH_SNR_DETECTION = 0.95

FIELDNAMES = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "condition", "sample_rate_hz", "fft_size",
    "noise_model", "snr_definition", "snr_db", "tone_1_hz",
    "tone_2_hz", "tone_separation_khz", "relative_tone_2_db",
    "controlled_bandwidth_khz", "expected_occupancy_percent",
    "expected_peak_count", "detected_peak_count",
    "detected_frequency_1_hz", "detected_frequency_2_hz",
    "frequency_error_1_hz", "estimated_bandwidth_1_khz",
    "measured_occupancy_percent", "local_floor_median_db",
    "threshold_median_db", "detected", "valid", "notes",
)


def run_trials() -> list[dict[str, object]]:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    bin_spacing = sample_rate / fft_size
    frequency_axis_hz = np.fft.fftshift(
        np.fft.fftfreq(fft_size, d=1.0 / sample_rate)
    )
    frequency_axis_mhz = frequency_axis_hz / 1e6
    sample_indices = np.arange(fft_size, dtype=float)
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    rows: list[dict[str, object]] = []
    trial_id = 0

    for snr_db in SNR_LEVELS_DB:
        tone_amplitude = float(np.sqrt(10.0 ** (snr_db / 10.0)))
        for _ in range(TRIALS_PER_SNR):
            seed = BASE_SEED + trial_id
            rng = np.random.default_rng(seed)
            tone_hz = float(rng.uniform(-750_000.0, 750_000.0))
            phase = float(rng.uniform(0.0, 2.0 * np.pi))
            noise = (
                rng.normal(0.0, np.sqrt(0.5), fft_size)
                + 1j * rng.normal(0.0, np.sqrt(0.5), fft_size)
            )
            tone = tone_amplitude * np.exp(
                1j * (
                    2.0 * np.pi * tone_hz * sample_indices / sample_rate
                    + phase
                )
            )
            power_db = compute_windowed_fft(noise + tone)
            peaks, threshold = detect_peaks(power_db, frequency_axis_mhz)
            peak_frequencies_hz = [float(peak[0]) * 1e6 for peak in peaks]
            matched_index = None
            if peak_frequencies_hz:
                closest_index = int(np.argmin(
                    np.abs(np.asarray(peak_frequencies_hz) - tone_hz)
                ))
                if abs(peak_frequencies_hz[closest_index] - tone_hz) <= bin_spacing:
                    matched_index = closest_index

            detected = matched_index is not None
            matched_frequency = (
                peak_frequencies_hz[matched_index] if detected else "NA"
            )
            frequency_error = (
                float(matched_frequency) - tone_hz if detected else "NA"
            )
            bandwidth_khz = (
                float(peaks[matched_index][2]) if detected else "NA"
            )
            rows.append({
                "validation_id": VALIDATION_ID,
                "configuration_id": CONFIGURATION_ID,
                "trial_id": trial_id + 1,
                "timestamp": timestamp,
                "random_seed": seed,
                "condition": "tone_noise",
                "sample_rate_hz": sample_rate,
                "fft_size": fft_size,
                "noise_model": "circular complex Gaussian E[abs(n)^2]=1",
                "snr_definition": "10*log10(tone power / complex noise power) before windowing",
                "snr_db": snr_db,
                "tone_1_hz": tone_hz,
                "tone_2_hz": "NA",
                "tone_separation_khz": "NA",
                "relative_tone_2_db": "NA",
                "controlled_bandwidth_khz": 0.0,
                "expected_occupancy_percent": "NA",
                "expected_peak_count": 1,
                "detected_peak_count": len(peaks),
                "detected_frequency_1_hz": matched_frequency,
                "detected_frequency_2_hz": "NA",
                "frequency_error_1_hz": frequency_error,
                "estimated_bandwidth_1_khz": bandwidth_khz,
                "measured_occupancy_percent": "NA",
                "local_floor_median_db": float(np.median(threshold - 10.0)),
                "threshold_median_db": float(np.median(threshold)),
                "detected": str(detected).lower(),
                "valid": "true",
                "notes": "Match requires a returned peak within one 250 Hz FFT bin",
            })
            trial_id += 1
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for snr_db in SNR_LEVELS_DB:
        group = [row for row in rows if float(row["snr_db"]) == snr_db]
        detected = [row for row in group if row["detected"] == "true"]
        absolute_errors = np.asarray([
            abs(float(row["frequency_error_1_hz"])) for row in detected
        ])
        summaries.append({
            "snr_db": snr_db,
            "trial_count": len(group),
            "detected_count": len(detected),
            "detection_probability": len(detected) / len(group),
            "median_absolute_frequency_error_hz": (
                float(np.median(absolute_errors)) if len(absolute_errors) else "NA"
            ),
            "p95_absolute_frequency_error_hz": (
                float(np.percentile(absolute_errors, 95)) if len(absolute_errors) else "NA"
            ),
            "mean_returned_peak_count": float(np.mean([
                int(row["detected_peak_count"]) for row in group
            ])),
        })
    return summaries


def build_result(summaries: list[dict[str, object]]) -> dict[str, object]:
    by_snr = {float(row["snr_db"]): row for row in summaries}
    rise = (
        float(by_snr[HIGH_SNR_DB]["detection_probability"])
        - float(by_snr[LOW_SNR_DB]["detection_probability"])
    )
    high_snr_pass = all(
        float(row["detection_probability"]) >= MINIMUM_HIGH_SNR_DETECTION
        for row in summaries if float(row["snr_db"]) >= HIGH_SNR_DB
    )
    detected_error_medians = [
        float(row["median_absolute_frequency_error_hz"])
        for row in summaries
        if row["median_absolute_frequency_error_hz"] != "NA"
    ]
    frequency_pass = max(detected_error_medians) <= float(SAMPLE_RATE) / int(NUM_SAMPLES)
    passed = rise >= MINIMUM_DETECTION_RISE and high_snr_pass and frequency_pass
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": sum(int(row["trial_count"]) for row in summaries),
        "snr_level_count": len(summaries),
        "trials_per_snr": TRIALS_PER_SNR,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "bin_spacing_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES),
        "low_snr_db": LOW_SNR_DB,
        "high_snr_db": HIGH_SNR_DB,
        "observed_detection_rise": rise,
        "minimum_detection_rise": MINIMUM_DETECTION_RISE,
        "observed_high_snr_detection_probability": float(
            by_snr[HIGH_SNR_DB]["detection_probability"]
        ),
        "minimum_high_snr_detection_probability": MINIMUM_HIGH_SNR_DETECTION,
        "maximum_median_absolute_frequency_error_hz": max(detected_error_medians),
        "frequency_error_limit_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES),
        "result": "PASS" if passed else "FAIL",
        "claim_scope": "Synthetic single-tone detection probability through the existing FFT and peak detector",
        "excluded_claims": "Noise-only false alarms (AV-PD-02); hardware sensitivity; modulated-signal detection",
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames=None) -> None:
    names = fieldnames or FIELDNAMES
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)


def plot_results(path: Path, summaries: list[dict[str, object]]) -> None:
    snr = np.asarray([float(row["snr_db"]) for row in summaries])
    probability = np.asarray([
        float(row["detection_probability"]) for row in summaries
    ])
    errors = np.asarray([
        np.nan if row["median_absolute_frequency_error_hz"] == "NA"
        else float(row["median_absolute_frequency_error_hz"])
        for row in summaries
    ])
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.0))
    axes[0].plot(snr, probability * 100.0, "o-", color="#00aeea", linewidth=2)
    axes[0].axhline(95.0, color="#ffbf00", linestyle="--", label="95% criterion")
    axes[0].axvline(HIGH_SNR_DB, color="#7f8c98", linestyle=":", label="High-SNR gate")
    axes[0].set(title="Detection Probability vs Input SNR", xlabel="Input SNR (dB)", ylabel="Detection probability (%)", ylim=(-3, 103))
    axes[0].grid(True, alpha=0.25); axes[0].legend(loc="lower right")
    axes[1].plot(snr, errors, "o-", color="#1fd98a", linewidth=2)
    axes[1].axhline(float(SAMPLE_RATE) / int(NUM_SAMPLES), color="#ffbf00", linestyle="--", label="One-bin limit")
    axes[1].set(title="Matched-Peak Frequency Error", xlabel="Input SNR (dB)", ylabel="Median absolute error (Hz)")
    axes[1].grid(True, alpha=0.25); axes[1].legend(loc="upper right")
    fig.suptitle("AV-PD-01: Synthetic Peak-Detector Performance")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.text(0.01, 0.01, "CFG-S01 | 100 deterministic trials per SNR | Hann FFT + existing adaptive detector", color="#64748b")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{VALIDATION_ID}_{CONFIGURATION_ID}"
    rows = run_trials()
    summaries = summarize(rows)
    result = build_result(summaries)
    write_csv(args.output_dir / f"{prefix}_detector_trials.csv", rows)
    write_csv(
        args.output_dir / f"{prefix}_snr_summary.csv",
        summaries,
        fieldnames=summaries[0].keys(),
    )
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    plot_results(args.output_dir / f"{prefix}_detector_performance.png", summaries)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
