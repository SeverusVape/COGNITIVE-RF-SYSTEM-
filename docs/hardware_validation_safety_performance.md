# Hardware Validation Safety and Performance Verification

## Scope

This Stage 13 review verifies that the temporary SPECTRA hardware-validation
framework remains observational and does not change production detector,
survey, SDR, FFT, waterfall, or SMART behavior. It records automated evidence
and defines the final manual checks required with the RTL-SDR.

No detector thresholds, confirmation parameters, survey rules, ranking rules,
or application features are changed by this stage.

## Verification Matrix

| Requirement | Verification method | Evidence | Status |
|---|---|---|---|
| Inactive validation has negligible work | Regression test verifies immediate return before time providers, receiver-state providers, record construction, or filesystem creation | `test_inactive_mode_short_circuits_before_capture_work` | Automated pass |
| Inactive validation writes no records | Controller test attempts frame and survey capture before session start | `test_inactive_controller_ignores_frame_and_survey_records` | Automated pass |
| Detector evidence is unchanged | Deterministic complex-IQ spectrum is detected, logged, compared for mutation, and detected again | `test_active_logging_does_not_mutate_detector_evidence` | Automated pass |
| Frame logging is decimated | Controlled monotonic clock verifies the independent validation interval | `test_logging_interval_controls_frame_evidence` | Automated pass |
| Files close and summaries are generated | Simulated full session starts, records frames and a survey, stops, and reads all outputs | `test_complete_simulated_session_generates_consistent_evidence` | Automated pass |
| Shutdown safely stops an active session | Controller shutdown test verifies inactive final state and shutdown event | `test_shutdown_stops_active_session` | Automated pass |
| Interrupted survey is labeled honestly | Existing survey-controller tests and manual shutdown session preserve `interrupted` state | Survey tests and local hardware smoke test | Verified |
| Write failures do not crash production logic | Permission, missing-directory, serialization, frame-write, and summary-write failures are injected | Hardware validation logger tests | Automated pass |
| UI remains responsive while recording | Observe FFT, waterfall, controls, tuning, and survey transitions during a live session | Manual procedure below | Operator check required |
| Normal application behavior remains correct | Run monitoring, manual tune, Auto-Tune, FREE survey, and SMART survey with validation inactive and active | Manual procedure below | Operator check required |

## Detector Equivalence Boundary

The validation call occurs after production FFT processing and adaptive peak
detection. The regression test supplies deterministic complex IQ containing
two tones and seeded noise, then:

1. computes the production windowed FFT;
2. runs the production adaptive detector;
3. records those outputs through an active validation controller;
4. verifies that frequency, power, threshold, and peak values were not
   mutated;
5. reruns the production detector and compares its output exactly.

This establishes deterministic software non-interference for the tested
pipeline. It does not claim equivalence for every possible hardware,
operating-system, or RF condition.

## Inactive-Mode Performance Boundary

When validation is inactive, `log_frame()` checks controller activity and
returns before:

- reading the monotonic clock;
- reading confirmed receiver frequency;
- converting NumPy values;
- constructing a validation record;
- serializing data;
- accessing the filesystem.

The inactive path therefore consists of a controller state check and return.
The structural regression test is preferred over a fragile wall-clock
threshold because it directly verifies that expensive operations are not
reached. No claim of exactly zero overhead is made.

## Active-Mode Performance Boundary

When active, frame logging is limited by
`HARDWARE_VALIDATION_LOG_INTERVAL_MS`, currently 1000 ms, independently of the
100 ms display update. A logged frame performs record conversion and appends
one CSV row and one JSONL object. Surveys are written only when a survey event
occurs. Summary generation occurs at session stop.

The current implementation uses short synchronous file appends and does not
introduce a logging thread or queue. Hardware observation is therefore
required to confirm that the chosen interval does not create visible UI
freezing on the target computer.

## Manual RTL-SDR Verification Procedure

Use one short smoke-test session. Raw result folders remain local.

### A. Validation inactive

1. Start SPECTRA with validation inactive.
2. Confirm RTL-SDR connection.
3. Observe FFT and waterfall motion for at least 15 seconds.
4. Perform one manual tune.
5. Run one short survey.
6. Confirm normal status-card, survey, and recommendation behavior.

### B. Validation active

1. Press **Start validation log**.
2. Confirm **Validation logging active**.
3. Observe FFT and waterfall motion for at least 15 seconds.
4. Interact with the frequency input and controls.
5. Perform one manual tune.
6. Run one FREE or SMART survey to completion.
7. Confirm no visible freeze, crash, or abnormal survey transition.
8. Press **Stop validation log** and wait for **Validation log saved**.

### C. Safe shutdown

1. Start another validation session.
2. Begin a survey.
3. Close SPECTRA before the survey completes.
4. Reopen the newest local result directory.
5. Confirm `validation.log` contains the shutdown event.
6. Confirm the survey record is `interrupted`.
7. Confirm a session summary exists and files are readable.

### D. Evidence consistency

For each accepted session:

- frame CSV data-row count equals frame JSONL line count;
- survey CSV data-row count equals survey JSONL line count;
- summary frame and survey totals match the raw files;
- configuration includes sample rate, FFT size, gain mode, decision mode, and
  Git SHA;
- warnings and errors contain only expected test conditions.

## Acceptance Criteria

Stage 13 is accepted when:

- the focused hardware-validation tests pass;
- the complete repository test suite passes;
- deterministic detector evidence remains unchanged;
- inactive mode performs no capture or persistence work;
- the operator observes no material FFT, waterfall, tuning, or survey
  regression in the manual procedure;
- normal stop and shutdown both leave readable evidence;
- any interrupted survey is labeled honestly;
- no production detector or decision logic is modified.

## Limitations

- Automated tests cannot measure subjective UI smoothness on the operator's
  computer.
- A short smoke test does not establish long-duration storage performance.
- Detector equivalence is deterministic software evidence, not RF ground
  truth.
- Filesystem performance can vary across systems and storage devices.
- Validation logging remains a temporary engineering subsystem and is not an
  end-user feature.
