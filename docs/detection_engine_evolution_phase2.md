# SPECTRA Detection Engine Evolution

## Phase 2 — Independent OS-CFAR Implementation

**Status:** Implementation complete; production integration not started  
**Production detector:** `SDR/detection.py` remains unchanged  
**Experimental detector:** `SDR/os_cfar.py`

## Scope

Phase 2 adds an independent Ordered Statistics CFAR detector for controlled
comparison with SPECTRA's existing adaptive detector.

The application does not import or execute the OS-CFAR module. Survey, SMART,
occupancy, history, classification, FFT, waterfall, and UI behavior are
therefore unchanged.

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

## Validation Added

`tests/test_os_cfar.py` verifies:

- default rank consistency;
- invalid configuration rejection;
- constant-floor threshold calculation;
- guard-cell exclusion;
- ordered-rank response to a reference outlier;
- insufficient-window rejection;
- peak detection and public return compatibility;
- strongest-peak limiting;
- explicit FFT-edge exclusion;
- descending frequency-axis support;
- non-monotonic frequency-axis rejection.

## Verification Result

- OS-CFAR focused tests: **11 passed**
- Complete repository suite: **149 passed**
- Informational local runtime smoke measurement:
  approximately **13.7 ms per 8,192-bin frame** over 20 runs on the current
  development system

The runtime figure is not a formal comparison result. Phase 3 must measure both
detectors under the same benchmark protocol with warmup, repeated trials, and
reported distribution statistics.

## Phase 2 Decision

The independent detector is ready for automated comparison development.

It is not ready for:

- `main.py` integration;
- hardware selection;
- occupancy replacement;
- SMART evaluation;
- production claims;
- removal of the current detector.

The next approved phase should freeze identical datasets and acceptance
metrics for both detectors before generating comparative results.
