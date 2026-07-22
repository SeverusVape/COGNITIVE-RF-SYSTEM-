"""Run AV-PD-03 two-tone resolution validation without SDR hardware."""

from __future__ import annotations

import argparse
import csv
import itertools
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


VALIDATION_ID = "AV-PD-03"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_103_326
SEPARATIONS_KHZ = (25.0, 50.0, 62.5, 70.0, 74.0, 75.0, 76.0, 80.0, 87.5, 100.0, 125.0, 150.0)
RELATIVE_TONE_2_DB = (0.0, -6.0, -12.0)
TRIALS_PER_CONDITION = 50
PRIMARY_TONE_SNR_DB = -10.0
CONFIGURED_MINIMUM_SPACING_KHZ = 75.0
MATCH_TOLERANCE_BINS = 1.0
MINIMUM_RESOLUTION_PROBABILITY = 0.95
MAXIMUM_SUBLIMIT_RESOLUTION_PROBABILITY = 0.05

TRIAL_FIELDS = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "sample_rate_hz", "fft_size", "bin_spacing_hz",
    "noise_model", "snr_definition", "primary_tone_snr_db",
    "relative_tone_2_db", "tone_1_hz", "tone_2_hz",
    "tone_separation_khz", "expected_peak_count", "returned_peak_count",
    "tone_1_detected", "tone_2_detected", "both_tones_detected",
    "detected_frequency_1_hz", "detected_frequency_2_hz",
    "frequency_error_1_hz", "frequency_error_2_hz",
    "detected_peak_separation_khz", "missed_detection_count",
    "local_response_count", "nearest_local_peak_hz", "response_class",
    "valid", "notes",
)


def generate_trial(
        rng: np.random.Generator,
        separation_khz: float,
        relative_tone_2_db: float,
        fft_size: int,
        sample_rate: float,
) -> tuple[np.ndarray, float, float]:
    half_separation_hz = separation_khz * 500.0
    midpoint_hz = float(rng.uniform(-650_000.0, 650_000.0))
    tone_1_hz = midpoint_hz - half_separation_hz
    tone_2_hz = midpoint_hz + half_separation_hz
    sample_indices = np.arange(fft_size, dtype=float)
    primary_amplitude = float(np.sqrt(10.0 ** (PRIMARY_TONE_SNR_DB / 10.0)))
    secondary_amplitude = primary_amplitude * float(
        10.0 ** (relative_tone_2_db / 20.0)
    )
    phase_1 = float(rng.uniform(0.0, 2.0 * np.pi))
    phase_2 = float(rng.uniform(0.0, 2.0 * np.pi))
    noise = (
        rng.normal(0.0, np.sqrt(0.5), fft_size)
        + 1j * rng.normal(0.0, np.sqrt(0.5), fft_size)
    )
    tone_1 = primary_amplitude * np.exp(
        1j * (2.0 * np.pi * tone_1_hz * sample_indices / sample_rate + phase_1)
    )
    tone_2 = secondary_amplitude * np.exp(
        1j * (2.0 * np.pi * tone_2_hz * sample_indices / sample_rate + phase_2)
    )
    return noise + tone_1 + tone_2, tone_1_hz, tone_2_hz


