# SPECTRA Hardware Validation Session Summary

This report summarizes observed SPECTRA behavior. It does not establish RF ground truth, calibrated power, probability of detection, or classical false-alarm probability.

## Session Identity

- Validation ID: `VAL-20260726-182111`
- Session ID: `SESSION-20260726-182111-9e0b6db1`
- Session name: SPECTRA hardware validation
- Test band: operator selected
- Configuration ID: `CFG-HW-01`
- Git commit: `c631c616a8d18068c91a92f7fa26a3e23e52da95`
- Start: 2026-07-26T18:21:11-04:00
- Stop: 2026-07-26T18:22:12-04:00
- Duration: 61.449 s

## Evidence Totals

- Logged frames: 57
- Valid frames: 57
- Skipped or invalid frames: 0
- Survey records: 1

## Observed Frame Metrics

| Metric | Observed value |
|---|---:|
| Average raw candidates per frame | 3.0 |
| Average confirmed signals per frame | 1.456 |
| Average detector runtime | 1.045 ms |
| Maximum detector runtime | 1.381 ms |
| Average spectral-bin occupancy | 11.161% |

## Survey Completion States

| State | Count |
|---|---:|
| success | 1 |

## Recommendation Observations

- Most frequent SMART recommendation: 100.000000 MHz
- Survey recommendation repeatability: 100.0%

Repeatability is the fraction of recorded survey recommendations matching the most common recommendation. It is not a probability of correct selection.

## Confirmed-Frequency Observations

| Frequency | Frame observations |
|---|---:|
| 345.758250 MHz | 17 |
| 344.353750 MHz | 10 |
| 345.600000 MHz | 7 |
| 99.499750 MHz | 5 |
| 345.601500 MHz | 5 |

## Strongest Observed FFT Bin

- Frequency: 99.499750 MHz
- Relative FFT power: 63.6 dB

The strongest FFT bin is a spectral maximum, not necessarily a confirmed or identified signal.

## Operator Metadata

- Notes: unspecified
- Antenna: RTL-SDR Blog V3 R860 RTL2832U with dipole antenna kit
- Location: Fourth-floor residential indoor window test location, Bay Ridge, Brooklyn, NY
- Expected signal description: Local broadcast and public RF carriers observable with indoor dipole

## Warnings

- None recorded.

## Errors

- None recorded.

## Limitations

- RTL-SDR measurements are relative, not calibrated dBm.
- Indoor antenna placement affects observed occupancy.
- Validation records reflect SPECTRA application behavior.
