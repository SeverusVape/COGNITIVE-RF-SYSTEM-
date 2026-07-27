# SPECTRA Screenshot Inventory

## Inventory

| Filename | Purpose | Demonstration stage | Visible evidence |
|---|---|---|---|
| `start.png` | Application startup and live receiver operation | Startup and interface orientation | Full SPECTRA interface, confirmed 100.0 MHz center, `RECEIVER CONNECTED`, live FFT, waterfall, peak candidates, spectral-bin occupancy, survey controls, and empty pre-survey history state |
| `fft_and_waterfall.png` | Real-time spectrum and waterfall visualization | Live DSP explanation | Relative-power FFT, frequency axis, three labeled peak candidates, and aligned waterfall activity around the observed spectrum |
| `survey_running.png` | Event-driven survey execution and progress | Automated survey | SMART survey settings, confirmed 91.0 MHz center, `SURVEY IN PROGRESS`, scan point 4/13, 30% progress, live FFT/waterfall, occupancy heatmap, and receiver status |
| `survey_complete.png` | Completed survey with recommendation and Auto-Tune state | Survey completion and Auto-Tune | Completed occupancy history, high-contrast recommendation marker, survey history, confirmed 100.0 MHz center, `ON RECOMMENDED CHANNEL`, and detailed-results control |
| `smart_report_top.png` | SMART decision comparison and score explanation | Explainable recommendation | 89.000 MHz recommendation, 13 points scanned, average spectral-bin occupancy, 82.7/111 SMART score, 92.000 MHz runner-up, 14.8-point separation, HIGH score-separation category, why-selected statements, grouped score breakdown, and supporting measurements |
| `smart_report_diagnostics.png` | Signal diagnostics and survey-coverage evidence | Supporting engineering evidence | Survey Diagnostic Coverage table, recommended-frequency row, evidence maturity, frequency behavior, bandwidth behavior, activity descriptors, diagnostic-only disclaimer, and report close control |

## Asset Details

| Filename | Dimensions | SHA-256 |
|---|---:|---|
| `start.png` | 2934 × 1740 | `2468068c7e6d10f46db8a9757bf7cf92012981ce6b64e62326ba61b13a50ff41` |
| `fft_and_waterfall.png` | 1832 × 738 | `80eccc21ab5567de6a27b8899c66ce3eb9f4000d4a7aa2dd4b8515b263c7e6a3` |
| `survey_running.png` | 2940 × 1912 | `a8429395329f48cb9241864beb6cc8bff8b6a47e2a8b67fa93cff66c2f802fb1` |
| `survey_complete.png` | 2940 × 1912 | `0ca99c703c4e611d167fa6b9b674808d15c566dee6ba5d5da5189d114dce3ed9` |
| `smart_report_top.png` | 2940 × 1628 | `c7563edfa395c359aa956ce923a6a1571aaed5cc15d2404f06d09c3215de29a8` |
| `smart_report_diagnostics.png` | 2940 × 524 | `fe9e3602be7c5269c7c744eba90dd0605ca641e0daebbeb2d1f93c8b423e842d` |

The hashes above identify the exact PNG assets integrated into this release
package. Recalculate the inventory if any file is recaptured, cropped,
resized, or recompressed.

## Engineering Interpretation Boundaries

- FFT power is relative and is not calibrated dBm.
- Peak markers identify spectral candidates, not verified transmitters.
- Spectral-bin occupancy is not regulatory channel occupancy.
- Context descriptors do not identify modulation, protocol, service, or
  transmitter.
- SMART score separation is not statistical confidence.
- The screenshots demonstrate system behavior and presentation evidence, not
  absolute detector accuracy.
