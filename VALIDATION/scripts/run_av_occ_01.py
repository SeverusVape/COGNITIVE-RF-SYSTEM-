"""Run AV-OCC-01 synthetic spectral-bin occupancy validation."""

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

from UTILS.config import NUM_SAMPLES
from UTILS.occupancy import calculate_occupancy


VALIDATION_ID = "AV-OCC-01"
CONFIGURATION_ID = "CFG-S01"
BASE_SEED = 5_011_326
REQUESTED_OCCUPANCY_PERCENT = (0.0, 1.0, 5.0, 10.0, 25.0, 50.0, 75.0, 90.0, 100.0)
LAYOUTS = ("clustered", "distributed")
TRIALS_PER_CONDITION = 50
MAXIMUM_ERROR_PERCENTAGE_POINTS = 1e-9

TRIAL_FIELDS = (
    "validation_id", "configuration_id", "trial_id", "timestamp",
    "random_seed", "bin_count", "layout", "requested_occupancy_percent",
    "occupied_bin_count", "realized_expected_occupancy_percent",
    "measured_occupancy_percent", "measurement_error_percentage_points",
    "threshold_mode", "minimum_threshold_db", "maximum_threshold_db",
    "minimum_occupied_excess_db", "maximum_occupied_excess_db",
    "meter_filled_bar_count", "valid", "notes",
)


def occupied_indices(
        rng: np.random.Generator,
        bin_count: int,
        occupied_count: int,
        layout: str,
) -> np.ndarray:
    if occupied_count == 0:
        return np.asarray([], dtype=int)
    if occupied_count == bin_count:
        return np.arange(bin_count)
    if layout == "clustered":
        start = int(rng.integers(0, bin_count - occupied_count + 1))
        return np.arange(start, start + occupied_count)
    if layout == "distributed":
        offset = float(rng.uniform(0.0, 1.0))
        positions = ((np.arange(occupied_count) + offset) * bin_count / occupied_count)
        return np.floor(positions).astype(int) % bin_count
    raise ValueError(f"Unsupported layout: {layout}")


def count_meter_bars(meter: str) -> int:
    return meter.count("■")


def run_trials() -> list[dict[str, object]]:
    bin_count = int(NUM_SAMPLES)
    timestamp = datetime.now(timezone.utc).astimezone().isoformat()
    rows: list[dict[str, object]] = []
    trial_id = 0

    for layout in LAYOUTS:
        for requested_percent in REQUESTED_OCCUPANCY_PERCENT:
            for _ in range(TRIALS_PER_CONDITION):
                seed = BASE_SEED + trial_id
                rng = np.random.default_rng(seed)
                occupied_count = int(round(requested_percent * bin_count / 100.0))
                indices = occupied_indices(rng, bin_count, occupied_count, layout)

                # Exercise the supported per-bin threshold path. Values below and
                # above threshold are randomized while preserving exact truth.
                threshold = rng.uniform(18.0, 42.0, bin_count)
                power_db = threshold - rng.uniform(0.1, 15.0, bin_count)
                occupied_excess = rng.uniform(0.1, 20.0, occupied_count)
                power_db[indices] = threshold[indices] + occupied_excess

                measured, meter = calculate_occupancy(power_db, threshold)
                realized = 100.0 * occupied_count / bin_count
                error = measured - realized
                rows.append({
                    "validation_id": VALIDATION_ID,
                    "configuration_id": CONFIGURATION_ID,
                    "trial_id": trial_id + 1,
                    "timestamp": timestamp,
                    "random_seed": seed,
                    "bin_count": bin_count,
                    "layout": layout,
                    "requested_occupancy_percent": requested_percent,
                    "occupied_bin_count": occupied_count,
                    "realized_expected_occupancy_percent": realized,
                    "measured_occupancy_percent": measured,
                    "measurement_error_percentage_points": error,
                    "threshold_mode": "independent per-bin threshold",
                    "minimum_threshold_db": float(np.min(threshold)),
                    "maximum_threshold_db": float(np.max(threshold)),
                    "minimum_occupied_excess_db": (
                        float(np.min(occupied_excess)) if occupied_count else "NA"
                    ),
                    "maximum_occupied_excess_db": (
                        float(np.max(occupied_excess)) if occupied_count else "NA"
                    ),
                    "meter_filled_bar_count": count_meter_bars(meter),
                    "valid": "true",
                    "notes": "Expected value uses realized integer-bin fraction",
                })
                trial_id += 1
    return rows


