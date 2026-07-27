# SPECTRA Hardware Validation Framework — Final Engineering Report

> **Historical document.** The described GUI validation workflow has been
> retired. Current validation uses the standalone REAL-RF capture/replay
> workflow documented in
> [`real_rf_detector_evaluation.md`](real_rf_detector_evaluation.md). This
> report is preserved as evidence of the completed temporary subsystem; its
> original technical conclusions and results have not been rewritten.

## 1. Executive Summary

The SPECTRA Hardware Validation Framework provides a temporary, isolated
engineering mode for recording reproducible evidence from the production
adaptive detector during real RTL-SDR operation. It allows an operator to
start a validation session, use normal monitoring and survey functions, stop
the session, and receive structured configuration, frame, survey, event-log,
and summary artifacts.

The framework observes values already produced by SPECTRA. It does not own SDR
tuning, FFT processing, adaptive thresholding, peak detection, temporal
confirmation, occupancy calculation, survey sequencing, recommendation
ranking, or SMART scoring.

The completed implementation includes:

- JSON-safe validation data contracts;
- collision-safe validation sessions and evidence folders;
- CSV and JSONL frame and survey logging;
- frozen production-configuration snapshots;
- automatic survey outcome capture;
- neutral session summaries;
- timestamped lifecycle and error logging;
- temporary Start/Stop UI controls;
- safe shutdown, interruption, invalid-input, and write-error handling;
- framework, operator, and safety documentation;
- focused unit, integration, isolation, and regression tests.

The framework passed the complete automated repository suite and real RTL-SDR
manual smoke testing. It is ready to support the approved hardware validation
campaign.

## 2. Engineering Objective

The objective was to reduce manual data transcription and create traceable
hardware-validation evidence without changing production signal-processing or
decision behavior.

The implemented evidence chain is:

```text
Production SPECTRA measurements
            |
            v
HardwareValidationController
            |
            v
JSON-safe validation records
            |
            v
CSV + JSONL + event log
            |
            v
JSON + CSV + Markdown session summary
```

This design preserves a clear boundary between measurement production and
evidence persistence.

## 3. Architecture

### 3.1 Validation package

The implementation is concentrated under `VALIDATION/hardware/`:

| File | Responsibility |
|---|---|
| `__init__.py` | Public validation-package interface |
| `validation_models.py` | JSON-safe configuration, frame, survey, and summary dataclasses |
| `validation_capture.py` | Conversion of existing application values into validation records |
| `validation_controller.py` | Session orchestration, logging cadence, survey capture, and safe shutdown |
| `validation_session.py` | IDs, collision-safe folders, counters, statistics, warnings, and errors |
| `validation_logger.py` | Configuration, frame, survey, event, and summary persistence |
| `validation_summary.py` | Reviewer-readable Markdown summary generation |
| `validation_environment.py` | Safe Git commit SHA retrieval |

### 3.2 Production integration

Production integration is intentionally narrow:

- `main.py` constructs one `HardwareValidationController`.
- Existing FFT and detector outputs are passed to `log_frame()` after
  production detection has completed.
- Existing survey outcomes are passed to `log_survey()` through the survey
  completion callback.
- Application shutdown calls the validation controller's safe shutdown path.
- `UI/tuning_panel.py` exposes temporary Start/Stop controls and a compact
  status label.
- `UI/theme.py` applies the existing SPECTRA visual language to those temporary
  controls.
- `UTILS/config.py` supplies explicit validation metadata and the independent
  logging interval.

The framework does not directly import or control RTL-SDR hardware and does not
make survey or recommendation decisions.

### 3.3 Temporary subsystem boundary

The framework is an engineering tool rather than an end-user feature.
`HARDWARE_VALIDATION_ENABLED` defaults to `False`; manual Start/Stop controls
activate recording when required. The validation package can later be hidden
or removed without redesigning the production detector or decision pipeline.

## 4. Files Added

### 4.1 Validation implementation

- `VALIDATION/hardware/validation_controller.py`
- `VALIDATION/hardware/validation_environment.py`
- `VALIDATION/hardware/validation_summary.py`

The remaining validation modules existed as initial framework scaffolding and
were completed and hardened during this phase.

### 4.2 Tests

- `tests/test_hardware_validation_controller.py`
- `tests/test_hardware_validation_environment.py`
- `tests/test_hardware_validation_integration.py`
- `tests/test_hardware_validation_safety.py`

### 4.3 Documentation

- `docs/hardware_validation_framework.md`
- `docs/hardware_validation_operator_guide.md`
- `docs/hardware_validation_safety_performance.md`
- `docs/hardware_validation_framework_final_report.md`

## 5. Files Modified

The framework phase modified the following integration or framework files:

- `main.py`
- `UI/tuning_panel.py`
- `UI/theme.py`
- `VALIDATION/hardware/__init__.py`
- `VALIDATION/hardware/validation_capture.py`
- `VALIDATION/hardware/validation_logger.py`
- `VALIDATION/hardware/validation_models.py`
- `VALIDATION/hardware/validation_session.py`
- existing hardware-validation tests;
- survey tests required to verify validation completion callbacks and
  interruption semantics.

