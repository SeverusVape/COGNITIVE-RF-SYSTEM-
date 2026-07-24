# SPECTRA Phase 4 Detector Comparison

**Validation:** DE-CMP-01 / CFG-C01

## Outcome

The experimental OS-CFAR detector passed 5 of 6 predeclared synthetic gates.

**Phase 5 status:** Synthetic decision gates are not all satisfied. Do not replace the production detector.

This outcome is not a production-detector selection. Hardware evidence and full regression review remain mandatory.

## Frozen Method

- 100 trials for each of 8 scenarios
- 800 shared spectra
- Both detectors received the exact same read-only FFT arrays
- Base seed: 3104204
- Match tolerance: 1.0 FFT bin
- 5 warmup calls per detector
- Detector execution order alternated by trial

## Decision Gates

| Gate | Requirement | Adaptive | OS-CFAR | Result |
| --- | --- | ---: | ---: | --- |
| G1 | Material noise-only false-alarm reduction | 1.0000 | 1.0000 | FAIL |
| G2 | Single-carrier sensitivity | 1.0000 | 1.0000 | PASS |
| G3 | Weak carrier beside strong carrier | 0.9900 | 0.9900 | PASS |
| G4 | Closely spaced carrier performance | 1.0000 | 1.0000 | PASS |
| G5 | Robustness across non-ideal scenarios | 1.0000 | 1.0000 | PASS |
| G6 | Runtime compatible with the live processing interval | 0.5070 | 14.4218 | PASS |

## Scenario Metrics

`Pfa` in this frozen table means **SPECTRA Frame False Alarm Rate**: a frame is
false when it contains at least one unmatched raw detector candidate. It is
not the classical per-cell CFAR Probability of False Alarm. The frame-level
metric was chosen because it better represents whether a SPECTRA processing
frame can introduce an unsupported candidate into downstream processing.
Temporal confirmation remains outside this comparison.

| Scenario | Detector | Pd | Frame Pfa | Precision | Recall | p95 runtime (ms) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| noise only | adaptive | NA | 1.0000 | 0.0000 | NA | 0.507 |
| noise only | os_cfar | NA | 1.0000 | 0.0000 | NA | 14.333 |
| single carrier | adaptive | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 0.435 |
| single carrier | os_cfar | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 14.155 |
| weak beside strong | adaptive | 0.9900 | 1.0000 | 0.6600 | 0.9900 | 0.467 |
| weak beside strong | os_cfar | 0.9900 | 1.0000 | 0.6600 | 0.9900 | 14.422 |
| multiple carriers | adaptive | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 0.456 |
| multiple carriers | os_cfar | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 14.046 |
| fft edge | adaptive | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 0.465 |
| fft edge | os_cfar | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 14.165 |
| closely spaced carriers | adaptive | 1.0000 | 1.0000 | 0.6667 | 1.0000 | 0.468 |
| closely spaced carriers | os_cfar | 1.0000 | 1.0000 | 0.6667 | 1.0000 | 14.113 |
| variable noise floor | adaptive | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 0.458 |
| variable noise floor | os_cfar | 1.0000 | 1.0000 | 0.3333 | 1.0000 | 14.079 |
| monte carlo | adaptive | 1.0000 | 0.7100 | 0.4900 | 1.0000 | 0.441 |
| monte carlo | os_cfar | 1.0000 | 0.7100 | 0.4900 | 1.0000 | 13.866 |

## Engineering Limitations

- Inputs are deterministic synthetic unmodulated tones and algorithmic noise.
- Coherent Hann-window FFT processing provides narrow-tone processing gain;
  synthetic SNR fixtures are not equivalent to hardware input sensitivity.
- High-SNR cases can saturate the three-candidate output cap and produce
  near-unity detection probability for both detectors.
- Relative FFT levels are not calibrated dBm.
- Raw peak outputs are compared before temporal confirmation.
- The three-peak cap remains part of both public detector interfaces.
- Synthetic data cannot reproduce real RF clutter, multipath, modulation,
  impulsive interference, or receiver artifacts.
- Results apply only to frozen OS-CFAR configuration `CFG-C01`. Any parameter
  optimization requires a new predeclared validation campaign.
- Edge tests cover explicit excluded-bin behavior and valid near-edge
  detection, but not a complete sweep through excluded, transition, and valid
  regions.
- Runtime results apply only to this development computer and software environment.
- No claim about live RF performance is made by Phase 4.

## Runtime Interpretation

OS-CFAR met the `100 ms` runtime gate. Its worst p95 detector runtime
(`14.4218 ms`) was approximately 28 times, or about 30 times at engineering
precision, the adaptive detector result (`0.5070 ms`). Runtime alone does not
reject OS-CFAR because both detectors met the requirement. The candidate
nevertheless provided no measurable Frame False Alarm Rate improvement, so
the additional computation has no demonstrated production benefit.
