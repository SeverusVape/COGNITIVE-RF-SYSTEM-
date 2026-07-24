# SPECTRA Detection Engine Future Work

## Scope

This document records possible engineering investigations beyond the completed
Phase 4 detector comparison. These activities are **not required for Phase 4
completion**, do not alter its results, and do not authorize changes to the
production detector.

Each future experiment should use a new validation identifier, freeze its
configuration and acceptance criteria before execution, preserve the current
Phase 4 evidence, and distinguish synthetic algorithm evidence from hardware
system evidence.

## Low-SNR Probability-of-Detection Characterization

Phase 4 includes useful sensitivity scenarios, but several operate where both
detectors reach near-unity probability of detection. A dedicated SNR sweep
could estimate detection probability and confidence intervals through the
transition from nondetection to reliable detection.

The study should include:

- more trials near the detection knee;
- identical randomized phases and noise for each detector;
- uncertainty intervals at every SNR level;
- frequency error and missed-detection behavior; and
- separate results for isolated and adjacent carriers.

The result would characterize sensitivity trends, not calibrated receiver
sensitivity or minimum discernible signal.

## Per-Cell False-Alarm Measurement

A separate experiment could measure classical per-cell false-alarm behavior.
It should count threshold exceedances or returned cells relative to the total
number of valid cells under a precisely defined noise model.

This metric must remain separate from SPECTRA Frame False Alarm Rate. The study
would require:

- an explicit cell-under-test definition;
- treatment of excluded edge cells;
- a stated independence/correlation assumption;
- confidence intervals for rare events; and
- enough observations to support the target probability range.

## Live RF Validation

Saved RTL-SDR IQ captures could be replayed through both detector candidates
without requiring simultaneous receiver access. Appropriate receive-only
ranges include FM broadcast, airband, NOAA weather radio where receivable, and
the 2 m amateur band.

Live validation should record antenna geometry, gain mode, center frequency,
sample rate, receiver warm-up, time, location, and capture hashes. Because
ground truth is limited, results should be reported as candidate agreement,
repeatability, and engineering observations rather than absolute detection
accuracy.

## Real Interference and Clutter Testing

Future tests may characterize behavior with:

- impulsive interference;
- elevated or sloped baselines;
- adjacent-channel energy;
- receiver DC and image artifacts;
- intermittent carriers;
- multipath fading; and
- overlapping modulated emissions.

Where controlled RF equipment is unavailable, saved receive-only captures and
carefully documented observational labels are preferable to unsupported
ground-truth claims.

## Additional Synthetic Scenarios

Useful additions include frequency drift, burst duty cycles, chirps, wider
modulated-like spectra, asymmetric clutter, amplitude fading, and randomized
combinations of narrow and broad emissions.

Every scenario should answer a defined engineering question. Adding synthetic
cases only to increase test quantity would not improve the evidence package.

## CFAR Parameter Optimization

OS-CFAR rank, reference cells, guard cells, scale, spacing, and output cap may
be explored only as a **new experiment**. Phase 4 validates configuration
`CFG-C01`; it does not validate other parameter combinations.

An optimization campaign should:

1. divide data into development and held-out evaluation sets;
2. predeclare the objective function and operational constraints;
3. prevent tuning on the final comparison set;
4. include computational cost; and
5. repeat final qualification using newly frozen acceptance gates.

Retuning Phase 4 retrospectively would invalidate its objective comparison and
must be avoided.

## Candidate Qualification Improvements

Future qualification could add:

- stratified low-, medium-, and high-SNR gates;
- confidence intervals for detector differences;
- paired statistical comparisons;
- saved-IQ replay tests;
- memory and CPU utilization evidence;
- boundary-condition sweeps; and
- regression criteria for downstream classification and survey behavior.

Qualification should continue to compare complete operational consequences,
not only raw peak count.

## Temporal Confirmation Improvements

The current temporal stage can suppress transient raw candidates, but future
work may examine:

- confirmation probability versus persistence;
- false confirmation under correlated noise;
- tolerance versus frequency drift;
- burst and intermittent-signal behavior;
- state expiration after retuning; and
- interaction with the three-candidate detector cap.

Any change should be validated independently before integration because
temporal confirmation affects signal history, classification, and survey
outputs.

## Future-Work Boundary

None of these investigations changes the completed Phase 4 conclusion. Until
a new candidate passes a fully predeclared qualification campaign, SPECTRA
should retain the adaptive detector as its production detector.
