# RF Validation Evidence Package

This directory defines the validation plan for the COGNITIVE-RF-SYSTEM
application baseline at commit `73f06b9` and validation-planning baseline at
commit `4cf57b6`. It separates deterministic algorithm validation
from RTL-SDR hardware/system validation and defines the records required for
reproducible final-report evidence.

No measurement result should be entered until the configuration record for the
session is complete. Application algorithms, decision weights, and processing
settings remain frozen during the validation campaign.

## Current release status

The validation package now contains completed engineering evidence in addition
to its original planning records:

- deterministic synthetic DSP validation;
- adaptive-detector characterization;
- temporal confirmation, peak-spacing, bandwidth, and occupancy studies;
- frozen Adaptive-versus-OS-CFAR comparison;
- nine antenna-connected REAL-RF complex-IQ datasets;
- immutable detector replay and frequency-agreement comparison; and
- detector runtime comparison.

The Adaptive Detector is the production detector. OS-CFAR remains an
independent research and validation baseline. The REAL-RF campaign supports
repeatability, capped top-three frequency-agreement, and runtime observations;
it does not establish detection accuracy or false-alarm probability without
controlled ground truth.

Rows and templates marked as planned are retained as historical planning
records or future controlled-characterization proposals. Their presence does
not mean those experiments were completed by the REAL-RF campaign.

## Package contents

| File | Purpose |
| --- | --- |
| `validation_matrix.csv` | Traceability from feature and claim to experiment and report artifact |
| `experiments.md` | Ordered experimental procedures and completion criteria |
| `csv_schemas.md` | Data dictionary, units, allowed values, and recording rules |
| `configuration_record.csv` | Frozen baseline plus blank session-specific configuration fields |
| `equipment_inventory.csv` | Available and pending physical/software validation resources |
| `reference_signal_inventory.csv` | Candidate synthetic, controlled, and live RF references |
| `resource_plan.md` | Experiment dependencies, fallbacks, gates, and execution order |
| `report_outputs.md` | Required plots, tables, captions, and engineering conclusions |
| `templates/*.csv` | Header-only measurement templates for each experiment family |

## Validation domains

### Algorithm validation — synthetic data

Synthetic complex samples provide known frequencies, amplitudes, separations,
bandwidths, and noise conditions. These tests validate the FFT, threshold,
detector, bandwidth heuristic, and occupancy calculations without antenna,
tuner, oscillator, or propagation uncertainty.

### Hardware/system validation — RTL-SDR

Hardware tests characterize the complete receive chain, including oscillator
error, warm-up behavior, gain behavior, environmental RF, survey repeatability,
and SMART decision repeatability. Results are valid for the recorded receiver,
antenna, location, settings, and time—not for every RTL-SDR installation.

## Measurement freeze rules

1. Record the Git commit and complete `configuration_record.csv`.
2. Use one configuration ID for every row produced under the same settings.
3. Do not change gain, sample rate, FFT size, detector constants, antenna, or
   source placement inside a comparison series.
4. If any setting changes, create a new configuration ID.
5. Preserve raw observations. Calculate summaries in separate derived files.
6. Record failed and invalid trials; do not silently delete them.
7. Use `NA` for a field that is not applicable and leave no ambiguous blanks.
8. Record all timestamps in ISO 8601 format with UTC offset.
9. Treat FFT values as relative dB. Never relabel them as dBm.
10. Treat occupancy as spectral-bin occupancy for the measurement window, not
    regulatory or long-term channel occupancy.

## File naming

Use:

```text
<experiment_id>_<configuration_id>_<YYYYMMDD>_<descriptor>.csv
```

Example:

```text
HV_FREQ_ACC_CFG-H01_20260722_known_carriers.csv
```

Recommended generated figures use the same prefix and a descriptive suffix:

```text
HV_FREQ_ACC_CFG-H01_20260722_error_vs_frequency.png
```

## Evidence status

At creation, the matrix, procedures, configuration records, inventories, and
templates were planning artifacts. They remain part of the historical
engineering record. Completion status is recorded explicitly in the validation
matrix and result directories; blank templates do not contain measurements and
do not imply that an experiment has passed.

The completed REAL-RF campaign is documented in
[`docs/REAL_RF_VALIDATION_CAMPAIGN_REPORT.md`](../docs/REAL_RF_VALIDATION_CAMPAIGN_REPORT.md).
Controlled ground-truth and calibrated RF characterization remain future work.

## Hardware frame field semantics

Hardware-validation frame records use
`strongest_fft_bin_frequency_hz` and `strongest_fft_bin_power_db` for the
frequency and relative power of the maximum FFT bin in a captured frame. These
fields describe a spectral maximum only. They do not imply that the bin passed
the peak detector, survived temporal confirmation, or represents an identified
RF signal. Confirmed signal evidence is recorded separately in
`confirmed_frequencies_hz`; confirmed-signal power is not recorded because the
current confirmation output does not provide an independent reliable power
value.

## Invalid hardware frames

The hardware frame builder returns `None` when FFT frequency and power arrays
are empty, have different lengths, cannot be converted to numeric arrays, or
contain no finite frequency/power pair. The active validation session records a
warning and skips that frame; the production application continues running.
For length-matched arrays containing a mixture of finite and invalid values,
only finite frequency/power pairs are used to calculate the maximum FFT bin and
average relative power. Skipped frames do not consume a logged frame index.

## Validation write failures

Configuration, frame, survey, and summary writes are isolated from production
SDR processing. If a filesystem or serialization operation fails, the logger
records the operation and exception in the session error list, disables further
validation writes, closes the active validation state, and notifies the
temporary validation UI. SPECTRA continues monitoring normally. A failed
evidence session must be treated as incomplete; validation should be restarted
only after the reported storage problem is corrected.
