# RF Validation Evidence Package

This directory defines the validation plan for the COGNITIVE-RF-SYSTEM
application baseline at commit `73f06b9` and validation-planning baseline at
commit `4cf57b6`. It separates deterministic algorithm validation
from RTL-SDR hardware/system validation and defines the records required for
reproducible final-report evidence.

No measurement result should be entered until the configuration record for the
session is complete. Application algorithms, decision weights, and processing
settings remain frozen during the validation campaign.

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

At creation, all files in this package are planning artifacts. The templates do
not contain measurements and do not imply that an experiment has passed.