def assign_distinct_peaks(
        targets_hz: tuple[float, float],
        peak_frequencies_hz: list[float],
        tolerance_hz: float,
) -> tuple[int | None, int | None]:
    best_assignment: tuple[int | None, int | None] = (None, None)
    best_matches = -1
    best_error = float("inf")
    choices = [None] + list(range(len(peak_frequencies_hz)))
    for assignment in itertools.product(choices, repeat=2):
        used = [index for index in assignment if index is not None]
        if len(used) != len(set(used)):
            continue
        errors = []
        valid = True
        for target, index in zip(targets_hz, assignment):
            if index is None:
                continue
            error = abs(peak_frequencies_hz[index] - target)
            if error > tolerance_hz:
                valid = False
                break
            errors.append(error)
        if not valid:
            continue
        match_count = len(errors)
        total_error = sum(errors)
        if match_count > best_matches or (
                match_count == best_matches and total_error < best_error
        ):
            best_assignment = assignment
            best_matches = match_count
            best_error = total_error
    return best_assignment


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

    for relative_db in RELATIVE_TONE_2_DB:
        for separation_khz in SEPARATIONS_KHZ:
            for _ in range(TRIALS_PER_CONDITION):
                seed = BASE_SEED + trial_id
                rng = np.random.default_rng(seed)
                samples, tone_1_hz, tone_2_hz = generate_trial(
                    rng, separation_khz, relative_db, fft_size, sample_rate
                )
                power_db = compute_windowed_fft(samples)
                peaks, _ = detect_peaks(power_db, frequency_axis_mhz)
                peak_frequencies_hz = [float(peak[0]) * 1e6 for peak in peaks]
                match_1, match_2 = assign_distinct_peaks(
                    (tone_1_hz, tone_2_hz),
                    peak_frequencies_hz,
                    bin_spacing_hz * MATCH_TOLERANCE_BINS,
                )
                detected_1 = match_1 is not None
                detected_2 = match_2 is not None
                both_detected = detected_1 and detected_2
                detected_frequency_1 = (
                    peak_frequencies_hz[match_1] if detected_1 else "NA"
                )
                detected_frequency_2 = (
                    peak_frequencies_hz[match_2] if detected_2 else "NA"
                )
                error_1 = (
                    float(detected_frequency_1) - tone_1_hz if detected_1 else "NA"
                )
                error_2 = (
                    float(detected_frequency_2) - tone_2_hz if detected_2 else "NA"
                )
                detected_separation = (
                    abs(float(detected_frequency_2) - float(detected_frequency_1)) / 1000.0
                    if both_detected else "NA"
                )
                lower = tone_1_hz - bin_spacing_hz
                upper = tone_2_hz + bin_spacing_hz
                local_peaks = [
                    frequency for frequency in peak_frequencies_hz
                    if lower <= frequency <= upper
                ]
                midpoint_hz = (tone_1_hz + tone_2_hz) / 2.0
                nearest_local = (
                    min(local_peaks, key=lambda value: abs(value - midpoint_hz))
                    if local_peaks else "NA"
                )
                if both_detected:
                    response_class = "resolved"
                elif detected_1 and not detected_2:
                    response_class = "tone_1_only"
                elif detected_2 and not detected_1:
                    response_class = "tone_2_only"
                elif len(local_peaks) == 1:
                    response_class = "merged_or_suppressed"
                else:
                    response_class = "neither_detected"

                rows.append({
                    "validation_id": VALIDATION_ID,
                    "configuration_id": CONFIGURATION_ID,
                    "trial_id": trial_id + 1,
                    "timestamp": timestamp,
                    "random_seed": seed,
                    "sample_rate_hz": sample_rate,
                    "fft_size": fft_size,
                    "bin_spacing_hz": bin_spacing_hz,
                    "noise_model": "circular complex Gaussian E[abs(n)^2]=1",
                    "snr_definition": "tone 1 power / complex noise power before windowing",
                    "primary_tone_snr_db": PRIMARY_TONE_SNR_DB,
                    "relative_tone_2_db": relative_db,
                    "tone_1_hz": tone_1_hz,
                    "tone_2_hz": tone_2_hz,
                    "tone_separation_khz": separation_khz,
                    "expected_peak_count": 2,
                    "returned_peak_count": len(peaks),
                    "tone_1_detected": str(detected_1).lower(),
                    "tone_2_detected": str(detected_2).lower(),
                    "both_tones_detected": str(both_detected).lower(),
                    "detected_frequency_1_hz": detected_frequency_1,
                    "detected_frequency_2_hz": detected_frequency_2,
                    "frequency_error_1_hz": error_1,
                    "frequency_error_2_hz": error_2,
                    "detected_peak_separation_khz": detected_separation,
                    "missed_detection_count": 2 - int(detected_1) - int(detected_2),
                    "local_response_count": len(local_peaks),
                    "nearest_local_peak_hz": nearest_local,
                    "response_class": response_class,
                    "valid": "true",
                    "notes": "Distinct assignment requires each tone within one 250 Hz FFT bin",
                })
                trial_id += 1
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for relative_db in RELATIVE_TONE_2_DB:
        for separation_khz in SEPARATIONS_KHZ:
            group = [
                row for row in rows
                if float(row["relative_tone_2_db"]) == relative_db
                and float(row["tone_separation_khz"]) == separation_khz
            ]
            resolved = [row for row in group if row["both_tones_detected"] == "true"]
            errors = np.asarray([
                abs(float(row[key]))
                for row in resolved
                for key in ("frequency_error_1_hz", "frequency_error_2_hz")
            ])
            response_counts = {
                response: sum(row["response_class"] == response for row in group)
                for response in (
                    "resolved", "tone_1_only", "tone_2_only",
                    "merged_or_suppressed", "neither_detected",
                )
            }
            summaries.append({
                "tone_separation_khz": separation_khz,
                "relative_tone_2_db": relative_db,
                "trial_count": len(group),
                "both_detected_count": len(resolved),
                "both_detected_probability": len(resolved) / len(group),
                "tone_1_detection_probability": np.mean([
                    row["tone_1_detected"] == "true" for row in group
                ]),
                "tone_2_detection_probability": np.mean([
                    row["tone_2_detected"] == "true" for row in group
                ]),
                "merged_or_suppressed_probability": (
                    response_counts["merged_or_suppressed"] / len(group)
                ),
                "mean_returned_peak_count": np.mean([
                    int(row["returned_peak_count"]) for row in group
                ]),
                "median_absolute_frequency_error_hz": (
                    float(np.median(errors)) if len(errors) else "NA"
                ),
                "p95_absolute_frequency_error_hz": (
                    float(np.percentile(errors, 95)) if len(errors) else "NA"
                ),
                "resolved_count": response_counts["resolved"],
                "tone_1_only_count": response_counts["tone_1_only"],
                "tone_2_only_count": response_counts["tone_2_only"],
                "merged_or_suppressed_count": response_counts["merged_or_suppressed"],
                "neither_detected_count": response_counts["neither_detected"],
            })
    return summaries


