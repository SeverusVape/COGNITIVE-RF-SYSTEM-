"""Run AV-FFT-01 without accessing SDR hardware.

This validation drives deterministic, bin-centered synthetic complex tones
through the existing application FFT implementation. It writes raw trials,
summary statistics, and the required frequency-error figure.
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

from SDR.fft_processing import compute_windowed_fft
from UTILS.config import NUM_SAMPLES, SAMPLE_RATE


VALIDATION_ID = "AV-FFT-01"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_102_026
REPETITIONS_PER_OFFSET = 5
SHIFTED_BIN_OFFSETS = (-3072, -1536, 0, 1536, 3072)

FIELDNAMES = (
    "validation_id",
    "configuration_id",
    "trial_id",
    "timestamp",
    "random_seed",
    "sample_rate_hz",
    "fft_size",
    "bin_spacing_hz",
    "shifted_bin_index",
    "tone_offset_hz",
    "phase_rad",
    "measured_offset_hz",
    "error_hz",
    "absolute_error_hz",
    "peak_relative_db",
    "acceptance_limit_hz",
    "passed",
    "notes",
)


def run_trials() -> list[dict[str, object]]:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    bin_spacing = sample_rate / fft_size
    acceptance_limit = bin_spacing / 2.0
    sample_indices = np.arange(fft_size, dtype=float)
    frequency_axis = np.fft.fftshift(
        np.fft.fftfreq(fft_size, d=1.0 / sample_rate)
    )
    center_index = fft_size // 2
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()

    rows: list[dict[str, object]] = []
    trial_id = 0

    for bin_offset in SHIFTED_BIN_OFFSETS:
        shifted_bin_index = center_index + bin_offset
        tone_offset_hz = float(frequency_axis[shifted_bin_index])

        for _ in range(REPETITIONS_PER_OFFSET):
            random_seed = BASE_SEED + trial_id
            rng = np.random.default_rng(random_seed)
            phase_rad = float(rng.uniform(0.0, 2.0 * np.pi))
            samples = np.exp(
                1j
                * (
                    2.0
                    * np.pi
                    * tone_offset_hz
                    * sample_indices
                    / sample_rate
                    + phase_rad
                )
            )

            spectrum_db = compute_windowed_fft(samples)
            measured_index = int(np.argmax(spectrum_db))
            measured_offset_hz = float(frequency_axis[measured_index])
            error_hz = measured_offset_hz - tone_offset_hz
            absolute_error_hz = abs(error_hz)
            passed = absolute_error_hz <= acceptance_limit

            rows.append(
                {
                    "validation_id": VALIDATION_ID,
                    "configuration_id": CONFIGURATION_ID,
                    "trial_id": trial_id + 1,
                    "timestamp": timestamp,
                    "random_seed": random_seed,
                    "sample_rate_hz": sample_rate,
                    "fft_size": fft_size,
                    "bin_spacing_hz": bin_spacing,
                    "shifted_bin_index": shifted_bin_index,
                    "tone_offset_hz": tone_offset_hz,
                    "phase_rad": phase_rad,
                    "measured_offset_hz": measured_offset_hz,
                    "error_hz": error_hz,
                    "absolute_error_hz": absolute_error_hz,
                    "peak_relative_db": float(spectrum_db[measured_index]),
                    "acceptance_limit_hz": acceptance_limit,
                    "passed": str(passed).lower(),
                    "notes": "bin-centered deterministic complex tone",
                }
            )
            trial_id += 1

    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    errors = np.asarray([float(row["error_hz"]) for row in rows])
    peaks = np.asarray([float(row["peak_relative_db"]) for row in rows])
    passed_count = sum(row["passed"] == "true" for row in rows)

    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": len(rows),
        "unique_tone_offsets": len({row["tone_offset_hz"] for row in rows}),
        "repetitions_per_offset": REPETITIONS_PER_OFFSET,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "bin_spacing_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES),
        "acceptance_limit_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES) / 2.0,
        "mean_error_hz": float(np.mean(errors)),
        "standard_deviation_error_hz": float(np.std(errors, ddof=1)),
        "maximum_absolute_error_hz": float(np.max(np.abs(errors))),
        "mean_peak_relative_db": float(np.mean(peaks)),
        "standard_deviation_peak_relative_db": float(np.std(peaks, ddof=1)),
        "passed_trials": passed_count,
        "failed_trials": len(rows) - passed_count,
        "result": "PASS" if passed_count == len(rows) else "FAIL",
        "claim_scope": "Numerical FFT-axis placement for bin-centered synthetic complex tones",
        "excluded_claims": "RTL-SDR frequency accuracy; off-bin interpolation; calibrated power",
    }


def write_summary_csv(path: Path, summary: dict[str, object]) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)


def plot_frequency_error(path: Path, rows: list[dict[str, object]]) -> None:
    grouped: dict[float, list[float]] = {}
    for row in rows:
        grouped.setdefault(float(row["tone_offset_hz"]), []).append(
            float(row["error_hz"])
        )

    offsets = np.asarray(sorted(grouped))
    means = np.asarray([np.mean(grouped[offset]) for offset in offsets])
    standard_deviations = np.asarray(
        [np.std(grouped[offset], ddof=1) for offset in offsets]
    )
    acceptance_limit = float(rows[0]["acceptance_limit_hz"])

    fig, axis = plt.subplots(figsize=(9.0, 5.2))
    axis.errorbar(
        offsets / 1000.0,
        means,
        yerr=standard_deviations,
        fmt="o-",
        color="#00aeea",
        ecolor="#7f8c98",
        capsize=4,
        linewidth=1.8,
        markersize=6,
        label="Mean signed error (n=5)",
    )
    axis.axhline(0.0, color="#1fd98a", linewidth=1.2, label="Ideal")
    axis.axhline(
        acceptance_limit,
        color="#ffbf00",
        linestyle="--",
        linewidth=1.0,
        label="Half-bin acceptance limit",
    )
    axis.axhline(
        -acceptance_limit,
        color="#ffbf00",
        linestyle="--",
        linewidth=1.0,
    )
    axis.set_ylim(-acceptance_limit * 1.2, acceptance_limit * 1.2)
    axis.set_title("AV-FFT-01: Bin-Centered Synthetic Frequency Error")
    axis.set_xlabel("Expected tone offset from center (kHz)")
    axis.set_ylabel("Signed frequency error (Hz)")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper right")
    fig.subplots_adjust(bottom=0.19, left=0.1, right=0.98, top=0.9)
    fig.text(
        0.01,
        0.025,
        "CFG-S01 | 25 trials | 2.048 MSPS | 8192-point Hann-windowed FFT | Synthetic data",
        fontsize=8,
        color="#4b5563",
    )
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = run_trials()
    summary = build_summary(rows)

    raw_path = args.output_dir / "AV-FFT-01_CFG-S01_fft_frequency_trials.csv"
    summary_csv_path = args.output_dir / "AV-FFT-01_CFG-S01_summary.csv"
    summary_json_path = args.output_dir / "AV-FFT-01_CFG-S01_summary.json"
    figure_path = args.output_dir / "AV-FFT-01_CFG-S01_frequency_error.png"

    write_csv(raw_path, rows)
    write_summary_csv(summary_csv_path, summary)
    summary_json_path.write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    plot_frequency_error(figure_path, rows)

    print(json.dumps(summary, indent=2))
    return 0 if summary["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
