# SPECTRA Hardware Validation Operator Guide

> **Historical document.** The described GUI validation workflow has been
> retired. Current validation uses the standalone REAL-RF capture/replay
> workflow documented in
> [`real_rf_detector_evaluation.md`](real_rf_detector_evaluation.md). This
> guide is retained only as a record of the earlier validation procedure.

## Before the Session

1. Connect the RTL-SDR Blog V3 and dipole antenna.
2. Place the antenna in the planned, documented position.
3. Start SPECTRA and verify **Receiver connected**.
4. Allow the receiver to warm up when the experiment requires frequency
   stability.
5. Select the center frequency, survey range, step, and decision mode required
   by the experiment.
6. Record any experiment-specific notes separately if the fixed
   `HARDWARE_VALIDATION_*` metadata in `UTILS/config.py` does not fully describe
   the run.

Do not change gain, antenna position, sample rate, FFT size, or survey settings
between repeatability runs unless the experiment specifically requires that
change.

## Start Recording

1. Press **Start validation log**.
2. Confirm the status changes to **Validation logging active**.
3. Wait at least one second and confirm that normal FFT and waterfall updates
   continue.
4. Do not press Start again while the session is active.

The session configuration is frozen when Start is pressed. Frame evidence is
recorded at the independent validation interval, currently one record per
second.

## Perform the Experiment

Use SPECTRA normally:

- monitor a fixed center frequency;
- tune manually;
- run FREE or SMART surveys;
- repeat surveys as required by the validation plan.

Keep environmental conditions as stable as practical. Do not interpret live
RF candidates as verified transmitters without an independent reference.

For a survey repeatability experiment:

1. Keep antenna placement and configuration unchanged.
2. Use the same range, step, and decision mode for every run.
3. Complete the required number of surveys within the same validation session
   unless the validation protocol specifies separate sessions.
4. Allow each survey to complete before starting the next one.

## Stop and Save

1. Press **Stop validation log**.
2. Confirm the status changes to **Validation log saved**.
3. Do not close SPECTRA until the saved status appears.

If the application must close while recording, the shutdown path attempts to
save the session safely and marks an active survey as interrupted.

## Locate the Evidence

Open:

```text
VALIDATION/hardware/results/
```

Choose the newest directory beginning with `VAL-`. Review:

1. `validation.log` for the session lifecycle and warnings.
2. `session_config.json` for frozen settings and Git SHA.
3. `frames/frame_records.csv` for time-series measurements.
4. `surveys/survey_records.jsonl` for complete structured survey results.
5. `summaries/summary.md` for the reviewer-readable session report.
6. `summaries/session_summary.json` for machine-readable aggregate values.

## Quick Evidence Check

Before accepting a session:

- CSV and JSONL frame counts agree.
- CSV and JSONL survey counts agree.
- `validation.log` contains session start, configuration saved, first frame,
  stop requested, summary generated, and session stopped.
- Successful surveys are labeled `success`.
- Aborted or shutdown surveys are labeled `interrupted`.
- `errors_encountered` is empty unless a known fault was intentionally tested.
- The Git SHA is a 40-character commit identifier or `unknown`.
- Gain mode, decision mode, sample rate, FFT size, and logging interval match
  the intended experiment.

Automatic gain is represented by `gain_mode: auto` with no numeric `gain_db`.
FREE surveys intentionally have empty SMART-only score fields.

## Minimum Recommended Session Notes

Record the following for each formal experiment:

- experiment identifier;
- date and local time;
- validation session directory;
- test band;
- antenna element length, orientation, and window position;
- receiver warm-up time;
- gain mode;
- expected reference signal, if any;
- unusual interference, movement, weather, or equipment changes.

## Common Problems

### Status remains idle

Press Start once. If recording does not begin, check the application console
and verify that the results directory is writable.

### Session has very few frames

Frame evidence is recorded once per configured logging interval, not on every
display refresh. Longer sessions produce more useful time-series evidence.

### Survey has no recommendation

Inspect `completion_status`, `completion_reason`, and `error_message`. An
interrupted or failed survey must not be treated as a completed recommendation.

### Results contain unexpected frequencies

Live RF lacks automatic ground truth. The observation may be a real signal,
interference, image, DC-related artifact, or transient. Preserve the evidence
and discuss the uncertainty rather than relabeling the result.

### Application closes during recording

Restart SPECTRA and inspect the newest session. A correctly handled shutdown
contains a shutdown event, an interrupted survey record when applicable, and a
generated summary.

## End-of-Session Rule

Do not commit raw hardware session folders automatically. First review data
quality, identify the sessions required by the approved validation experiment,
and select only the evidence intended for the final report.