def summarize(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for layout in LAYOUTS:
        for requested_percent in REQUESTED_OCCUPANCY_PERCENT:
            group = [
                row for row in rows
                if row["layout"] == layout
                and float(row["requested_occupancy_percent"]) == requested_percent
            ]
            expected = np.asarray([
                float(row["realized_expected_occupancy_percent"]) for row in group
            ])
            measured = np.asarray([
                float(row["measured_occupancy_percent"]) for row in group
            ])
            errors = measured - expected
            summaries.append({
                "layout": layout,
                "requested_occupancy_percent": requested_percent,
                "occupied_bin_count": int(group[0]["occupied_bin_count"]),
                "realized_expected_occupancy_percent": float(np.mean(expected)),
                "trial_count": len(group),
                "mean_measured_occupancy_percent": float(np.mean(measured)),
                "standard_deviation_percent": float(np.std(measured, ddof=1)),
                "mean_error_percentage_points": float(np.mean(errors)),
                "maximum_absolute_error_percentage_points": float(np.max(np.abs(errors))),
                "mean_meter_filled_bar_count": float(np.mean([
                    int(row["meter_filled_bar_count"]) for row in group
                ])),
            })
    return summaries


def build_result(summaries: list[dict[str, object]]) -> dict[str, object]:
    maximum_error = max(
        float(row["maximum_absolute_error_percentage_points"]) for row in summaries
    )
    maximum_std = max(float(row["standard_deviation_percent"]) for row in summaries)
    layout_differences = []
    for requested in REQUESTED_OCCUPANCY_PERCENT:
        values = [
            float(row["mean_measured_occupancy_percent"])
            for row in summaries
            if float(row["requested_occupancy_percent"]) == requested
        ]
        layout_differences.append(max(values) - min(values))
    maximum_layout_difference = max(layout_differences)
    passed = (
        maximum_error <= MAXIMUM_ERROR_PERCENTAGE_POINTS
        and maximum_std <= MAXIMUM_ERROR_PERCENTAGE_POINTS
        and maximum_layout_difference <= MAXIMUM_ERROR_PERCENTAGE_POINTS
    )
    return {
        "validation_id": VALIDATION_ID,
        "configuration_id": CONFIGURATION_ID,
        "trial_count": sum(int(row["trial_count"]) for row in summaries),
        "layout_count": len(LAYOUTS),
        "occupancy_level_count": len(REQUESTED_OCCUPANCY_PERCENT),
        "trials_per_condition": TRIALS_PER_CONDITION,
        "bin_count": int(NUM_SAMPLES),
        "maximum_allowed_error_percentage_points": MAXIMUM_ERROR_PERCENTAGE_POINTS,
        "maximum_absolute_error_percentage_points": maximum_error,
        "maximum_repeatability_standard_deviation_percent": maximum_std,
        "maximum_clustered_distributed_difference_percentage_points": maximum_layout_difference,
        "result": "PASS" if passed else "FAIL",
        "claim_scope": "Exact spectral-bin fraction above scalar or per-bin thresholds for deterministic synthetic spectra",
        "excluded_claims": "Regulatory occupancy, time occupancy, channel utilization, hardware repeatability, and RF calibration",
    }


def write_csv(path: Path, rows: list[dict[str, object]], fields) -> None:
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_accuracy(path: Path, summaries: list[dict[str, object]]) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    for layout, color, marker in (
        ("clustered", "#00AEEA", "o"),
        ("distributed", "#7C5CFC", "s"),
    ):
        group = [row for row in summaries if row["layout"] == layout]
        axis.plot(
            [float(row["realized_expected_occupancy_percent"]) for row in group],
            [float(row["mean_measured_occupancy_percent"]) for row in group],
            marker=marker, linewidth=2, color=color, label=layout.title(),
        )
    axis.plot((0, 100), (0, 100), "--", color="#FFBF00", label="Ideal reference")
    axis.set(
        title="Synthetic Spectral-Bin Occupancy Accuracy",
        xlabel="Expected occupied-bin fraction (%)",
        ylabel="Measured occupancy (%)",
        xlim=(-2, 102), ylim=(-2, 102),
    )
    axis.grid(True, alpha=0.25)
    axis.legend(loc="upper left")
    figure.tight_layout()
    figure.savefig(path, dpi=180)
    plt.close(figure)


def plot_error(path: Path, summaries: list[dict[str, object]]) -> None:
    figure, axis = plt.subplots(figsize=(8.8, 5.2))
    x = np.arange(len(REQUESTED_OCCUPANCY_PERCENT))
    width = 0.36
    for offset, layout, color in (
        (-width / 2, "clustered", "#00AEEA"),
        (width / 2, "distributed", "#7C5CFC"),
    ):
        group = [row for row in summaries if row["layout"] == layout]
        axis.bar(
            x + offset,
            [float(row["maximum_absolute_error_percentage_points"]) for row in group],
            width, color=color, label=layout.title(),
        )
    axis.set_xticks(x, [f"{value:g}" for value in REQUESTED_OCCUPANCY_PERCENT])
    axis.set(
        title="Maximum Occupancy Error by Condition",
        xlabel="Requested occupancy (%)", ylabel="Absolute error (percentage points)",
    )
    axis.grid(True, axis="y", alpha=0.25)
    axis.legend(loc="upper right")
    figure.tight_layout()
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
    write_csv(args.output_dir / f"{prefix}_occupancy_trials.csv", rows, TRIAL_FIELDS)
    write_csv(args.output_dir / f"{prefix}_occupancy_summary.csv", summaries, summaries[0].keys())
    (args.output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    plot_accuracy(args.output_dir / f"{prefix}_occupancy_accuracy.png", summaries)
    plot_error(args.output_dir / f"{prefix}_occupancy_error.png", summaries)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
