# AV-PD-02 — Noise-Only False-Alarm Characterization

## Method

The existing coherent-gain-corrected Hann FFT and adaptive peak detector were
evaluated without RTL-SDR hardware. The experiment used 1,000 deterministic
signal-free complex-IQ frames:

- 500 circular complex Gaussian flat-noise frames.
- 500 complex Gaussian frames with a deterministic slow baseline composed of
  a 4 dB tilt and 6 dB sinusoidal variation.

Every candidate returned by `detect_peaks()` was counted as a false alarm. No
detector parameters or application source files were changed.

## Frozen acceptance criteria

- Frame false-alarm probability: at most 5%.
- Mean returned false candidates: at most 0.10 per frame.
- Frames reaching the detector's three-candidate cap: at most 1%.

## Result — FAIL

| Condition | Frames | Frame false-alarm probability | Mean candidates/frame | Frames at cap | Median maximum excess |
| --- | ---: | ---: | ---: | ---: | ---: |
| Flat noise | 500 | 100.0% | 3.00 | 100.0% | 4.24 dB |
| Uneven baseline | 500 | 100.0% | 3.00 | 100.0% | 3.66 dB |

The existing raw detector selected three statistical maxima in every
signal-free frame. Therefore the claim that the configured adaptive threshold
alone bounds noise-only false candidates is not supported.

This result is intentionally retained. It characterizes raw detector
specificity and does not mean the application displays three persistent false
signals per frame: downstream peak confirmation and history logic apply
temporal evidence that is outside this experiment. It also does not invalidate
the AV-PD-01 probability-of-detection result.

## Reproduction

```bash
.venv/bin/python VALIDATION/scripts/run_av_pd_02.py \
  --output-dir VALIDATION/results/AV-PD-02_CFG-S01_20260722
```

The raw CSV is deterministic except for its ISO timestamp. A second run matched
all trial values and the complete condition summary after timestamp exclusion.
The repository regression suite passed 138 tests.
