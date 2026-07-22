# AV-FFT-01 Result — Synthetic FFT Frequency Accuracy

## Outcome

**PASS**

All 25 deterministic bin-centered complex-tone trials were placed on the
expected shifted FFT bin by the existing application FFT implementation.

## Frozen configuration

- Configuration: `CFG-S01`
- Sample rate: 2.048 MSPS
- FFT length: 8192 complex samples
- FFT-bin spacing: 250 Hz
- Window: Hann with coherent-gain compensation
- Tone offsets from center: -768, -384, 0, 384, and 768 kHz
- Repetitions: 5 randomized phases per offset
- Seed policy: base seed 3102026 plus zero-based trial index
- Acceptance limit: ±125 Hz (one-half FFT bin)

## Results

| Metric | Result |
| --- | ---: |
| Trials | 25 |
| Passed | 25 |
| Failed | 0 |
| Mean signed error | 0.0 Hz |
| Error standard deviation | 0.0 Hz |
| Maximum absolute error | 0.0 Hz |

## Engineering interpretation

The result verifies numerical FFT-axis placement for bin-centered synthetic
complex tones across most of the configured 2.048 MHz span. It also shows that
randomized starting phase does not alter the selected peak bin under these
conditions.

This result does **not** validate:

- RTL-SDR oscillator or tuner frequency accuracy
- Off-bin frequency interpolation
- Receiver sensitivity
- Calibrated power or dBm accuracy
- Detector performance in noise

Those claims require separate validation IDs.

## Evidence files

- `AV-FFT-01_CFG-S01_fft_frequency_trials.csv`: immutable raw trial records
- `AV-FFT-01_CFG-S01_summary.csv`: compact machine-readable summary
- `AV-FFT-01_CFG-S01_summary.json`: processing-friendly summary
- `AV-FFT-01_CFG-S01_frequency_error.png`: final-report figure
- `AV-FFT-01_CFG-S01_report.xlsx`: auditable raw-data and formula-backed report
- `AV-FFT-01_CFG-S01_report_preview.png`: workbook visual-QA rendering