def find_validated_boundary(summaries, relative_db: float) -> float | str:
    rows = sorted(
        [row for row in summaries if float(row["relative_tone_2_db"]) == relative_db],
        key=lambda row: float(row["tone_separation_khz"]),
    )
    for index, row in enumerate(rows):
        if all(
                float(candidate["both_detected_probability"])
                >= MINIMUM_RESOLUTION_PROBABILITY
                for candidate in rows[index:]
        ):
            return float(row["tone_separation_khz"])
    return "NA"


def build_result(summaries: list[dict[str, object]]) -> dict[str, object]:
    equal = [row for row in summaries if float(row["relative_tone_2_db"]) == 0.0]
    at_or_above = [
        row for row in equal
        if float(row["tone_separation_khz"]) >= CONFIGURED_MINIMUM_SPACING_KHZ
    ]
    below = [
        row for row in equal
        if float(row["tone_separation_khz"]) < CONFIGURED_MINIMUM_SPACING_KHZ
    ]
    errors = [
        float(row["p95_absolute_frequency_error_hz"])
        for row in equal if row["p95_absolute_frequency_error_hz"] != "NA"
    ]
    minimum_above = min(float(row["both_detected_probability"]) for row in at_or_above)
    maximum_below = max(float(row["both_detected_probability"]) for row in below)
    maximum_p95_error = max(errors)
    passed = (
        minimum_above >= MINIMUM_RESOLUTION_PROBABILITY
        and maximum_below <= MAXIMUM_SUBLIMIT_RESOLUTION_PROBABILITY
        and maximum_p95_error <= float(SAMPLE_RATE) / int(NUM_SAMPLES)
    )
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": sum(int(row["trial_count"]) for row in summaries),
        "separation_count": len(SEPARATIONS_KHZ),
        "relative_amplitude_count": len(RELATIVE_TONE_2_DB),
        "trials_per_condition": TRIALS_PER_CONDITION,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "bin_spacing_hz": float(SAMPLE_RATE) / int(NUM_SAMPLES),
        "configured_minimum_spacing_khz": CONFIGURED_MINIMUM_SPACING_KHZ,
        "minimum_resolution_probability": MINIMUM_RESOLUTION_PROBABILITY,
        "maximum_sublimit_resolution_probability": MAXIMUM_SUBLIMIT_RESOLUTION_PROBABILITY,
        "equal_amplitude_minimum_probability_at_or_above_limit": minimum_above,
        "equal_amplitude_maximum_probability_below_limit": maximum_below,
        "equal_amplitude_maximum_p95_frequency_error_hz": maximum_p95_error,
        "validated_boundary_khz_by_relative_amplitude": {
            str(relative_db): find_validated_boundary(summaries, relative_db)
            for relative_db in RELATIVE_TONE_2_DB
        },
        "result": "PASS" if passed else "FAIL",
        "claim_scope": "Synthetic two-tone resolution through the unchanged FFT and raw peak detector",
        "excluded_claims": "Modulated-signal resolution, hardware selectivity, temporal confirmation, and calibrated dynamic range",
    }


