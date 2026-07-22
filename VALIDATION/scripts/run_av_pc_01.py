"""Run AV-PC-01 temporal-confirmation false-alarm validation."""

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
from SIGNALS.peak_confirmation import PeakConfirmer
from UTILS.config import (
    NUM_SAMPLES,
    PEAK_CONFIRMATION_REQUIRED_HITS,
    PEAK_CONFIRMATION_TOLERANCE_KHZ,
    PEAK_CONFIRMATION_WINDOW_FRAMES,
    SAMPLE_RATE,
)
from VALIDATION.scripts.run_av_pd_02 import CONDITIONS, make_noise


VALIDATION_ID = "AV-PC-01"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 3_103_026
WINDOWS_PER_CONDITION = 50
FRAMES_PER_WINDOW = 100
CONFIRMED_FRAME_PROBABILITY_LIMIT = 0.05
MEAN_CONFIRMED_FALSE_PER_FRAME_LIMIT = 0.05
MINIMUM_SUPPRESSION_RATIO = 0.95
P95_CONFIRMED_FALSE_PER_WINDOW_LIMIT = 5.0

FRAME_FIELDS = (
    "validation_id", "configuration_id", "condition",
    "observation_window_id", "frame_index", "global_frame_index",
    "timestamp", "random_seed", "sample_rate_hz", "fft_size",
    "raw_peak_count", "frame_has_raw_candidates",
    "confirmed_false_count", "frame_has_confirmed_false",
    "confirmed_frequencies_mhz", "maximum_active_persistence_frames",
    "required_hits", "confirmation_window_frames",
    "confirmation_tolerance_khz", "valid", "notes",
)

WINDOW_FIELDS = (
    "validation_id", "configuration_id", "condition",
    "observation_window_id", "frame_count", "raw_candidate_count",
    "confirmed_false_count", "confirmed_false_frame_count",
    "raw_to_confirmed_suppression_ratio", "maximum_persistence_frames",
    "distinct_confirmed_frequency_tracks", "valid", "notes",
)


def update_persistence_tracks(
        confirmed_peaks,
        previous_tracks: list[dict[str, float | int]],
        tolerance_mhz: float,
        next_track_id: int,
) -> tuple[list[dict[str, float | int]], int, int]:
    current_tracks: list[dict[str, float | int]] = []
    unused = set(range(len(previous_tracks)))

    for peak in confirmed_peaks:
        frequency = float(peak[0])
        candidates = [
            index for index in unused
            if abs(float(previous_tracks[index]["frequency_mhz"]) - frequency)
            <= tolerance_mhz
        ]
        if candidates:
            matched = min(
                candidates,
                key=lambda index: abs(
                    float(previous_tracks[index]["frequency_mhz"]) - frequency
                ),
            )
            unused.remove(matched)
            current_tracks.append({
                "track_id": int(previous_tracks[matched]["track_id"]),
                "frequency_mhz": frequency,
                "run_frames": int(previous_tracks[matched]["run_frames"]) + 1,
            })
        else:
            current_tracks.append({
                "track_id": next_track_id,
                "frequency_mhz": frequency,
                "run_frames": 1,
            })
            next_track_id += 1

    maximum_run = max(
        (int(track["run_frames"]) for track in current_tracks),
        default=0,
    )
    return current_tracks, next_track_id, maximum_run


