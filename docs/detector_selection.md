# SPECTRA Production Detector Selection

## Decision

**Retain the Adaptive Detector as the SPECTRA production detector.**

OS-CFAR remains a standalone research and validation baseline. It is not
connected to production spectrum processing, survey sequencing, SMART scoring,
or the operator interface.

## Evidence

The detector decision used two complementary evidence sets:

1. A frozen deterministic synthetic comparison using identical FFT inputs and
   predeclared decision gates.
2. Nine REAL-RF IQ datasets replayed through shared FFT preprocessing and both
   unchanged detectors.

Both production configurations return capped top-three candidate lists. The
REAL-RF evidence therefore measures agreement among selected candidates, not
ground-truth correctness.

## Engineering Basis

- The frozen OS-CFAR configuration did not improve the defined synthetic
  frame-level false-alarm result.
- Both detectors produced comparable capped peak-selection behavior under the
  recorded REAL-RF campaign.
- OS-CFAR met the runtime requirement but required approximately 30–32 times
  greater mean detector runtime on the tested host and configurations.
- No demonstrated production benefit justified the additional computation and
  integration risk.

Runtime alone did not reject OS-CFAR. The decision reflects the absence of a
measurable project-level benefit that offsets its cost.

## Claim Boundary

The evidence does not establish universal detector superiority, absolute
probability of detection, false-alarm probability, or calibrated accuracy.
Controlled ground-truth RF characterization remains future work.

Detailed methodology and results remain in the
[final detector assessment](detection_engine_final_assessment.md) and
[REAL-RF campaign report](REAL_RF_VALIDATION_CAMPAIGN_REPORT.md).
