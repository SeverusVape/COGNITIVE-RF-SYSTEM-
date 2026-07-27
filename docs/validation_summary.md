# SPECTRA Validation Summary

## Scope

SPECTRA validation combines deterministic software testing, synthetic DSP
experiments, live RTL-SDR smoke testing, and immutable REAL-RF replay. Claims
are limited to what each evidence type can support.

## Automated Regression

- **283 automated tests passed** on the release-candidate environment.
- Coverage includes FFT processing, frequency-axis mapping, detection,
  temporal confirmation, signal history, survey sequencing, SMART scoring,
  status behavior, SDR worker behavior, OS-CFAR isolation, and REAL-RF replay.

## Synthetic Evidence

| Campaign | Validated behavior |
| --- | --- |
| AV-FFT-01 | FFT frequency placement under bin-centered synthetic tones |
| AV-FFT-02 | Hann-window and off-bin leakage behavior |
| AV-NF-01 | Local adaptive noise-floor behavior |
| AV-PD-01/02/03 | SNR response, frame false alarms, and two-tone spacing |
| AV-PC-01 | Temporal confirmation behavior |
| AV-BW-01 | Descriptive bandwidth heuristic |
| AV-OCC-01 | Spectral-bin occupancy calculation |
| DE-CMP-01 | Frozen Adaptive-versus-OS-CFAR comparison |

Negative acceptance results are retained as engineering limitations rather than
being tuned away. Public result folders contain summaries and key plots; raw
trial exports and workbook QA artifacts remain in the private archive.

## REAL-RF Evidence

Nine antenna-connected datasets cover FM broadcast, NOAA weather, two-meter
amateur, airband, and a nominally quiet 300 MHz region. Identical recorded IQ
was replayed through shared FFT preprocessing and both detector engines.

The campaign demonstrated:

- deterministic replay;
- identical detector input;
- capped top-three frequency-agreement measurement; and
- an observed OS-CFAR mean runtime approximately 30–32 times that of the
  Adaptive Detector on the recorded host and configurations.

It did not establish probability of detection, false-alarm probability, or
absolute detector accuracy because the captures contain no controlled ground
truth.

## Production Decision

The Adaptive Detector remains the production engine. OS-CFAR remains an
independent research and validation baseline. This is a project-specific
engineering decision, not a universal claim that one detector is superior.

## Evidence Links

- [Validation evidence index](VALIDATION_EVIDENCE_INDEX.md)
- [REAL-RF campaign report](REAL_RF_VALIDATION_CAMPAIGN_REPORT.md)
- [Detector selection](detector_selection.md)
- [Release-candidate verification](RELEASE_CANDIDATE_VERIFICATION_REPORT.md)
- [Validation package](../VALIDATION/README.md)