def run_experiment() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    sample_rate = float(SAMPLE_RATE)
    fft_size = int(NUM_SAMPLES)
    frequency_axis_hz = np.fft.fftshift(
        np.fft.fftfreq(fft_size, d=1.0 / sample_rate)
    )
    frequency_axis_mhz = frequency_axis_hz / 1e6
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    tolerance_mhz = float(PEAK_CONFIRMATION_TOLERANCE_KHZ) / 1000.0
    frame_rows: list[dict[str, object]] = []
    window_rows: list[dict[str, object]] = []
    global_frame_index = 0

    for condition_index, condition in enumerate(CONDITIONS):
        for window_id in range(1, WINDOWS_PER_CONDITION + 1):
            confirmer = PeakConfirmer(
                required_hits=PEAK_CONFIRMATION_REQUIRED_HITS,
                window_frames=PEAK_CONFIRMATION_WINDOW_FRAMES,
                tolerance_khz=PEAK_CONFIRMATION_TOLERANCE_KHZ,
            )
            previous_tracks: list[dict[str, float | int]] = []
            next_track_id = 1
            observed_track_ids: set[int] = set()
            raw_total = 0
            confirmed_total = 0
            confirmed_frames = 0
            maximum_persistence = 0

            for frame_index in range(1, FRAMES_PER_WINDOW + 1):
                global_frame_index += 1
                seed = (
                    BASE_SEED
                    + condition_index * WINDOWS_PER_CONDITION * FRAMES_PER_WINDOW
                    + (window_id - 1) * FRAMES_PER_WINDOW
                    + frame_index - 1
                )
                rng = np.random.default_rng(seed)
                samples, _, _ = make_noise(rng, condition, fft_size)
                power_db = compute_windowed_fft(samples)
                raw_peaks, _ = detect_peaks(power_db, frequency_axis_mhz)
                confirmed_peaks = confirmer.update(raw_peaks)
                current_tracks, next_track_id, active_persistence = (
                    update_persistence_tracks(
                        confirmed_peaks,
                        previous_tracks,
                        tolerance_mhz,
                        next_track_id,
                    )
                )
                previous_tracks = current_tracks
                observed_track_ids.update(
                    int(track["track_id"]) for track in current_tracks
                )
                maximum_persistence = max(
                    maximum_persistence,
                    active_persistence,
                )
                raw_count = len(raw_peaks)
                confirmed_count = len(confirmed_peaks)
                raw_total += raw_count
                confirmed_total += confirmed_count
                confirmed_frames += int(confirmed_count > 0)
                frequency_text = (
                    ";".join(f"{float(peak[0]):.6f}" for peak in confirmed_peaks)
                    if confirmed_peaks else "NA"
                )
                frame_rows.append({
                    "validation_id": VALIDATION_ID,
                    "configuration_id": CONFIGURATION_ID,
                    "condition": condition,
                    "observation_window_id": window_id,
                    "frame_index": frame_index,
                    "global_frame_index": global_frame_index,
                    "timestamp": timestamp,
                    "random_seed": seed,
                    "sample_rate_hz": sample_rate,
                    "fft_size": fft_size,
                    "raw_peak_count": raw_count,
                    "frame_has_raw_candidates": str(raw_count > 0).lower(),
                    "confirmed_false_count": confirmed_count,
                    "frame_has_confirmed_false": str(confirmed_count > 0).lower(),
                    "confirmed_frequencies_mhz": frequency_text,
                    "maximum_active_persistence_frames": active_persistence,
                    "required_hits": PEAK_CONFIRMATION_REQUIRED_HITS,
                    "confirmation_window_frames": PEAK_CONFIRMATION_WINDOW_FRAMES,
                    "confirmation_tolerance_khz": PEAK_CONFIRMATION_TOLERANCE_KHZ,
                    "valid": "true",
                    "notes": "Consecutive noise-only frame; every confirmed peak is false",
                })

            suppression = 1.0 - confirmed_total / raw_total if raw_total else 1.0
            window_rows.append({
                "validation_id": VALIDATION_ID,
                "configuration_id": CONFIGURATION_ID,
                "condition": condition,
                "observation_window_id": window_id,
                "frame_count": FRAMES_PER_WINDOW,
                "raw_candidate_count": raw_total,
                "confirmed_false_count": confirmed_total,
                "confirmed_false_frame_count": confirmed_frames,
                "raw_to_confirmed_suppression_ratio": suppression,
                "maximum_persistence_frames": maximum_persistence,
                "distinct_confirmed_frequency_tracks": len(observed_track_ids),
                "valid": "true",
                "notes": (
                    "Persistence is consecutive confirmed-frame matching within 25 kHz"
                ),
            })

    return frame_rows, window_rows


