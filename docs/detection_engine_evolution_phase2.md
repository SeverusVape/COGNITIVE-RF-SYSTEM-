# SPECTRA Detection Engine Evolution

## Phase 2 — Independent OS-CFAR Implementation

**Status:** Completed and certified independent candidate detector

**Production detector:** `SDR/detection.py` remains unchanged

**Independent candidate detector:** `SDR/os_cfar.py`

## Scope

Phase 2 provides an independently callable Ordered Statistics CFAR detector
for a future controlled comparison with SPECTRA's existing adaptive detector.
The implementation and focused certification are complete. Completion means
that the detector contract, numerical validation, threshold calculation,
detection behavior, bandwidth convention, determinism, and isolation are
covered by automated tests. It does not mean OS-CFAR has been selected.

The application does not import or execute the OS-CFAR module. Survey, SMART,
occupancy, history, classification, FFT, waterfall, and UI behavior are
therefore unchanged.

Detector comparison and final production selection are separate activities.
The adaptive detector remains SPECTRA's production detector.

## Public Interface

```python
detect_peaks(
    power_db,
    freqs_mhz,
    config=None
) -> (results, threshold)
```

This return structure matches the production detector:

- `results` is a list of `(frequency_mhz, power_db, bandwidth_khz)` tuples;
- `threshold` is a per-bin relative-dB threshold array.

The compatible interface is for experimental comparison. It does not imply
that either detector has been selected.

### Input Contract

Both inputs must be one-dimensional, numeric arrays with equal lengths and at
least two bins. Power and frequency values must be finite. The frequency axis
may be strictly increasing or strictly decreasing; duplicate or non-monotonic
values are rejected. The spectrum must contain enough bins for complete
leading and lagging reference windows.

Programmer and configuration errors raise clear `ValueError` or `TypeError`
exceptions. The detector does not silently sanitize malformed FFT data.

### Output Contract

The threshold array is aligned one-to-one with the input spectrum. Each result
tuple contains:

1. selected FFT-bin frequency in MHz;
2. selected FFT-bin relative power in dB; and
3. estimated occupied bandwidth in kHz.

Results are ordered by descending peak power and limited by `maximum_peaks`.
The detector does not modify either input array.

## OS-CFAR Processing

For every valid cell under test:

1. collect a leading reference window;
2. skip the configured leading guard cells;
3. exclude the cell under test;
4. skip the configured lagging guard cells;
5. collect a lagging reference window;
6. combine and order the reference samples;
7. select the configured one-based rank;
8. apply the configured linear-power threshold scale;
9. compare the cell under test with the resulting relative-dB threshold.

Because ordering is invariant under a monotonic dB transform, the detector
selects the ranked reference value in dB and adds:

```text
10 log10(threshold_scale)
```

This is numerically equivalent to selecting and scaling the reference in
linear power, while avoiding unnecessary conversion of SPECTRA's relative FFT
values.

## Experimental Configuration

| Parameter | Default | Meaning |
| --- | ---: | --- |
| Reference cells | 32 per side | 64 total background samples |
| Guard cells | 8 per side | Signal-energy exclusion around the test cell |
| Rank | 48 | 48th-lowest of 64 reference samples |
| Threshold scale | 4.0 | Linear-power multiplier, approximately +6.02 dB |
| Minimum peak distance | 75 kHz | Matches current detector spacing |
| Maximum returned peaks | 3 | Matches current public behavior |
| Bandwidth drop | 15 dB | Matches current bandwidth heuristic |

These defaults are experimental starting values. They are not calibrated
production settings and do not establish a target false-alarm probability.
Phase 3 must test and, if justified, freeze comparison configurations before
the detector-selection experiment.

## Edge Policy

OS-CFAR is evaluated only where complete leading and lagging reference windows
exist. Edge bins without a complete window receive an infinite threshold and
cannot be detected.

