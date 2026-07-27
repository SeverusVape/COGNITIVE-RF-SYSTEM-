# SPECTRA Release Candidate Verification Report

## 1. Verification Summary

SPECTRA release candidate `031af87` was verified on July 27, 2026. The
verification combined automated regression testing with a live RTL-SDR
hardware workflow.

All required checks passed:

- documented application startup;
- live spectrum operation;
- manual tuning;
- event-driven survey execution;
- SMART recommendation reporting;
- Auto-Tune operation;
- clean receiver shutdown; and
- successful application relaunch.

No release-blocking issue was observed during this verification.

## 2. Environment

| Item | Verified configuration |
|---|---|
| Verification date | July 27, 2026 |
| Recorded start time | 16:45:27 EDT |
| Operating system | macOS 26.5.2, build 25F84 |
| Python | CPython 3.10.11 |
| Hardware | RTL-SDR Blog V3, RTL2832U/R860, 1 PPM TCXO |
| SDR system library | Homebrew `librtlsdr` |
| Application revision | `031af87` |
| Production detector | Adaptive Detector |
| Research baseline | Standalone OS-CFAR |

The receiver library reported the compatible tuner-family name `Rafael
Micro R820T`. This is expected for the R860-based RTL-SDR Blog V3 and does
not indicate different physical hardware.

## 3. Automated Verification

### Repository Baseline

Commands:

```text
git status --short
git diff --check
```

Results:

- working tree clean before verification;
- no whitespace errors.

### Dependency Health

Command:

```text
.venv/bin/python -m pip check
```

Result:

```text
No broken requirements found.
```

The pip cache-permission warning observed during this command did not
indicate a dependency conflict and did not affect application execution.

### Regression Suite

Command:

```text
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 283 tests in 0.440s
OK
```

All 283 tests passed. No failures, errors, or unexpected skips were
reported.

## 4. Manual Hardware Verification Checklist

The operator performed the following checks with the RTL-SDR connected.

| Area | Verification | Result |
|---|---|---|
| Startup | Application opened from the documented launch command | Pass |
| Receiver | RTL-SDR detected and `RECEIVER CONNECTED` displayed | Pass |
| FFT | Live FFT trace updated continuously | Pass |
| Waterfall | Waterfall history updated continuously | Pass |
| Peak display | Peak markers appeared over detected candidates | Pass |
| Status | Receiver values and spectral status updated | Pass |
| Manual tuning | Tune command changed the confirmed center frequency | Pass |
| Plot alignment | Frequency display and plot range followed confirmed tuning | Pass |
| Survey setup | Survey configured for 88–92 MHz with 1 MHz steps | Pass |
| Survey sequencing | Five tune-confirm-measure points completed | Pass |
| Survey result | Recommendation was generated | Pass |
| Detailed report | Survey Results report opened | Pass |
| Decision comparison | Recommendation and runner-up displayed | Pass |
| Decision separation | Score-separation value and label displayed | Pass |
| Score breakdown | SMART component scores displayed | Pass |
| Diagnostics | Supporting diagnostic sections displayed | Pass |
| Auto-Tune | Receiver moved from another frequency to the recommendation | Pass |
| Survey status | `ON RECOMMENDED CHANNEL` displayed after confirmed tuning | Pass |
| Shutdown | Application exited and SDR worker closed | Pass |
| Relaunch | Receiver could be opened again after shutdown | Pass |

Terminal evidence from the survey and shutdown sequence:

```text
SDR CONNECTED
Survey point: 1 / 5
Survey point: 2 / 5
Survey point: 3 / 5
Survey point: 4 / 5
Survey point: 5 / 5
SDR CLOSED
```

## 5. Known Limitations

- FFT power values are relative and are not calibrated dBm measurements.
- Spectral-bin occupancy is an application measurement metric, not
  regulatory channel occupancy.
- Signal context labels do not identify modulation, protocol, transmitter,
  or service with ground-truth certainty.
- The REAL-RF campaign demonstrates deterministic replay, detector
  agreement, and runtime behavior; it does not establish absolute
  probability of detection or false-alarm performance.
- RTL-SDR frequency and amplitude measurements remain subject to receiver,
  antenna, gain, local-interference, and RF-environment limitations.
- `librtlsdr` emitted the existing `[R82XX] PLL not locked!` startup
  warning. The receiver nevertheless connected and completed live tuning,
  acquisition, survey, Auto-Tune, shutdown, and relaunch checks.
- Only one process may control the RTL-SDR at a time.

## 6. Release Recommendation

The verified revision satisfies the defined release-candidate acceptance
checks. Automated regression, dependency health, live receiver operation,
survey sequencing, explainable SMART reporting, Auto-Tune, shutdown, and
relaunch all passed.

**Recommendation: approve this revision as the SPECTRA release candidate.**

This recommendation is limited to the documented application scope and
does not imply calibrated RF measurement accuracy, ground-truth signal
identification, or statistically validated detector accuracy.
