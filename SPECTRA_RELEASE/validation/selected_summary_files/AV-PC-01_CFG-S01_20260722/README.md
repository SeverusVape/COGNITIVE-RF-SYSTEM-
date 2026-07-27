# AV-PC-01 — Temporal Confirmation False-Alarm Validation

## Objective

Determine whether the existing temporal peak-confirmation stage suppresses the raw noise candidates observed by AV-PD-02 sufficiently to support this claim:

> Under deterministic noise-only input, the complete detection chain produces a bounded confirmed false-signal rate.

## Method

The test exercised the unchanged application chain:

1. deterministic complex noise generation;
2. existing Hann-window FFT processing;
3. existing adaptive noise-floor and raw peak detector;
4. existing `PeakConfirmer` temporal confirmation.

Two AV-PD-02 noise conditions were reused: flat noise and uneven-baseline noise. Each condition used 50 independent 100-frame observation windows (5,000 frames per condition; 10,000 total). Consecutive frames within each window were processed by one confirmer instance. The confirmer was reset only between independent windows.

Application parameters were frozen at two required hits in a three-frame confirmation window with 25 kHz matching tolerance. No detector, confirmation, SDR, or UI parameters were changed.

## Frozen acceptance criteria

Each noise condition was required to satisfy all of the following:

- confirmed false-signal frame probability no greater than 5%;
- mean confirmed false signals per frame no greater than 0.05;
- raw-to-confirmed suppression ratio of at least 95%;
- 95th-percentile confirmed false signals per 100-frame window no greater than 5.

Frequency persistence was reported as supporting evidence and was not used to override a rate failure.

## Results

| Condition | Raw candidates | Confirmed false signals | Confirmed-frame probability | Mean confirmed/frame | Mean confirmed/window | p95 confirmed/window | Suppression | Maximum persistence |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Flat noise | 15,000 | 2,114 | 37.30% | 0.4228 | 42.28 | 51.65 | 85.91% | 3 frames |
| Uneven baseline | 15,000 | 8,288 | 91.22% | 1.6576 | 165.76 | 177.55 | 44.75% | 9 frames |

**Overall result: FAIL**

The result was reproduced with the same deterministic seeds. All 10,000 frame records, 100 window summaries, two condition summaries, and the JSON summary matched a second run after timestamp normalization. The complete existing automated suite also passed: 138 tests.

## Engineering interpretation

Temporal confirmation suppresses part of the raw detector output, but the suppression is not sufficient under either frozen noise-only condition. Flat noise still produces confirmed candidates in 37.3% of frames. The uneven-baseline condition is more severe: persistent spectral structure causes locally aligned noise maxima to recur within the 25 kHz confirmation tolerance, producing confirmed candidates in 91.22% of frames.

The 2-of-3 temporal rule therefore does not establish the proposed bounded false-signal claim at the frozen limits. This is a validation finding, not a software failure, and the detector was deliberately left unchanged. AV-PD-02 remains unchanged.

## Scope and limitations

This experiment validates the synthetic chain through `PeakConfirmer`. It does not validate signal-history aging, classifier behavior, hardware interference, calibrated sensitivity, or the final false-signal rate perceived in every UI context. The deterministic noise models are controlled stress conditions rather than a complete model of the RTL-SDR environment.

## Reproduction

From the repository root:

```text
.venv/bin/python VALIDATION/scripts/run_av_pc_01.py \
  --output-dir VALIDATION/results/AV-PC-01_CFG-S01_20260722
```

## Evidence files

- `AV-PC-01_CFG-S01_confirmation_frames.csv` — frame-level raw and confirmed results;
- `AV-PC-01_CFG-S01_confirmation_windows.csv` — observation-window summaries;
- `AV-PC-01_CFG-S01_condition_summary.csv` — condition-level acceptance metrics;
- `AV-PC-01_CFG-S01_summary.json` — frozen configuration and overall result;
- `AV-PC-01_CFG-S01_candidate_suppression.png` — raw versus confirmed candidate comparison;
- `AV-PC-01_CFG-S01_false_confirmation_timeline.png` — false-confirmation behavior over time;
- `AV-PC-01_CFG-S01_report.xlsx` — review workbook with raw data and summary.
