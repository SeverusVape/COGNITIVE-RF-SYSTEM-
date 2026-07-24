# SPECTRA Detection Engine Evolution

## Phase 3 — Shared Automated Evaluation Framework

**Status:** Framework complete; comparative experiment not started  
**Production detector:** `SDR/detection.py` remains unchanged  
**Experimental detector:** `SDR/os_cfar.py` remains isolated

## Scope

Phase 3 creates a deterministic, validation-only framework that can evaluate
SPECTRA's current adaptive detector and the experimental OS-CFAR detector on
the exact same synthetic FFT inputs.

This phase does not:

- select a detector;
- tune either detector;
- generate a pass/fail comparison;
- change the production application;
- change occupancy, survey, SMART, history, classification, or UI behavior.

Those boundaries prevent the evaluation infrastructure from influencing the
algorithms it is intended to measure.

## Shared Detector Interface

Both algorithms are wrapped by a validation-only `DetectorAdapter` with the
same callable contract:

```text
detector(power_db, freqs_mhz) -> (peaks, threshold)
```

The current detector is imported directly from `SDR/detection.py`. The
experimental detector is imported from `SDR/os_cfar.py` and receives an
explicit `OSCFARConfig`.

The application does not import the evaluation module.

## Deterministic Synthetic Inputs

`VALIDATION/detector_evaluation.py` creates complex-IQ noise and tones, passes
them through SPECTRA's existing coherent-gain-corrected Hann FFT, and stores
the resulting spectra as read-only arrays.

Every random condition has a recorded seed. Both detectors receive the same
`SyntheticTrial` objects, so differences in output cannot be attributed to
different noise realizations.

The framework covers:

| Scenario | Engineering purpose |
| --- | --- |
| Noise only | Raw false-alarm behavior |
| Single carrier | Basic sensitivity and frequency estimation |
| Weak beside strong | Masking behavior near a stronger response |
| Multiple carriers | Operation in a populated spectrum |
| FFT edge | Explicit edge-policy behavior |
| Closely spaced carriers | Behavior near the 75 kHz spacing constraint |
| Variable noise floor | Adaptation to a nonuniform spectral baseline |
| Monte Carlo | Repeatability over randomized signal populations |

The current scenario values are evaluation fixtures, not calibrated RF input
levels or final acceptance limits.

## Detection Matching

Expected and detected frequencies are associated using deterministic
one-to-one nearest-frequency matching within a configurable tolerance.

One detection cannot satisfy more than one expected carrier. Unmatched
detections are false positives, and unmatched expected carriers are false
negatives.

This avoids overstating probability of detection in closely spaced cases.

## Common Metrics

The framework calculates the same metrics for both algorithms:

- probability of detection;
- frame false-alarm rate;
- precision;
- recall;
- mean runtime;
- 95th-percentile runtime;
- runtime coefficient of variation;
- detected-count standard deviation;
- frequency-error standard deviation.

The full per-trial result also records:

- scenario and deterministic seed;
- expected, detected, true-positive, false-positive, and false-negative
  counts;
- individual matched-frequency errors;
- detector runtime;
- median finite threshold.

Runtime values include only the detector call. Dataset construction and FFT
generation are outside the timed region.

## Automated Verification

`tests/test_detector_evaluation.py` verifies:

- complete scenario coverage;
- deterministic trial generation;
- invalid trial-count rejection;
- one-to-one association;
- false-positive accounting;
- per-trial metric collection;
- summary metric calculation;
- execution of both real detectors over identical scenarios;
- finite threshold evidence from both algorithms.

The tests establish evaluation-framework correctness. They do not establish
that either detector is superior.

## Phase 3 Decision

The shared comparison framework is ready for the controlled Phase 4
experiment.

Before Phase 4 runs, the comparison protocol must freeze:

- detector configurations;
- scenario counts and seeds;
- SNR and separation sweeps;
- matching tolerance;
- runtime warmup and repetition policy;
- acceptance criteria;
- output artifact schema.

No production integration or detector selection is authorized by this phase.
