# SPECTRA Real-RF Detector Evaluation

## Purpose

The real-RF evaluation layer records complex RTL-SDR IQ frames once and
replays the same immutable dataset through SPECTRA's standalone detector
adapters. This supports objective comparison without changing production
application behavior or repeating an RF capture.

The production application continues to use the Adaptive Detector.
OS-CFAR remains standalone. This validation layer does not select a production
detector.

At the project level, the completed synthetic and REAL-RF reviews retain the
Adaptive Detector as SPECTRA's production detector. The REAL-RF campaign found
comparable capped top-three peak-selection behavior under the recorded
conditions while OS-CFAR required approximately 30–32 times greater mean
detector execution time than the Adaptive Detector. OS-CFAR remains an
independent research and validation baseline. This is an engineering production
decision, not a claim of detector accuracy or universal superiority.

## Architecture

```text
RTL-SDR
  |
  v
immutable complex-IQ dataset
  |
  v
windowed FFT replay + absolute frequency axis
  |
  v
existing DetectorAdapter callbacks
  |
  v
normalized detections and thresholds
  |
  v
objective JSON, CSV, NPZ, and text reports
```

The implementation is isolated in `VALIDATION/real_rf/`. It does not modify
the GUI, SDR worker, production detector, Survey, SMART, Feature Store, Signal
History, or tuning logic.

## Canonical Dataset Input

Raw complex IQ frames are the canonical recorded input. Each row of
`samples.npy` is one complete FFT input frame.

`compute_windowed_fft()` does not impose a fixed FFT length. Production
currently reads `NUM_SAMPLES` IQ values and uses that same value as its FFT
size. Because this equality is a system convention rather than an FFT-function
requirement, metadata stores both:

- `iq_samples_per_frame`
- `fft_size`

Schema version `1.0` requires these values to be equal. A future schema would
be required before introducing padding, truncation, overlap, or a different
FFT size.

## Dataset Layout

```text
VALIDATION/real_rf/datasets/<dataset-id>/
    metadata.json
    samples.npy
```

Datasets and reports are excluded from Git because IQ and threshold arrays may
be large. Captured datasets are engineering evidence and should be backed up
outside the repository when they must be retained.

### Required Metadata

The JSON metadata records:

- schema version
- dataset ID
- UTC timestamp
- scenario and operator notes
- center frequency in Hz
- sample rate in Hz
- gain or `auto`
- IQ samples per frame
- FFT size
- frame count
- total sample count
- measured capture duration
- detector input type
- preprocessing function
- FFT window convention
- array filename, dtype, and shape

The IQ file must be a finite, two-dimensional complex NumPy array whose dtype
and shape exactly match the metadata.

## Capture Workflow

The capture utility is standalone and does not use the production GUI:

```bash
.venv/bin/python -m VALIDATION.real_rf.capture \
  --scenario "FM broadcast observation" \
  --center-mhz 100.0 \
  --frames 100 \
  --samples-per-frame 8192 \
  --gain auto
```

Optional arguments include:

- `--output-root`
- `--dataset-id`
- `--notes`
- `--sample-rate`

The utility:

1. validates arguments before opening hardware;
2. on macOS, discovers `librtlsdr.dylib` in the standard Apple Silicon or
   Intel Homebrew prefix without requiring a shell-level
   `DYLD_LIBRARY_PATH`;
3. opens the receiver through the existing `SDRManager`;
4. reads the declared number of exact-size IQ frames;
5. rejects missing, malformed, non-complex, or non-finite frames;
6. creates the dataset only after the complete capture succeeds;
7. prevents replacement of an existing dataset; and
8. closes the receiver on every success or failure path.

A failed capture does not produce a partial dataset.
The library-path adjustment is local to the initial standalone import and is
removed immediately afterward. Linux and Windows retain the normal
`pyrtlsdr` loading behavior.

## Replay Workflow

`load_dataset()` validates both files and memory-maps `samples.npy` read-only.
For each IQ frame, replay:

