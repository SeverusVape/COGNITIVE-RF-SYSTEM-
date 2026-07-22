"""Run AV-FFT-02 with deterministic synthetic IQ and no SDR hardware.

The experiment compares the existing rectangular FFT path with the existing
coherent-gain-corrected Hann FFT path. Leakage is the integrated spectral
energy outside a fixed +/-2-bin protected region around the detected peak.
"""

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

from SDR.fft_processing import compute_fft, compute_windowed_fft
from UTILS.config import NUM_SAMPLES, SAMPLE_RATE


VALIDATION_ID = "AV-FFT-02"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_102_027
REPETITIONS_PER_CONDITION = 20
INTEGER_BIN_OFFSETS = (-2048, 0, 2048)
FRACTIONAL_BIN_OFFSETS = (0.0, 0.25, 0.5)
WINDOWS = ("Rectangular", "Hann")
PROTECTED_HALF_WIDTH_BINS = 2
CENTERED_PEAK_LIMIT_DB = 0.01
MINIMUM_OFF_BIN_IMPROVEMENT_DB = 10.0

FIELDNAMES = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "window_type", "sample_rate_hz", "fft_size",
    "bin_spacing_hz", "integer_bin_offset", "fractional_bin_offset",
    "tone_offset_hz", "phase_rad", "detected_bin_offset",
    "peak_relative_db", "ideal_peak_db", "peak_error_db",
    "protected_half_width_bins", "leakage_relative_db",
    "maximum_sidelobe_relative_db", "centered_peak_limit_db",
    "minimum_off_bin_improvement_db", "passed", "notes",
)