def summarize(
        frame_rows: list[dict[str, object]],
        window_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for condition in CONDITIONS:
        frames = [row for row in frame_rows if row["condition"] == condition]
        windows = [row for row in window_rows if row["condition"] == condition]
        raw_counts = np.asarray([
            int(row["raw_peak_count"]) for row in frames
        ], dtype=float)
        confirmed_counts = np.asarray([
            int(row["confirmed_false_count"]) for row in frames
        ], dtype=float)
        window_confirmed = np.asarray([
            int(row["confirmed_false_count"]) for row in windows
        ], dtype=float)
        window_persistence = np.asarray([
            int(row["maximum_persistence_frames"]) for row in windows
        ], dtype=float)
        raw_total = int(np.sum(raw_counts))
        confirmed_total = int(np.sum(confirmed_counts))
        confirmed_frame_probability = float(np.mean(confirmed_counts > 0))
        mean_confirmed = float(np.mean(confirmed_counts))
        suppression = 1.0 - confirmed_total / raw_total if raw_total else 1.0
        p95_window = float(np.percentile(window_confirmed, 95))
        passed = (
            confirmed_frame_probability <= CONFIRMED_FRAME_PROBABILITY_LIMIT
            and mean_confirmed <= MEAN_CONFIRMED_FALSE_PER_FRAME_LIMIT
            and suppression >= MINIMUM_SUPPRESSION_RATIO
            and p95_window <= P95_CONFIRMED_FALSE_PER_WINDOW_LIMIT
        )
        summaries.append({
            "condition": condition,
            "observation_window_count": len(windows),
            "total_frames": len(frames),
            "frames_with_raw_candidates": int(np.sum(raw_counts > 0)),
            "raw_candidate_count": raw_total,
            "mean_raw_candidates_per_frame": float(np.mean(raw_counts)),
            "frames_with_confirmed_false": int(np.sum(confirmed_counts > 0)),
            "confirmed_false_count": confirmed_total,
            "confirmed_false_frame_probability": confirmed_frame_probability,
            "mean_confirmed_false_per_frame": mean_confirmed,
            "mean_confirmed_false_per_window": float(np.mean(window_confirmed)),
            "p95_confirmed_false_per_window": p95_window,
            "raw_to_confirmed_suppression_ratio": suppression,
            "maximum_persistence_frames": int(np.max(window_persistence)),
            "p95_maximum_persistence_frames": float(
                np.percentile(window_persistence, 95)
            ),
            "confirmed_frame_probability_limit": CONFIRMED_FRAME_PROBABILITY_LIMIT,
            "mean_confirmed_false_per_frame_limit": (
                MEAN_CONFIRMED_FALSE_PER_FRAME_LIMIT
            ),
            "minimum_suppression_ratio": MINIMUM_SUPPRESSION_RATIO,
            "p95_confirmed_false_per_window_limit": (
                P95_CONFIRMED_FALSE_PER_WINDOW_LIMIT
            ),
            "result": "PASS" if passed else "FAIL",
        })
    return summaries


def build_result(summaries: list[dict[str, object]]) -> dict[str, object]:
    passed = all(row["result"] == "PASS" for row in summaries)
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "conditions": list(CONDITIONS),
        "observation_windows_per_condition": WINDOWS_PER_CONDITION,
        "frames_per_window": FRAMES_PER_WINDOW,
        "total_frames": len(CONDITIONS) * WINDOWS_PER_CONDITION * FRAMES_PER_WINDOW,
        "sample_rate_hz": float(SAMPLE_RATE),
        "fft_size": int(NUM_SAMPLES),
        "required_hits": PEAK_CONFIRMATION_REQUIRED_HITS,
        "confirmation_window_frames": PEAK_CONFIRMATION_WINDOW_FRAMES,
        "confirmation_tolerance_khz": PEAK_CONFIRMATION_TOLERANCE_KHZ,
        "confirmed_frame_probability_limit": CONFIRMED_FRAME_PROBABILITY_LIMIT,
        "mean_confirmed_false_per_frame_limit": (
            MEAN_CONFIRMED_FALSE_PER_FRAME_LIMIT
        ),
        "minimum_suppression_ratio": MINIMUM_SUPPRESSION_RATIO,
        "p95_confirmed_false_per_window_limit": (
            P95_CONFIRMED_FALSE_PER_WINDOW_LIMIT
        ),
        "result": "PASS" if passed else "FAIL",
        "claim_scope": (
            "Synthetic noise-only specificity through FFT, raw detector, and "
            "unchanged temporal peak confirmation"
        ),
        "excluded_claims": (
            "Signal-history aging, classifier behavior, hardware interference, "
            "and displayed UI false-alarm rate"
        ),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fields) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_suppression(path: Path, summaries: list[dict[str, object]]) -> None:
    labels = [str(row["condition"]).replace("_", " ").title() for row in summaries]
    raw = np.asarray([
        float(row["mean_raw_candidates_per_frame"]) for row in summaries
    ])
    confirmed = np.asarray([
        float(row["mean_confirmed_false_per_frame"]) for row in summaries
    ])
    suppression = np.asarray([
        float(row["raw_to_confirmed_suppression_ratio"]) for row in summaries
    ]) * 100.0
    x = np.arange(len(labels))
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
    width = 0.34
    axes[0].bar(x - width / 2, raw, width, label="Raw", color="#00aeea")
    axes[0].bar(x + width / 2, confirmed, width, label="Confirmed", color="#ef476f")
    axes[0].set(
        title="Raw vs Confirmed Noise Candidates",
        ylabel="Mean candidates per frame",
        xticks=x,
        xticklabels=labels,
    )
    axes[0].legend()
    axes[1].bar(labels, suppression, color=["#00aeea", "#8b5cf6"])
    axes[1].axhline(
        MINIMUM_SUPPRESSION_RATIO * 100.0,
        color="#ffbf00", linestyle="--", label="95% criterion",
    )
    axes[1].set(
        title="Raw-to-Confirmed Suppression",
        ylabel="Suppression ratio (%)",
        ylim=(0, 105),
    )
    axes[1].legend(loc="lower right")
    for axis in axes:
        axis.grid(True, axis="y", alpha=0.25)
    figure.suptitle("AV-PC-01: Temporal Confirmation False-Alarm Suppression")
    figure.tight_layout(rect=(0, 0.05, 1, 0.93))
    figure.text(
        0.01, 0.01,
        "CFG-S01 | unchanged 2-of-3 confirmation | ±25 kHz tolerance",
        color="#64748b",
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def plot_timeline(path: Path, frame_rows: list[dict[str, object]]) -> None:
    figure, axes = plt.subplots(2, 1, figsize=(12.0, 6.8), sharex=True)
    for axis, condition in zip(axes, CONDITIONS):
        rows = [
            row for row in frame_rows
            if row["condition"] == condition
            and int(row["observation_window_id"]) == 1
        ]
        frames = [int(row["frame_index"]) for row in rows]
        raw = [int(row["raw_peak_count"]) for row in rows]
        confirmed = [int(row["confirmed_false_count"]) for row in rows]
        axis.step(frames, raw, where="mid", color="#00aeea", label="Raw")
        axis.step(
            frames, confirmed, where="mid", color="#ef476f",
            linewidth=1.8, label="Confirmed",
        )
        axis.set(
            title=condition.replace("_", " ").title(),
            ylabel="Candidates",
            ylim=(-0.15, 3.25),
        )
        axis.grid(True, alpha=0.25)
        axis.legend(loc="upper right")
    axes[-1].set_xlabel("Consecutive frame index")
    figure.suptitle("AV-PC-01: False-Confirmation Behavior Over Time")
    figure.tight_layout(rect=(0, 0.03, 1, 0.95))
    figure.savefig(path, dpi=180)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"{VALIDATION_ID}_{CONFIGURATION_ID}"
    frame_rows, window_rows = run_experiment()
    summaries = summarize(frame_rows, window_rows)
    result = build_result(summaries)
    write_csv(
        args.output_dir / f"{prefix}_confirmation_frames.csv",
        frame_rows,
        FRAME_FIELDS,
    )
    write_csv(
        args.output_dir / f"{prefix}_confirmation_windows.csv",
        window_rows,
        WINDOW_FIELDS,
    )
    write_csv(
        args.output_dir / f"{prefix}_condition_summary.csv",
        summaries,
        summaries[0].keys(),
    )
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    plot_suppression(
        args.output_dir / f"{prefix}_candidate_suppression.png",
        summaries,
    )
    plot_timeline(
        args.output_dir / f"{prefix}_false_confirmation_timeline.png",
        frame_rows,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