1. calls the existing `compute_windowed_fft()` function;
2. applies the existing Hann window and coherent-gain compensation;
3. produces shifted relative FFT magnitude in dB;
4. calls the existing production frequency-axis builder with the recorded
   FFT size, sample rate, and center frequency; and
5. presents read-only `power_db` and `freqs_mhz` arrays to detector adapters.

Repeated replay of an unchanged dataset produces identical detector input.

## Detector Comparison

Run the default Adaptive and OS-CFAR adapters with:

```bash
.venv/bin/python -m VALIDATION.real_rf.comparison \
  VALIDATION/real_rf/datasets/<dataset-id> \
  --repetitions 2
```

Existing reports are protected from accidental replacement. To intentionally
remove and regenerate the complete report set for a dataset, add `--force`:

```bash
.venv/bin/python -m VALIDATION.real_rf.comparison \
  VALIDATION/real_rf/datasets/<dataset-id> \
  --repetitions 2 \
  --force
```

The comparison layer reuses `DetectorAdapter` and
`build_detector_adapters()` from `VALIDATION/detector_evaluation.py`. There is
no second adapter framework.

Each detector receives the exact same replay arrays. Detector-only runtime is
measured around the detector callback and excludes disk loading and FFT
preprocessing.

Each normalized detection contains:

- frequency in MHz
- relative peak power in dB
- estimated bandwidth in kHz

Each detector result also records runtime, detection count, threshold
statistics, and a reference to the complete threshold-array artifact.

## Generated Reports

```text
VALIDATION/real_rf/reports/<dataset-id>/
    adaptive_results.json
    adaptive_thresholds.npz
    os_cfar_results.json
    os_cfar_thresholds.npz
    comparison.json
    detections.csv
    pairwise_comparison.csv
    summary.txt
```

The individual JSON reports contain normalized detections and per-frame
runtime. Compressed NPZ files retain complete threshold arrays without
expanding JSON files unnecessarily.

The pairwise table records:

- each detector's detection count
- detections matched within one FFT-bin width
- detections reported only by the first detector
- detections reported only by the second detector

Reports are collision-safe and are always stored separately from the source
dataset.

## Interpretation Limits

An uncontrolled real-RF capture normally has no complete detection ground
truth. Therefore:

- agreement between detectors is not proof that either detector is correct;
- a detector-only response is not automatically a false alarm;
- no probability of detection is calculated;
- no false-alarm probability is calculated;
- relative FFT values are not calibrated dBm;
- runtime applies to the recorded computer and software environment; and
- the comparison engine does not declare a winning detector.

Ground-truth accuracy metrics require a separately documented reference source
and experiment protocol. This framework does not infer or fabricate them.

## Engineering Decision Boundaries

**Detector certification** verifies one detector's implementation, input
handling, output contract, determinism, and unit-test coverage.

**Detector evaluation** measures one detector on declared datasets and
conditions.

**Detector comparison** gives multiple detectors identical input and presents
their observed differences.

**Production detector selection** is a separate engineering decision based on
predeclared requirements and appropriate evidence. Running this framework does
not change SPECTRA's production detector.

## Tests

`tests/test_real_rf_validation.py` verifies:

- metadata and array-schema validation;
- separate IQ-frame and FFT-size metadata;
- collision-safe dataset creation;
- rejection of malformed and corrupted datasets;
- immutable loading and replay;
- exact use of existing FFT and frequency-axis functions;
- deterministic repeated replay;
- hardware-free capture through an injected manager;
- receiver closure and absence of partial output on failure;
- identical read-only detector input;
- reuse of existing Adaptive and OS-CFAR adapters;
- normalized output and complete threshold artifacts;
- deterministic detector output checks;
- collision-safe report generation; and
- explicit absence of unsupported accuracy or winner claims.

## Known Limitations

- Schema `1.0` requires non-overlapping IQ frames whose length equals the FFT
  size.
- Captures use one center frequency, sample rate, and gain setting per
  dataset.
- The utility does not schedule retunes or multi-band surveys.
- Large captures require external storage management.
- The current pairwise matching tolerance is one FFT-bin width.
- Cross-detector matching is descriptive and is not ground truth.
- No production application or GUI integration is provided or intended.