def _measure_spectrum(
    samples: np.ndarray,
    window_type: str,
    integer_bin_offset: int,
) -> dict[str, float]:
    spectrum_db = (
        compute_fft(samples)
        if window_type == "Rectangular"
        else compute_windowed_fft(samples)
    )
    peak_index = int(np.argmax(spectrum_db))
    peak_db = float(spectrum_db[peak_index])
    ideal_peak_db = float(20.0 * np.log10(len(samples)))
    linear_power = np.power(10.0, spectrum_db / 10.0)
    protected = np.zeros(len(samples), dtype=bool)
    protected[
        max(0, peak_index - PROTECTED_HALF_WIDTH_BINS):
        min(len(samples), peak_index + PROTECTED_HALF_WIDTH_BINS + 1)
    ] = True
    total_power = float(np.sum(linear_power))
    leakage_power = float(np.sum(linear_power[~protected]))
    leakage_relative_db = float(
        10.0 * np.log10(max(leakage_power / total_power, np.finfo(float).tiny))
    )
    maximum_sidelobe_relative_db = float(
        np.max(spectrum_db[~protected]) - peak_db
    )
    detected_bin_offset = float(peak_index - len(samples) // 2)
    return {
        "detected_bin_offset": detected_bin_offset,
        "peak_relative_db": peak_db,
        "ideal_peak_db": ideal_peak_db,
        "peak_error_db": peak_db - ideal_peak_db,
        "leakage_relative_db": leakage_relative_db,
        "maximum_sidelobe_relative_db": maximum_sidelobe_relative_db,
        "bin_error": detected_bin_offset - integer_bin_offset,
    }


def run_trials() -> list[dict[str, object]]:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    bin_spacing = sample_rate / fft_size
    sample_indices = np.arange(fft_size, dtype=float)
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    rows: list[dict[str, object]] = []
    pair_id = 0
    trial_id = 0

    for integer_bin_offset in INTEGER_BIN_OFFSETS:
        for fractional_bin_offset in FRACTIONAL_BIN_OFFSETS:
            tone_bins = integer_bin_offset + fractional_bin_offset
            tone_offset_hz = tone_bins * bin_spacing
            for _ in range(REPETITIONS_PER_CONDITION):
                random_seed = BASE_SEED + pair_id
                rng = np.random.default_rng(random_seed)
                phase_rad = float(rng.uniform(0.0, 2.0 * np.pi))
                samples = np.exp(
                    1j * (
                        2.0 * np.pi * tone_offset_hz * sample_indices
                        / sample_rate + phase_rad
                    )
                )
                for window_type in WINDOWS:
                    metrics = _measure_spectrum(
                        samples, window_type, integer_bin_offset
                    )
                    centered_pass = (
                        fractional_bin_offset != 0.0
                        or abs(metrics["peak_error_db"])
                        <= CENTERED_PEAK_LIMIT_DB
                    )
                    rows.append({
                        "validation_id": VALIDATION_ID,
                        "configuration_id": CONFIGURATION_ID,
                        "trial_id": trial_id + 1,
                        "timestamp": timestamp,
                        "random_seed": random_seed,
                        "window_type": window_type,
                        "sample_rate_hz": sample_rate,
                        "fft_size": fft_size,
                        "bin_spacing_hz": bin_spacing,
                        "integer_bin_offset": integer_bin_offset,
                        "fractional_bin_offset": fractional_bin_offset,
                        "tone_offset_hz": tone_offset_hz,
                        "phase_rad": phase_rad,
                        "detected_bin_offset": metrics["detected_bin_offset"],
                        "peak_relative_db": metrics["peak_relative_db"],
                        "ideal_peak_db": metrics["ideal_peak_db"],
                        "peak_error_db": metrics["peak_error_db"],
                        "protected_half_width_bins": PROTECTED_HALF_WIDTH_BINS,
                        "leakage_relative_db": metrics["leakage_relative_db"],
                        "maximum_sidelobe_relative_db": metrics[
                            "maximum_sidelobe_relative_db"
                        ],
                        "centered_peak_limit_db": CENTERED_PEAK_LIMIT_DB,
                        "minimum_off_bin_improvement_db": (
                            MINIMUM_OFF_BIN_IMPROVEMENT_DB
                        ),
                        "passed": str(centered_pass).lower(),
                        "notes": (
                            "Synthetic unit-amplitude complex tone; leakage "
                            "excludes fixed +/-2 bins around detected peak"
                        ),
                    })
                    trial_id += 1
                pair_id += 1
    return rows


def _condition_means(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for integer_bin_offset in INTEGER_BIN_OFFSETS:
        for fractional_bin_offset in FRACTIONAL_BIN_OFFSETS:
            condition = [
                row for row in rows
                if int(row["integer_bin_offset"]) == integer_bin_offset
                and float(row["fractional_bin_offset"]) == fractional_bin_offset
            ]
            by_window = {
                window: [row for row in condition if row["window_type"] == window]
                for window in WINDOWS
            }
            rectangular_leakage = float(np.mean([
                float(row["leakage_relative_db"])
                for row in by_window["Rectangular"]
            ]))
            hann_leakage = float(np.mean([
                float(row["leakage_relative_db"])
                for row in by_window["Hann"]
            ]))
            improvement = rectangular_leakage - hann_leakage
            summaries.append({
                "integer_bin_offset": integer_bin_offset,
                "fractional_bin_offset": fractional_bin_offset,
                "rectangular_peak_error_db": float(np.mean([
                    float(row["peak_error_db"])
                    for row in by_window["Rectangular"]
                ])),
                "hann_peak_error_db": float(np.mean([
                    float(row["peak_error_db"])
                    for row in by_window["Hann"]
                ])),
                "rectangular_leakage_db": rectangular_leakage,
                "hann_leakage_db": hann_leakage,
                "hann_leakage_improvement_db": improvement,
                "off_bin_pass": (
                    fractional_bin_offset == 0.0
                    or improvement >= MINIMUM_OFF_BIN_IMPROVEMENT_DB
                ),
            })
    return summaries


def build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    conditions = _condition_means(rows)
    centered_errors = [
        abs(float(row["peak_error_db"])) for row in rows
        if float(row["fractional_bin_offset"]) == 0.0
    ]
    off_bin_conditions = [
        condition for condition in conditions
        if float(condition["fractional_bin_offset"]) > 0.0
    ]
    centered_pass = max(centered_errors) <= CENTERED_PEAK_LIMIT_DB
    off_bin_pass = all(bool(row["off_bin_pass"]) for row in off_bin_conditions)
    result = "PASS" if centered_pass and off_bin_pass else "FAIL"
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": len(rows),
        "paired_tone_realizations": len(rows) // len(WINDOWS),
        "frequency_locations": len(INTEGER_BIN_OFFSETS),
        "fractional_offsets": len(FRACTIONAL_BIN_OFFSETS),
        "repetitions_per_condition": REPETITIONS_PER_CONDITION,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "bin_spacing_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES),
        "protected_half_width_bins": PROTECTED_HALF_WIDTH_BINS,
        "centered_peak_limit_db": CENTERED_PEAK_LIMIT_DB,
        "maximum_centered_peak_error_db": max(centered_errors),
        "minimum_required_off_bin_improvement_db": (
            MINIMUM_OFF_BIN_IMPROVEMENT_DB
        ),
        "minimum_observed_off_bin_improvement_db": min(
            float(row["hann_leakage_improvement_db"])
            for row in off_bin_conditions
        ),
        "centered_peak_acceptance": "PASS" if centered_pass else "FAIL",
        "off_bin_leakage_acceptance": "PASS" if off_bin_pass else "FAIL",
        "result": result,
        "claim_scope": (
            "Numerical rectangular-versus-Hann response for deterministic "
            "synthetic complex tones"
        ),
        "excluded_claims": (
            "RTL-SDR analog response; calibrated power; arbitrary modulated "
            "signals; universal sidelobe specification"
        ),
        "leakage_definition": (
            "Integrated spectral energy outside fixed +/-2 bins around the "
            "detected peak, relative to total spectral energy"
        ),
        "conditions": conditions,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_condition_csv(path: Path, conditions: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=conditions[0].keys())
        writer.writeheader()
        writer.writerows(conditions)


def plot_comparison(path: Path, conditions: list[dict[str, object]]) -> None:
    fractions = np.asarray(FRACTIONAL_BIN_OFFSETS)
    rectangular_leakage = []
    hann_leakage = []
    rectangular_peak = []
    hann_peak = []
    for fractional_offset in fractions:
        selected = [
            row for row in conditions
            if float(row["fractional_bin_offset"]) == fractional_offset
        ]
        rectangular_leakage.append(np.mean([
            float(row["rectangular_leakage_db"]) for row in selected
        ]))
        hann_leakage.append(np.mean([
            float(row["hann_leakage_db"]) for row in selected
        ]))
        rectangular_peak.append(np.mean([
            float(row["rectangular_peak_error_db"]) for row in selected
        ]))
        hann_peak.append(np.mean([
            float(row["hann_peak_error_db"]) for row in selected
        ]))

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.8))
    colors = {"Rectangular": "#7f8c98", "Hann": "#00aeea"}
    axes[0].plot(fractions[1:], rectangular_leakage[1:], "o-", linewidth=2,
                 color=colors["Rectangular"], label="Rectangular")
    axes[0].plot(fractions[1:], hann_leakage[1:], "o-", linewidth=2,
                 color=colors["Hann"], label="Hann")
    axes[0].set_title("Integrated Leakage Outside ±2 Bins")
    axes[0].set_xlabel("Fractional bin offset")
    axes[0].set_ylabel("Leakage relative to total energy (dB)")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend()

    axes[1].plot(fractions, rectangular_peak, "o-", linewidth=2,
                 color=colors["Rectangular"], label="Rectangular")
    axes[1].plot(fractions, hann_peak, "o-", linewidth=2,
                 color=colors["Hann"], label="Hann")
    axes[1].axhline(0.0, color="#1fd98a", linewidth=1)
    axes[1].set_title("Peak Amplitude Error")
    axes[1].set_xlabel("Fractional bin offset")
    axes[1].set_ylabel("Peak error (dB)")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend()
    fig.suptitle("AV-FFT-02: Rectangular vs Coherent-Gain-Corrected Hann")
    fig.text(0.01, 0.01,
             "CFG-S01 | 360 spectra | 2.048 MSPS | 8192 points | Synthetic data",
             fontsize=8, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = run_trials()
    summary = build_summary(rows)
    prefix = "AV-FFT-02_CFG-S01"
    write_csv(args.output_dir / f"{prefix}_fft_window_trials.csv", rows)
    write_condition_csv(
        args.output_dir / f"{prefix}_condition_summary.csv",
        summary["conditions"],
    )
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    plot_comparison(
        args.output_dir / f"{prefix}_window_comparison.png",
        summary["conditions"],
    )
    print(json.dumps({key: value for key, value in summary.items()
                      if key != "conditions"}, indent=2))
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