def write_csv(path: Path, rows: list[dict[str, object]], fields) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_resolution(path: Path, summaries: list[dict[str, object]]) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    colors = ("#00AEEA", "#7C5CFC", "#F0446E")
    for relative_db, color in zip(RELATIVE_TONE_2_DB, colors):
        rows = [row for row in summaries if float(row["relative_tone_2_db"]) == relative_db]
        axis.plot(
            [float(row["tone_separation_khz"]) for row in rows],
            [100.0 * float(row["both_detected_probability"]) for row in rows],
            "o-", linewidth=2, color=color, label=f"Tone 2 {relative_db:.0f} dB",
        )
    axis.axvline(75.0, color="#FFBF00", linestyle="--", label="Configured 75 kHz spacing")
    axis.axhline(95.0, color="#64748B", linestyle=":", label="95% resolution criterion")
    axis.set(
        title="Two-Tone Resolution Probability vs Tone Separation",
        xlabel="Tone separation (kHz)", ylabel="Both tones detected (%)",
        ylim=(-3, 103),
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="lower right")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def plot_frequency_error(path: Path, summaries: list[dict[str, object]]) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    colors = ("#00AEEA", "#7C5CFC", "#F0446E")
    for relative_db, color in zip(RELATIVE_TONE_2_DB, colors):
        rows = [
            row for row in summaries
            if float(row["relative_tone_2_db"]) == relative_db
            and row["p95_absolute_frequency_error_hz"] != "NA"
        ]
        axis.plot(
            [float(row["tone_separation_khz"]) for row in rows],
            [float(row["p95_absolute_frequency_error_hz"]) for row in rows],
            "o-", linewidth=2, color=color, label=f"Tone 2 {relative_db:.0f} dB",
        )
    axis.axhline(
        float(SAMPLE_RATE) / int(NUM_SAMPLES), color="#FFBF00",
        linestyle="--", label="One-bin matching limit",
    )
    axis.set(
        title="Resolved-Tone Frequency Error",
        xlabel="Tone separation (kHz)", ylabel="95th-percentile absolute error (Hz)",
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper right")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def plot_examples(path: Path) -> None:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    frequency_axis_hz = np.fft.fftshift(
        np.fft.fftfreq(fft_size, d=1.0 / sample_rate)
    )
    frequency_axis_mhz = frequency_axis_hz / 1e6
    figure, axes = plt.subplots(2, 1, figsize=(10.0, 7.0), sharex=False)
    for axis, separation_khz, seed, title in (
        (axes[0], 100.0, BASE_SEED + 90_001, "Resolved example: 100 kHz separation"),
        (axes[1], 50.0, BASE_SEED + 90_002, "Unresolved example: 50 kHz separation"),
    ):
        rng = np.random.default_rng(seed)
        samples, tone_1_hz, tone_2_hz = generate_trial(
            rng, separation_khz, 0.0, fft_size, sample_rate
        )
        power_db = compute_windowed_fft(samples)
        peaks, threshold = detect_peaks(power_db, frequency_axis_mhz)
        center_hz = (tone_1_hz + tone_2_hz) / 2.0
        mask = np.abs(frequency_axis_hz - center_hz) <= 125_000.0
        axis.plot(frequency_axis_hz[mask] / 1000.0, power_db[mask], color="#A900F5", linewidth=1.2, label="FFT")
        axis.plot(frequency_axis_hz[mask] / 1000.0, threshold[mask], color="#F59E0B", linewidth=1.0, label="Adaptive threshold")
        axis.axvline(tone_1_hz / 1000.0, color="#00B894", linestyle="--", label="True tones")
        axis.axvline(tone_2_hz / 1000.0, color="#00B894", linestyle="--")
        local_peaks = [peak for peak in peaks if abs(float(peak[0]) * 1e6 - center_hz) <= 125_000.0]
        if local_peaks:
            axis.scatter(
                [float(peak[0]) * 1000.0 for peak in local_peaks],
                [float(peak[1]) for peak in local_peaks],
                marker="v", s=70, color="#EF476F", label="Returned peaks", zorder=5,
            )
        axis.set(title=title, xlabel="Baseband frequency (kHz)", ylabel="Relative FFT level (dB)")
        axis.grid(True, alpha=0.22)
        axis.legend(loc="upper right")
    figure.suptitle("AV-PD-03: Resolved and Unresolved Two-Tone Examples")
    figure.tight_layout(rect=(0, 0, 1, 0.95))
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
    write_csv(args.output_dir / f"{prefix}_two_tone_trials.csv", rows, TRIAL_FIELDS)
    write_csv(
        args.output_dir / f"{prefix}_spacing_summary.csv",
        summaries, summaries[0].keys(),
    )
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    plot_resolution(args.output_dir / f"{prefix}_resolution_probability.png", summaries)
    plot_frequency_error(args.output_dir / f"{prefix}_frequency_error.png", summaries)
    plot_examples(args.output_dir / f"{prefix}_resolved_unresolved_examples.png")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
