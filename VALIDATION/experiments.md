# Validation Experiments

## Experiment order

Complete algorithm validation before hardware validation. This establishes the
behavior of the processing algorithms under known inputs before adding RTL-SDR,
antenna, oscillator, gain, propagation, and environmental uncertainty.

## Stage 0 — Baseline freeze

### Purpose

Establish the exact software and measurement configuration used by all later
experiments.

### Procedure

1. Record the Git commit and working-tree status.
2. Run the full automated test suite and record its result.
3. Complete one row per setting in `configuration_record.csv`.
4. Assign the synthetic configuration `CFG-S01` and the first hardware
   configuration `CFG-H01`.
5. Photograph or record the RTL-SDR, antenna, cables, attenuators, termination,
   and signal source used.
6. Freeze source placement, receiver placement, and gain within each series.

### Baseline currently observed

- Git baseline: `73f06b9`
- Automated result at planning time: 138 tests passed
- Sample rate: 2.048 MSPS
- FFT length: 8192 samples
- FFT-bin spacing: 250 Hz
- Window: Hann with coherent-gain compensation
- Survey settling interval: 500 ms

## Part A — Algorithm validation using synthetic data

Synthetic tests must use complex IQ arrays and the current processing
functions. They validate algorithms; they do not validate the RTL-SDR hardware.

### A1. FFT frequency and window response

Validation IDs: `AV-FFT-01`, `AV-FFT-02`

1. Generate bin-centered complex tones at low, center-offset, and high FFT
   bins.
2. Generate tones offset by 0.25 and 0.5 bins.
3. Process each with the frozen sample rate, FFT length, and Hann window.
4. Record expected frequency, detected frequency, peak level, and leakage.
5. Repeat with randomized phase.

Completion evidence:

- Expected versus measured frequency table
- Frequency error summary
- Rectangular-versus-Hann leakage plot

### A2. Adaptive noise-floor tracking

Validation ID: `AV-NF-01`

Test conditions:

- Flat Gaussian noise baseline
- Slowly curved baseline
- One stepped baseline
- Each baseline with zero, one, and several narrow peaks

For every trial, retain the known baseline array, estimated local floor, and
threshold. Report median absolute floor error and worst regional error.

### A3. Detection probability and false alarms

Validation IDs: `AV-PD-01`, `AV-PD-02`

1. Select an SNR sweep before execution; recommended starting points are
   `-5, 0, 3, 6, 10, 15, 20 dB`.
2. Run at least 100 randomized tone-plus-noise trials per SNR.
3. Run at least 500 noise-only frames for flat noise and another 500 for an
   uneven baseline.
4. Count detections within the declared matching tolerance.
5. Record all false and missed detections.

Do not choose the final SNR convention after examining the results. State
whether SNR is defined by tone amplitude, integrated signal power, or power
above the local bin floor.

### A4. Two-tone resolution

Validation ID: `AV-PD-03`

1. Generate equal-amplitude tones with decreasing separation.
2. Repeat with one tone 6 dB and 12 dB below the other.
3. Include separations below, at, and above the configured 75 kHz peak spacing.
4. Record expected and detected peak counts and frequency errors.

This experiment documents a designed limitation; it is not required to prove
resolution below the configured minimum spacing.

### A5. Bandwidth heuristic

Validation ID: `AV-BW-01`

Use controlled spectral shapes rather than calling the result regulatory
occupied bandwidth. Suitable inputs include filtered noise and deterministic
multi-tone groups with known span. Record reported minus-15 dB width, bias, and
repeatability.

### A6. Synthetic occupancy

Validation ID: `AV-OCC-01`

Construct spectra with known proportions of bins above the corresponding local
threshold. Include 0%, low, medium, high, and 100% cases, plus clustered and
distributed occupied bins. Compare expected and measured spectral-bin
occupancy.

## Part B — Hardware/system validation using RTL-SDR

Hardware results apply only to the recorded configuration. Warm up the receiver
for 10–15 minutes unless warm-up behavior itself is under test.

### B1. Cold-start oscillator drift

Validation ID: `HV-FREQ-02`

1. Select the narrowest stable legal receive-only reference available.
2. Start with a receiver that has been disconnected long enough to cool.
3. Record one estimate approximately every 10 seconds for at least 20 minutes.
4. Do not retune, move the antenna, or change gain during the run.
5. Plot error from the reference and error from the session median.

### B2. Multi-frequency accuracy

Validation ID: `HV-FREQ-01`

1. Use at least three suitable known carriers when available.
2. Record why each reference is considered stable.
3. Collect at least 10 observations per carrier after warm-up.
4. Calculate signed error in kHz and approximate ppm.
5. Report mean, standard deviation, minimum, and maximum.

Wideband FM station assignments may be used with an explicit limitation, but a
narrow continuous carrier is a better frequency reference.

### B3. Relative amplitude linearity

Validation ID: `HV-AMP-01`

1. Use fixed receiver gain.
2. Use a stable source and unchanged geometry.
3. Apply at least three known attenuation levels, if equipment is available.
4. Collect at least 10 readings at each level.
5. Compare measured relative change with applied attenuation.

If known attenuation is unavailable, skip the linearity claim and complete only
the repeatability experiment. Never convert results to dBm.

### B4. Relative amplitude repeatability

Validation ID: `HV-AMP-02`

Collect at least 30 observations without changing source, gain, antenna,
frequency, or geometry. Report mean, standard deviation, range, and relative
peak-above-floor behavior.

### B5. Noise-floor and threshold characterization

Validation ID: `HV-NF-01`

Recommended conditions:

1. Terminated input, if a 50-ohm termination is available
2. Antenna connected in a quiet span
3. Antenna connected in an active span
4. A second fixed-gain setting, if practical

Record the local floor, displayed median threshold, occupancy, and peak count.
Discuss antenna response, receiver noise, automatic gain, DC artifacts, and
strong-signal influence.

### B6. Live occupancy comparison

Validation IDs: `HV-OCC-01`, `HV-OCC-02`

1. Select quiet and active spans with the same bandwidth and settings.
2. Collect at least 30 measurements per span.
3. If a controlled legal source is available, collect at least 20 source-OFF
   and 20 source-ON measurements.
4. Report mean, standard deviation, range, and effect size.

State that the result is measurement-window spectral-bin occupancy—not
regulatory channel occupancy or long-term spectrum utilization.

### B7. SMART survey repeatability

Validation IDs: `HV-SMART-01`, `HV-SMART-02`

1. Freeze antenna, gain, start, stop, step, and decision mode.
2. Run at least 10 surveys over 88–92 MHz.
3. Run at least 10 surveys over 115–121 MHz.
4. Save every candidate's occupancy and score components.
5. Record winner, runner-up, margin, and confidence classification.
6. Explain every winner change through the recorded score components.

Do not redesign weights in response to this experiment. The goal is to validate
and explain the current policy.

### B8. Event-driven survey sequence verification

Validation ID: `HV-SEQ-01`

Complete three normal hardware surveys and record successful point count,
requested/confirmed frequency agreement, completion status, and any device
errors. Pair this evidence with the existing automated sequence tests.

## Stop conditions

Stop and record the run as invalid if:

- Gain changes unintentionally
- The source or antenna moves
- The SDR disconnects or reports a tune/read failure
- Another program accesses the receiver
- Configuration identity is missing
- The source reference becomes unavailable
- Required measurement fields are non-finite

Invalid runs remain in the record with an explanatory note.

