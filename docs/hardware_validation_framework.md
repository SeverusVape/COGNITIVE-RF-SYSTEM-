# SPECTRA Hardware Validation Framework

## Purpose

The hardware validation framework is a temporary engineering subsystem used to
capture reproducible evidence from the production adaptive detector while
SPECTRA operates with an RTL-SDR receiver. It records measurements that the
application already computes; it does not create RF ground truth, retune the
receiver, alter detections, change survey ranking, or modify SMART scoring.

The framework is isolated primarily under `VALIDATION/hardware/` so it can be
disabled or removed after the validation campaign with minimal effect on the
production application.

## Architecture

The evidence path is deliberately one-way:

```text
Production FFT and detector results
              |
              v
HardwareValidationController
  - owns validation session state
  - applies the independent logging interval
  - converts existing values into JSON-safe records
              |
              v
HardwareValidationLogger
  - writes configuration, frame, survey, event, and summary files
              |
              v
HardwareValidationSession
  - owns IDs, evidence folders, counts, and aggregate statistics
```

Key modules:

| Module | Responsibility |
|---|---|
| `validation_models.py` | JSON-safe dataclasses for configuration, frame, survey, and summary records |
| `validation_capture.py` | Converts existing application values into validation records |
| `validation_controller.py` | Coordinates start, stop, throttled frame capture, survey capture, and shutdown |
| `validation_session.py` | Creates collision-safe session folders and maintains aggregate accounting |
| `validation_logger.py` | Persists CSV, JSON, JSONL, Markdown, and event-log evidence |
| `validation_summary.py` | Builds the reviewer-readable session summary |
| `validation_environment.py` | Retrieves supporting environment metadata such as the Git commit SHA |

The production pipeline continues to perform FFT processing, adaptive
thresholding, peak detection, temporal confirmation, occupancy calculation,
and survey decisions. Validation receives copies of their existing outputs
only after those operations occur.

## Operating Workflow

1. Start SPECTRA and confirm that the RTL-SDR is connected.
2. Select the desired receiver center frequency and survey settings.
3. Press **Start validation log**.
4. Use normal monitoring, manual tuning, and surveys as required by the
   experiment.
5. Press **Stop validation log**.
6. Review the generated session directory under
   `VALIDATION/hardware/results/`.

Only one session can be active at a time. The Start control is disabled while
recording, and the Stop control is disabled while inactive. If the application
closes during an active session, shutdown requests a safe stop and records any
active survey as interrupted.

`HARDWARE_VALIDATION_ENABLED` in `UTILS/config.py` controls optional automatic
session start. Its normal value is `False`; the temporary UI controls remain
the preferred manual validation workflow.

## Configuration Snapshot

At session start, the framework freezes a configuration snapshot containing,
where available:

- validation, session, and configuration identifiers;
- session name, test band, operator notes, antenna, location, and expected
  signal description;
- confirmed receiver center frequency;
- sample rate and FFT size;
- SDR gain mode and numeric gain when manually configured;
- detector name and adaptive-detector parameters;
- temporal-confirmation parameters;
- detector update and validation logging intervals;
- survey measurement defaults;
- active decision mode and SMART-mode state;
- validation software description;
- checked-out Git commit SHA.

Git lookup is supporting metadata only. If it cannot be read safely, the
snapshot stores `unknown` and session creation continues.

## Output Structure

Each session receives a collision-safe directory:

