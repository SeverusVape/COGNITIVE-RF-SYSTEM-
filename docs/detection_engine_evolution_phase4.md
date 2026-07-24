# SPECTRA Detection Engine Evolution

## Phase 4 — Frozen Detector Comparison Protocol

**Protocol status:** Frozen before comparative execution  
**Validation ID:** `DE-CMP-01`  
**Configuration:** `CFG-C01`  
**Decision boundary:** Synthetic eligibility for hardware validation only

## Purpose

Phase 4 objectively compares SPECTRA's unchanged production adaptive detector
and the independent experimental OS-CFAR detector on identical deterministic
inputs.

The experiment may determine whether OS-CFAR is eligible for Phase 5 hardware
comparison. It cannot authorize production integration or replacement.

## Frozen Dataset

| Item | Frozen value |
| --- | ---: |
| Sample rate | 2.048 MS/s |
| FFT size | 8,192 |
| FFT-bin spacing | 250 Hz |
| Trials per scenario | 100 |
| Scenarios | 8 |
| Shared spectra | 800 |
| Detector evaluations | 1,600 |
| Base seed | 3,104,204 |
| Match tolerance | 1 FFT bin |
| Warmup calls | 5 per detector |

Both detectors receive the exact same read-only FFT arrays. Detector execution
order alternates by trial to reduce fixed ordering bias in runtime results.

## Frozen Detector Configurations

The adaptive detector is the production implementation in `SDR/detection.py`
with no parameter or logic changes.

The OS-CFAR configuration is:

| Parameter | Value |
| --- | ---: |
| Reference cells | 32 per side |
| Guard cells | 8 per side |
| Rank | 48 of 64, one-based |
| Linear threshold scale | 4.0 |
| Minimum peak distance | 75 kHz |
| Maximum peaks | 3 |
| Bandwidth drop | 15 dB |

## Frozen Metrics

- probability of detection with Wilson 95% interval;
- frame false-alarm rate with Wilson 95% interval;
- precision;
- recall;
- mean, median, and 95th-percentile runtime;
- runtime standard deviation and coefficient of variation;
- returned-count standard deviation;
- median, 95th-percentile, and standard deviation of matched frequency error;
- median finite detector threshold.

Expected and detected carriers use deterministic one-to-one nearest-frequency
matching. A returned peak that is not assigned to an expected carrier is a
false positive.

## Predeclared Synthetic Gates

| Gate | Requirement | Frozen criterion |
| --- | --- | --- |
| G1 | Material noise-only false-alarm reduction | OS-CFAR frame Pfa ≤ max(0.01, 50% of adaptive Pfa) |
| G2 | Single-carrier sensitivity | OS-CFAR Pd ≥ adaptive Pd − 0.05 |
| G3 | Weak carrier beside strong carrier | OS-CFAR recall ≥ adaptive recall − 0.10 |
| G4 | Closely spaced carriers | OS-CFAR recall ≥ adaptive recall − 0.05 |
| G5 | Non-ideal-scenario robustness | Mean OS-CFAR recall across edge, multiple-carrier, variable-floor, and Monte Carlo cases ≥ adaptive − 0.05 |
| G6 | Live runtime compatibility | Worst-scenario OS-CFAR p95 runtime ≤ 100 ms |

All six gates must pass before OS-CFAR is described as synthetically eligible
for hardware comparison.

The gates were selected to test the measured reason for considering a new
detector—false-candidate specificity—while bounding loss of useful production
behavior.

## Required Outputs

- raw paired-trial CSV;
- detector/scenario statistical summary CSV;
- predeclared gate-results CSV;
- frozen protocol JSON;
- detection, false-alarm, and runtime charts;
- auditable workbook;
- engineering summary.

## Limitations

- Inputs are synthetic unmodulated tones and noise.
- FFT levels are relative and are not calibrated dBm.
- Raw detector outputs are evaluated before temporal confirmation.
- The public three-peak cap remains in effect.
- Runtime applies to the recorded development system.
- Phase 4 does not validate live RF behavior.

No application source file imports or executes the comparison framework.

## Measured Result

Execution completed on 2026-07-24 under configuration `CFG-C01`.

- 800 deterministic spectra were generated across eight scenarios.
- Each spectrum was evaluated by both detectors, producing 1,600 detector
  evaluations.
- Five of the six predeclared gates passed.
- Gate G1 failed: both detectors produced an unmatched raw candidate in every
  noise-only frame (`Pfa = 1.000` for both).
- Detection sensitivity and recall were equivalent in the frozen scenarios.
- The worst observed p95 detector runtime was approximately `0.507 ms` for the
  adaptive detector and `14.422 ms` for OS-CFAR. Both remained below the
  predeclared `100 ms` compatibility limit.

The result does not support replacing the production adaptive detector with
the frozen OS-CFAR candidate. The candidate did not improve the raw
false-alarm behavior that motivated the comparison, despite meeting the
sensitivity, robustness, and runtime limits.

This is a valid negative engineering result. Detector parameters were not
retuned after observing the data, and the failed criterion was not relaxed.
The production detector remains unchanged.

## Evidence Package

The auditable evidence is stored in
`VALIDATION/results/DE-CMP-01_CFG-C01_20260724/` and includes:

- paired raw-trial data;
- per-scenario statistical summaries with 95% Wilson intervals;
- decision-gate results;
- frozen-protocol metadata;
- detection, false-alarm, and runtime figures;
- an engineering summary;
- a multi-sheet comparison workbook with visual QA previews.