This policy prevents a changing number of reference cells from silently
changing the selected statistic near FFT boundaries. Alternative edge
strategies may be compared later, but must not be introduced during a frozen
detector comparison.

## Bandwidth Estimation Convention

Bandwidth is estimated around each accepted peak using:

```text
bandwidth threshold = peak power - bandwidth_drop_db
```

The search includes the peak bin and every contiguous neighboring FFT bin
strictly above that level. Both the left and right boundaries are inclusive,
so:

```text
bandwidth bins = right included index - left included index + 1
bandwidth kHz = bandwidth bins × FFT-bin width kHz
```

Certification testing confirmed an earlier off-by-one defect: isolated and
interior multi-bin regions were reported one bin too wide. The boundary
search and inclusive bin count were corrected without changing CFAR threshold
generation, peak detection, ranking, configuration, defaults, or result
structure.

## Determinism and Isolation

Identical input arrays and configuration produce identical threshold arrays,
peak lists, peak ordering, and bandwidth values. Focused tests also prove that
threshold generation and detection do not mutate their input arrays.

`SDR/os_cfar.py` does not import the adaptive detector or any SDR, Survey,
SMART, Feature Store, Signal History, Validation, or UI subsystem. Importing
and invoking OS-CFAR does not alter the adaptive detector module's public
state.

## Computational Complexity

For `N` FFT bins and `R` reference cells per side, the current implementation
evaluates approximately `N - 2(R + G)` valid cells, builds `2R` reference
samples for each valid cell, and selects one order statistic with
`numpy.partition`.

For fixed detector configuration, runtime scales approximately linearly with
FFT length. In general terms, work is approximately `O(NR)`, while the
per-cell temporary reference storage is `O(R)`. Runtime remains measured
outside the detector, preserving the common `(results, threshold)` contract.
A non-strict 8,192-bin smoke test verifies that execution completes and
produces a finite, non-negative millisecond measurement without imposing a
machine-specific timing limit.

## Certification Test Coverage

`tests/test_os_cfar.py` verifies:

- focused validation of every `OSCFARConfig` field;
- dimensionality, length, finite-value, monotonic-axis, window-size, and
  configuration-type input validation;
- hand-calculated two-sided reference selection, CUT exclusion, guard-cell
  exclusion, one-based rank selection, and linear-scale dB conversion;
- threshold shape, explicit infinite edge thresholds, and input immutability;
- controlled noise-only, below-threshold, above-threshold, single-peak,
  multiple-peak, spacing, strongest-first, and maximum-output behavior;
- exact FFT-bin frequency and power reporting on increasing and decreasing
  axes;
- isolated, multi-bin, array-boundary, drop-controlled, finite, and
  non-negative bandwidth behavior;
- deterministic thresholds, peak results, ordering, and bandwidth;
- logical result-contract compatibility and isolation from the adaptive
  detector;
- representative 8,192-bin runtime smoke execution.

## Known Limitations

- Configuration does not establish a calibrated classical per-cell
  probability of false alarm.
- Performance depends on the selected rank, scale, window geometry, and RF
  environment.
- Complete-window edge exclusion creates intentional no-detection regions at
  both FFT boundaries.
- Closely spaced or wide signals may contaminate reference windows.
- Minimum peak spacing intentionally prevents sufficiently close local maxima
  from being returned independently.
- Bandwidth is a relative spectral-bin estimate, not a calibrated occupied
  bandwidth measurement.
- FFT power values remain relative and are not calibrated dBm.
- The Python per-cell implementation is slower than the current adaptive
  detector, although runtime selection is outside this certification task.

## Phase 2 Decision

The independent detector implementation is complete and certified for
controlled future evaluation.

It is not ready for:

- `main.py` integration;
- hardware selection;
- occupancy replacement;
- SMART evaluation;
- production claims;
- removal of the current detector.

The next approved detector phase should define a controlled comparison using
frozen, identical datasets and predeclared acceptance metrics. This document
makes no claim that OS-CFAR is superior and makes no production-selection
decision.