No production adaptive-detector, FFT, OS-CFAR, SMART, or survey-ranking module
was modified during the hardware-validation framework phase.

## 6. Validation UI Behavior

The temporary engineering controls are displayed near receiver tuning:

- **Start validation log**
- **Stop validation log**
- validation status label

State behavior:

| State | Start | Stop | Status |
|---|---:|---:|---|
| Inactive | Enabled | Disabled | Validation idle |
| Recording | Disabled | Enabled | Validation logging active |
| Saved | Enabled | Disabled | Validation log saved |
| Error | Enabled | Disabled | Explicit validation error |

Only one validation session may be active. Missing optional operator metadata
does not stop application operation. An active session is finalized during
application shutdown.

The controls are intentionally compact and temporary. They are not part of the
final end-user feature set.

## 7. Data Captured

### 7.1 Configuration snapshot

At session start, the framework captures:

- validation, session, and configuration IDs;
- session description and test band;
- antenna, location, expected-signal, and operator metadata;
- confirmed receiver center frequency;
- sample rate and FFT size;
- gain mode and manual gain value when applicable;
- detector name and adaptive-detector parameters;
- temporal-confirmation parameters;
- update and validation logging intervals;
- survey measurement defaults;
- active decision mode and SMART mode state;
- software description;
- Git commit SHA.

### 7.2 Frame evidence

At the independent validation interval, currently 1000 ms:

- timestamp;
- confirmed center frequency;
- strongest finite FFT-bin frequency and relative power;
- average relative FFT power;
- median adaptive threshold;
- spectral-bin occupancy;
- raw candidate count and frequencies;
- confirmed signal count and frequencies;
- adaptive-detector runtime;
- current recommendation when available;
- monitoring or survey application mode.

### 7.3 Survey evidence

For each recorded survey outcome:

- start, stop, and step frequency;
- requested/measured point count;
- ranked occupancy results;
- recommendation and recommended occupancy;
- decision mode;
- SMART recommendation, winner score, runner-up, margin, and confidence when
  applicable;
- completion state, reason, and error message.

FREE-mode surveys intentionally leave SMART-only score fields empty.
Interrupted and failed surveys are retained honestly rather than reported as
successful.

### 7.4 Session summary

The summary reports:

- session timing and duration;
- logged, valid, and skipped frame counts;
- survey count and completion states;
- average raw and confirmed counts;
- average and maximum detector runtime;
- average spectral-bin occupancy;
- frequently observed confirmed frequencies;
- strongest observed FFT bin;
- SMART recommendation frequency and repeatability when available;
- warnings, errors, operator metadata, and engineering limitations.

## 8. Output Folder Example

```text
VALIDATION/hardware/results/
  VAL-20260726-182111_SESSION-20260726-182111-9e0b6db1/
    session_config.csv
    session_config.json
    validation.log
    frames/
      frame_records.csv
      frame_records.jsonl
    surveys/
      survey_records.csv
      survey_records.jsonl
    summaries/
      session_summary.csv
      session_summary.json
      summary.md
    artifacts/
```

CSV provides spreadsheet compatibility. JSONL retains one structured record per
line for analysis. JSON provides structured configuration and aggregate
results. Markdown provides a reviewer-readable summary. The event log preserves
session lifecycle, survey, warning, error, and shutdown events.

Automatic screenshots were optional and were not implemented. The `artifacts/`
directory remains available for manually approved supporting evidence.

Raw session directories remain local by default and are not automatically
committed.

## 9. Automated Test Coverage

The framework tests cover:

- stable validation and session ID generation;
- collision-safe folder creation;
- configuration JSON and CSV output;
- frame CSV and JSONL serialization;
- survey CSV and JSONL serialization;
- session start, stop, duplicate start, and inactive stop;
- frame logging interval;
- inactive frame and survey rejection;
- missing optional fields;
- JSON safety and non-finite value rejection;
- invalid FFT input handling;
- summary statistics and Markdown generation;
- active FREE/SMART mode snapshotting;
- safe Git SHA retrieval and `unknown` fallback;
- successful, failed, cancelled, and interrupted survey evidence;
- permission, missing-directory, disk-write, serialization, and summary-write
  failures;
- safe application shutdown;
- complete simulated session generation in a temporary directory;
- CSV/JSONL/summary count consistency;
- inactive short-circuit before providers, record construction, or filesystem
  work;
- deterministic detector non-interference and input immutability.

All automated artifacts use temporary directories. Tests do not require
physical RTL-SDR hardware and do not write into the real results directory.

## 10. Test Results

Final Stage 13 automated results:

| Test scope | Result |
|---|---:|
| Focused safety and integration suite | 13 passed |
| Complete repository suite | 223 passed |
| Formatting check | Passed |

The complete suite includes FFT, detector, noise-floor, temporal confirmation,
signal history, feature extraction, classification, decision engine, survey
controller, UI rendering, OS-CFAR experimental code, and hardware-validation
tests.

## 11. Manual RTL-SDR Verification

Manual testing confirmed:

- SPECTRA starts and connects to the RTL-SDR normally;
- validation starts and stops normally;
- live FFT and waterfall remain responsive;
- manual tuning remains functional;
- surveys complete and are recorded;
- saved evidence is readable;
- shutdown during an active survey is safe;
- interrupted survey evidence is labeled correctly;
- no application crash occurs during normal validation operation.

### 11.1 Reviewed normal session

One reviewed normal session produced:

- 15 frame records;
- one successful 13-point FREE survey;
- 91 MHz recommendation;
- matching CSV and JSONL counts;
- no warnings or errors.

### 11.2 Reviewed shutdown session

One reviewed shutdown session produced:

- four frame records;
- one survey interrupted after three points;
- completion reason `Application shutdown`;
- matching CSV and JSONL counts;
- complete shutdown and summary lifecycle events;
- no warnings or errors.

### 11.3 Final performance smoke session

The final manual Stage 13 session produced:

| Metric | Observed result |
|---|---:|
| Duration | 61.449 s |
| Logged frames | 57 |
| Surveys | 1 successful |
| Average detector runtime | 1.045 ms |
| Maximum detector runtime | 1.381 ms |
| Warnings | 0 |
| Errors | 0 |

The configuration snapshot recorded:

- sample rate: 2.048 MS/s;
- FFT size: 8192;
- gain mode: automatic;
- decision mode: FREE;
- display update interval: 100 ms;
- validation logging interval: 1000 ms;
- valid 40-character Git commit SHA.

These runtime observations characterize the tested computer and session only.
They are not universal performance guarantees.

## 12. Exact Manual Test Procedure

Use this sequence for the final operator acceptance record:

1. Connect the RTL-SDR Blog V3 and dipole antenna.
2. Start SPECTRA.
3. Confirm **Receiver connected**.
4. With validation inactive, observe FFT and waterfall for at least 15 seconds.
5. Perform one manual tune.
6. Run one short survey and confirm normal recommendation/status behavior.
7. Press **Start validation log**.
8. Confirm **Validation logging active**.
9. Observe FFT and waterfall for at least 15 seconds.
10. Perform one manual tune.
11. Run one complete FREE or SMART survey.
12. Confirm the UI remains responsive and survey behavior is normal.
13. Press **Stop validation log**.
14. Wait for **Validation log saved**.
15. Open the newest `VALIDATION/hardware/results/VAL-*` directory.
16. Confirm frame CSV rows equal frame JSONL lines.
17. Confirm survey CSV rows equal survey JSONL lines.
18. Confirm summary totals match the raw evidence.
19. Confirm `validation.log` contains start, configuration, first frame, survey,
    stop, summary, and stopped events.
20. Confirm configuration values and Git SHA match the intended run.
21. Start a second validation session and begin a survey.
22. Close SPECTRA before survey completion.
23. Confirm the second session records shutdown and an interrupted survey.
24. Confirm both sessions contain readable summaries.

## 13. Known Limitations

- Live RF generally lacks known truth labels. A candidate is not automatically
  a verified transmitter or false alarm.
- An absent detection is not automatically a known miss.
- FFT power is relative and not calibrated dBm.
- Occupancy is spectral-bin occupancy for the measurement frame, not
  regulatory channel occupancy.
- Absolute frequency observations depend on RTL-SDR oscillator accuracy and
  calibration.
- Indoor antenna placement, polarization, multipath, cable routing,
  interference, gain mode, and receiver temperature affect results.
- Validation frame logging is intentionally decimated and does not retain every
  display update.
- Synchronous file appends were acceptable during tested sessions but have not
  been characterized as a long-duration storage benchmark.
- Recommendation repeatability is agreement among observed recommendations,
  not probability of correct channel selection.
- Automatic screenshots are not implemented.
- Validation controls are temporary engineering UI and should be removed or
  hidden after evidence collection.

## 14. Production Non-Modification Confirmation

The following statements are explicitly confirmed for this framework phase:

- **Adaptive detector logic was not modified.**
- **Adaptive threshold logic was not modified.**
- **Temporal confirmation logic was not modified.**
- **FFT processing was not modified.**
- **Experimental OS-CFAR was not modified or integrated into production.**
- **SMART scoring was not modified.**
- **Survey ranking was not modified.**
- **SDR tuning behavior was not modified by validation logging.**
- **No database, cloud service, network service, or new heavy dependency was
  introduced.**

When validation is inactive, frame and survey logging requests immediately
return before clock access, receiver-state access, record construction,
serialization, or filesystem activity. The remaining production-path cost is
a controller state check and function return.

## 15. Final Engineering Assessment

The Hardware Validation Framework meets its engineering objective. It provides
organized, traceable evidence while maintaining a conservative boundary around
the production signal-processing and decision system. Automated and hardware
testing demonstrate correct session lifecycle, evidence consistency, failure
containment, interruption handling, detector non-interference, and acceptable
target-system responsiveness.

The framework is suitable for the SPECTRA senior-design validation campaign.
It should remain enabled only while collecting approved engineering evidence.
After validation is complete, the temporary controls and production call sites
may be removed while preserving the standalone evidence package and final
report artifacts.
