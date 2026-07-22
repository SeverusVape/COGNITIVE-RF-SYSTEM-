# AV-OCC-01 — Synthetic Occupancy Validation

## Result

**PASS.**

The existing occupancy function was exercised without modification using 900
deterministic controlled-bin trials. Each trial contained 8,192 spectral bins
and an independently varying per-bin threshold.

## Method

Nine requested occupancy levels were tested: 0%, 1%, 5%, 10%, 25%, 50%, 75%,
90%, and 100%. Integer occupied-bin counts were arranged as either one
contiguous cluster or a distribution across the spectrum. Fifty randomized
trials were executed per level and layout. Unoccupied bins were strictly below
their corresponding thresholds and occupied bins were strictly above them.

The exact reference was the realized integer-bin fraction rather than the
nominal requested percentage, avoiding quantization ambiguity at 8,192 bins.

## Findings

- Maximum absolute measurement error: **0.0 percentage points**.
- Maximum repeatability standard deviation: **0.0%**.
- Maximum clustered-versus-distributed difference: **0.0 percentage points**.
- All 900 trials matched the exact occupied-bin fraction.

## Engineering interpretation

The implemented occupancy calculation correctly reports the fraction of bins
strictly above their associated thresholds. It is invariant to whether occupied
bins are clustered or distributed because spatial arrangement is intentionally
not part of the metric.

This validates **measurement-window spectral-bin occupancy only**. It is not
regulatory occupancy, time occupancy, channel utilization, calibrated RF power,
or hardware repeatability.

## Reproduction

```bash
.venv/bin/python VALIDATION/scripts/run_av_occ_01.py \
  --output-dir VALIDATION/results/AV-OCC-01_CFG-S01_20260722
```

## Artifacts

- `AV-OCC-01_CFG-S01_occupancy_trials.csv` — 900 raw trials;
- `AV-OCC-01_CFG-S01_occupancy_summary.csv` — condition statistics;
- `AV-OCC-01_CFG-S01_summary.json` — frozen settings and result;
- `AV-OCC-01_CFG-S01_occupancy_accuracy.png` — expected versus measured plot;
- `AV-OCC-01_CFG-S01_occupancy_error.png` — error by condition;
- `AV-OCC-01_CFG-S01_report.xlsx` — auditable workbook.
