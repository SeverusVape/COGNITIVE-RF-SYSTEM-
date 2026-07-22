# AV-PD-03 — Two-Tone Resolution Validation

## Objective

Characterize whether the unchanged detector resolves two simultaneous synthetic tones above, at, and below its configured 75 kHz minimum peak spacing.

## Method

The experiment exercised the existing Hann-window FFT, adaptive local noise-floor threshold, and raw peak detector without parameter changes. Each trial contained two unmodulated complex tones in circular complex Gaussian noise.

The frozen protocol used:

- 12 separations: 25, 50, 62.5, 70, 74, 75, 76, 80, 87.5, 100, 125, and 150 kHz;
- three secondary-tone relative levels: 0, −6, and −12 dB;
- primary-tone input SNR of −10 dB under the existing pre-window complex-noise convention;
- 50 deterministic trials per separation and relative level;
- 1,800 total trials;
- random off-bin midpoint frequency and independent tone phases;
- unique detector-to-tone assignment within one 250 Hz FFT bin.

The formal pass criterion was frozen for equal-amplitude tones:

1. at least 95% joint detection at every tested separation of 75 kHz or greater;
2. no more than 5% joint detection at every tested separation below 75 kHz;
3. 95th-percentile absolute frequency error no greater than one FFT bin.

Unequal-amplitude trials characterize amplitude influence and do not redefine the equal-amplitude resolution claim.

## Results

**Overall result: PASS**

| Separation range | Equal amplitude | Tone 2 at −6 dB | Tone 2 at −12 dB |
| --- | ---: | ---: | ---: |
| 74 kHz and below | 0% jointly resolved | 0% jointly resolved | 0% jointly resolved |
| 75 kHz | 100% | 98% | 98% |
| 76–150 kHz | 100% | 100% | 100% |

The validated resolution boundary was 75 kHz for all three tested relative levels under the frozen 95% criterion. The equal-amplitude minimum joint-detection probability at or above the configured limit was 100%, while the maximum below the limit was 0%.

The maximum equal-amplitude 95th-percentile absolute frequency error was 121.8 Hz, below the 250 Hz FFT-bin limit. Across all relative-level cases, resolved-tone 95th-percentile errors remained approximately 106–126 Hz.

Below 75 kHz the detector returned only one of the two local signal responses. With equal tones, either tone was retained with roughly equal probability. With a weaker secondary tone, the stronger primary tone was consistently retained and the secondary tone was suppressed by the configured peak-distance constraint.

## Engineering interpretation

The detector displays a sharp synthetic transition aligned with its configured 75 kHz minimum peak distance. The result validates that two stable, narrowband tones meeting the tested SNR conditions are resolved at the configured boundary, while tones below that boundary are intentionally not represented as two detector outputs.

The 98% result at exactly 75 kHz for the −6 and −12 dB cases shows a small boundary sensitivity when one peak is weaker. Moving only 1 kHz above the configured distance restored 100% joint detection in the tested data. Therefore, 75 kHz is a validated nominal boundary, not a guarantee for every possible amplitude, SNR, modulation, or spectral-leakage condition.

## Reproducibility and regression verification

The deterministic rerun matched all 1,800 raw trial records after timestamp normalization, all 36 spacing-summary records, and the JSON result. The existing automated suite also passed: 138 tests.

## Scope and limitations

This is synthetic algorithm validation using unmodulated tones at fixed SNR. It does not establish RTL-SDR hardware selectivity, modulated-signal resolution, temporal-confirmation behavior, adjacent-channel rejection, calibrated dynamic range, or performance below the secondary-tone level tested here.

## Reproduction

From the repository root:

```text
.venv/bin/python VALIDATION/scripts/run_av_pd_03.py \
  --output-dir VALIDATION/results/AV-PD-03_CFG-S01_20260722
```

## Evidence files

- `AV-PD-03_CFG-S01_two_tone_trials.csv` — raw trial data;
- `AV-PD-03_CFG-S01_spacing_summary.csv` — separation/amplitude summaries;
- `AV-PD-03_CFG-S01_summary.json` — frozen configuration and overall result;
- `AV-PD-03_CFG-S01_resolution_probability.png` — joint detection versus separation;
- `AV-PD-03_CFG-S01_frequency_error.png` — resolved-tone frequency error;
- `AV-PD-03_CFG-S01_resolved_unresolved_examples.png` — example FFT responses;
- `AV-PD-03_CFG-S01_report.xlsx` — review workbook with raw data and formulas.
