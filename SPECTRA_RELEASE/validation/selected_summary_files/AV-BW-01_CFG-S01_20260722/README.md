# AV-BW-01 — Bandwidth Heuristic Validation

## Result

**FAIL for the complete 5–400 kHz test range.**

The existing detector and minus-15 dB bandwidth estimator were exercised
without parameter changes on 700 deterministic controlled-spectrum trials.
Both Gaussian and flat-top/cosine-edge responses were tested at analytical
minus-15 dB widths of 5, 10, 25, 50, 100, 200, and 400 kHz.

## Findings

- Widths from 5 through 200 kHz were detected in 100% of trials for both
  spectral-shape families.
- Every admitted response was estimated with a repeatable +0.25 kHz bias,
  equal to one 250 Hz FFT bin.
- The bias follows directly from the implemented boundary search: the reported
  span includes the first bin at or below the peak-minus-15 dB crossing.
- Neither 400 kHz shape was detected. The 250 kHz local noise-floor window sits
  inside the broad response, raising the adaptive threshold enough to prevent
  peak admission. Without a detected peak, the bandwidth heuristic is not run.
- This documents an upstream broad-signal limitation; it does not justify a
  detector change within this validation milestone.

## Engineering interpretation

The minus-15 dB estimator is highly repeatable and bin-resolution limited when
the existing detector admits a response. Its demonstrated synthetic operating
range in this experiment is 5–200 kHz. The full tested-range claim fails because
400 kHz responses are rejected by the adaptive detector, not because the width
walk produces a variable result.

This result is **not regulatory occupied bandwidth**. It does not validate
modulated-signal bandwidth, RTL-SDR analog bandwidth, receiver filter shape,
or calibrated RF measurements.

## Reproduction

```bash
.venv/bin/python VALIDATION/scripts/run_av_bw_01.py \
  --output-dir VALIDATION/results/AV-BW-01_CFG-S01_20260722
```

The random seed base, spectral shapes, widths, levels, FFT size, and acceptance
criteria are frozen in the runner and recorded in the JSON summary.

## Artifacts

- `AV-BW-01_CFG-S01_bandwidth_trials.csv` — 700 raw trials;
- `AV-BW-01_CFG-S01_bandwidth_summary.csv` — per-shape/per-width statistics;
- `AV-BW-01_CFG-S01_summary.json` — frozen configuration and overall result;
- `AV-BW-01_CFG-S01_estimated_vs_controlled.png` — accuracy and repeatability;
- `AV-BW-01_CFG-S01_bias.png` — mean estimator bias;
- `AV-BW-01_CFG-S01_shape_examples.png` — controlled spectral examples;
- `AV-BW-01_CFG-S01_report.xlsx` — auditable workbook summary.