```text
VALIDATION/hardware/results/
  VAL-<timestamp>_SESSION-<timestamp>-<suffix>/
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

CSV files support spreadsheet review. JSON and JSONL preserve structured
records for scripted analysis. `validation.log` provides a timestamped
lifecycle record. The `artifacts/` directory is reserved for supplementary
evidence; automatic screenshots are not currently implemented.

Session result directories are measurement evidence and are intended to remain
local unless an experiment explicitly approves selected results for source
control.

## Recorded Frame Evidence

Frame capture uses `HARDWARE_VALIDATION_LOG_INTERVAL_MS`, independently of the
100 ms display update. The current configured logging interval is 1000 ms.
When validation is inactive, no frame record is generated.

Each accepted frame can contain:

- timestamp and confirmed receiver center frequency;
- strongest finite FFT-bin frequency and relative FFT power;
- average relative FFT power;
- median adaptive threshold;
- spectral-bin occupancy;
- raw peak-candidate count;
- temporally confirmed signal count;
- detector runtime;
- raw candidate and confirmed frequencies;
- current survey recommendation, when one exists;
- application mode (`monitoring` or `survey`).

The strongest FFT bin is a spectral maximum. It is not automatically a
confirmed signal or an identified transmitter.

## Recorded Survey Evidence

When a survey completes, fails, is interrupted, is cleared, or is terminated
by shutdown during an active validation session, the existing survey outcome
is recorded without rerunning or reranking it.

Survey evidence can include:

- requested start, stop, and step frequencies;
- number of measured points and ranked occupancy results;
- completion state and reason;
- selected recommendation;
- decision mode;
- recommended occupancy;
- SMART winner, runner-up, score margin, and confidence when applicable;
- error information for unsuccessful completion.

FREE-mode records correctly leave SMART-only score fields empty.

## Session Summary Metrics

The generated JSON, CSV, and Markdown summaries report:

- start, stop, and total duration;
- logged, valid, and skipped frame counts;
- survey count and completion-state counts;
- average raw candidates and confirmed signals per logged frame;
- average and maximum detector runtime;
- average spectral-bin occupancy;
- frequently observed confirmed frequencies;
- strongest observed FFT bin;
- most frequent SMART recommendation;
- survey recommendation repeatability;
- warnings, errors, operator metadata, and limitations.

Recommendation repeatability is the percentage of recorded recommendations
matching the most common recommendation. It is not a probability that the
recommendation is correct.

## Metric Definitions

| Metric | Meaning |
|---|---|
| Raw candidate | A peak returned by the production adaptive detector before temporal confirmation |
| Confirmed signal | A candidate accepted by the existing temporal confirmation stage |
| Relative FFT power | An uncalibrated FFT-domain value expressed in dB |
| Spectral-bin occupancy | Percentage of FFT bins above the adaptive threshold during the measurement frame |
| Detector runtime | Elapsed time for the production adaptive detector call only |
| Repeated detection | A frequency repeatedly present in confirmed frame records; not proof of signal identity |
| Recommendation repeatability | Agreement among recorded survey recommendations within one validation session |

## Engineering Limitations

- Live RF generally has no known truth labels. A recorded candidate cannot
  automatically be classified as a true signal or false alarm.
- An absent candidate cannot automatically be classified as a missed
  detection.
- FFT power is relative and is not calibrated dBm.
- Spectral-bin occupancy is not regulatory channel occupancy.
- RTL-SDR oscillator error affects absolute frequency accuracy.
- Indoor antenna placement, polarization, cable routing, multipath, local
  interference, gain mode, and receiver temperature affect observations.
- Frame logging is intentionally decimated and does not retain every display
  update.
- Frequently observed frequencies can include interference, receiver
  artifacts, or unresolved signal components.
- Automatic screenshots are not part of the current framework.

## Failure and Shutdown Behavior

Invalid FFT frame inputs are skipped, counted, and written as warnings. A file
write failure disables additional validation writes, records a diagnostic
error where possible, and reports the failure through the validation status
callback without intentionally terminating SPECTRA.

Stopping a session generates summaries and closes the event log. Application
shutdown records the shutdown request before stopping an active session.
Interrupted surveys retain their partial measurements and are labeled
`interrupted`; they are not reported as successful surveys.

## Troubleshooting

### Start does not begin recording

- Confirm no validation session is already active.
- Verify that `VALIDATION/hardware/results/` is writable.
- Read the validation status beside the controls.
- Check the application console for a setup error.

### No frame rows appear

- Confirm the status says validation logging is active.
- Confirm the RTL-SDR is connected and live FFT processing is running.
- Wait longer than the configured validation logging interval.
- Inspect `validation.log` for invalid-frame or write warnings.

### No survey record appears

- A survey record is written only while validation is active.
- Allow the survey to complete, or close/clear it in a way that produces an
  explicit interruption record.
- Inspect `validation.log` for the survey record event.

### Configuration fields appear empty

- Automatic gain intentionally produces `gain_mode: auto` and an empty
  `gain_db`.
- SMART score fields are intentionally empty for FREE-mode surveys.
- Use the current field names `git_commit_sha`, `gain_mode`, `gain_db`, and
  `active_decision_mode` when reviewing JSON.

### Results should not be committed

The complete `VALIDATION/hardware/results/` folder is local experimental
evidence by default. Commit only explicitly reviewed artifacts required by the
final engineering report.

## Production Isolation Statement

Validation mode observes and persists existing outputs. It does not alter
adaptive-detector decisions, temporal confirmation, FFT processing, occupancy
calculation, SDR tuning, survey sequencing, survey ranking, SMART scoring, or
recommendation selection. When inactive, the controller immediately rejects
frame and survey logging requests, leaving only a lightweight function call in
the production path.
