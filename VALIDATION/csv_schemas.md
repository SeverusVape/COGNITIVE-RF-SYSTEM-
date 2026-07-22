# CSV Schemas and Data Dictionary

Templates are header-only. Copy a template to a dated result file before data
collection. Do not enter results directly into the templates.

## Common conventions

- Encoding: UTF-8
- Separator: comma
- Decimal separator: period
- Timestamp: ISO 8601 with UTC offset
- Boolean values: `true` or `false`
- Missing/not-applicable values: `NA`
- Frequencies ending in `_hz`: Hz
- Frequencies ending in `_khz`: kHz
- Relative FFT quantities: dB, never dBm
- Percentages: numeric 0–100 without the `%` character
- Each row represents one raw trial or one candidate within a survey run

## `synthetic_detector_trials.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | Matrix ID such as `AV-PD-01` |
| configuration_id | text | Frozen configuration identifier |
| trial_id | integer | Unique trial within condition |
| timestamp | datetime | Trial generation time |
| random_seed | integer | Seed needed to reproduce trial |
| condition | text | `tone_noise`, `noise_only`, `two_tone`, `bandwidth`, or `occupancy` |
| sample_rate_hz | float | Synthetic IQ sample rate |
| fft_size | integer | Number of complex samples |
| noise_model | text | Noise distribution and shaping |
| snr_definition | text | Exact SNR definition |
| snr_db | float/NA | Configured SNR |
| tone_1_hz | float/NA | First tone offset or absolute test frequency |
| tone_2_hz | float/NA | Second tone frequency |
| tone_separation_khz | float/NA | Absolute tone separation |
| relative_tone_2_db | float/NA | Tone 2 relative to tone 1 |
| controlled_bandwidth_khz | float/NA | Known generated signal width |
| expected_occupancy_percent | float/NA | Known occupied-bin fraction |
| expected_peak_count | integer | Expected number of peaks |
| detected_peak_count | integer | Returned peak count |
| detected_frequency_1_hz | float/NA | First detected frequency |
| detected_frequency_2_hz | float/NA | Second detected frequency |
| frequency_error_1_hz | float/NA | Signed error for matched first peak |
| estimated_bandwidth_1_khz | float/NA | Detector bandwidth estimate |
| measured_occupancy_percent | float/NA | Calculated occupancy |
| local_floor_median_db | float | Median estimated noise floor |
| threshold_median_db | float | Median adaptive threshold |
| detected | boolean | Whether the intended signal was detected |
| valid | boolean | Trial validity |
| notes | text | Failure reason or special condition |

## `fft_frequency_trials.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `AV-FFT-01` |
| configuration_id | text | Frozen synthetic configuration |
| trial_id | integer | Unique trial number |
| timestamp | datetime | Execution time with UTC offset |
| random_seed | integer | Resolved seed used for the trial phase |
| sample_rate_hz | float | Synthetic IQ sample rate |
| fft_size | integer | Number of complex samples |
| bin_spacing_hz | float | Sample rate divided by FFT size |
| shifted_bin_index | integer | Index in the shifted FFT array |
| tone_offset_hz | float | Expected tone offset from center |
| phase_rad | float | Deterministic randomized starting phase |
| measured_offset_hz | float | Frequency-axis value at maximum FFT bin |
| error_hz | float | Measured offset minus expected offset |
| absolute_error_hz | float | Absolute frequency error |
| peak_relative_db | float | Relative FFT peak; not calibrated dBm |
| acceptance_limit_hz | float | Half-bin frequency-error limit |
| passed | boolean | Whether absolute error is within the limit |
| notes | text | Trial qualification or anomaly |

## `fft_window_trials.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `AV-FFT-02` |
| configuration_id | text | Frozen synthetic configuration |
| trial_id | integer | Unique spectrum evaluation |
| timestamp | datetime | Execution time with UTC offset |
| random_seed | integer | Seed used for the paired tone phase |
| window_type | text | `Rectangular` or coherent-gain-corrected `Hann` |
| sample_rate_hz | float | Synthetic IQ sample rate |
| fft_size | integer | Number of complex samples |
| bin_spacing_hz | float | Sample rate divided by FFT size |
| integer_bin_offset | integer | Integer FFT-bin location from center |
| fractional_bin_offset | float | Tone displacement from the integer bin |
| tone_offset_hz | float | Exact generated tone offset from center |
| phase_rad | float | Deterministic randomized starting phase |
| detected_bin_offset | float | Detected maximum-bin offset from center |
| peak_relative_db | float | Relative FFT peak; not calibrated dBm |
| ideal_peak_db | float | Ideal coherent bin-centered peak for a unit tone |
| peak_error_db | float | Measured peak minus ideal peak |
| protected_half_width_bins | integer | Bins protected on each side of peak |
| leakage_relative_db | float | Energy outside protected region relative to total energy |
| maximum_sidelobe_relative_db | float | Strongest bin outside protected region relative to peak |
| centered_peak_limit_db | float | Absolute centered-tone peak-error criterion |
| minimum_off_bin_improvement_db | float | Hann leakage-improvement criterion |
| passed | boolean | Per-row centered-peak criterion result |
| notes | text | Scope and leakage definition |

## `frequency_accuracy.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `HV-FREQ-01` or `HV-FREQ-02` |
| configuration_id | text | Frozen hardware configuration |
| session_id | text | Measurement session identifier |
| observation_id | integer | Sequential observation |
| timestamp | datetime | Observation time |
| elapsed_seconds | float | Time since receiver power-on/session start |
| reference_name | text | Source identifier |
| reference_basis | text | Why the expected value is credible |
| expected_frequency_hz | float | Reference frequency |
| measured_frequency_hz | float | Measured peak estimate |
| error_hz | float | Measured minus expected |
| error_khz | float | Error in kHz |
| error_ppm | float | Approximate ppm error |
| peak_relative_db | float | Relative FFT peak level |
| peak_above_floor_db | float | Peak minus local floor |
| valid | boolean | Observation validity |
| notes | text | Environment or anomaly note |

## `relative_amplitude.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `HV-AMP-01` or `HV-AMP-02` |
| configuration_id | text | Fixed-gain configuration |
| session_id | text | Measurement session |
| observation_id | integer | Sequential observation |
| timestamp | datetime | Observation time |
| source_name | text | Stable source identifier |
| source_frequency_hz | float | Source frequency |
| gain_db | float | Fixed receiver gain; `NA` is not acceptable for linearity test |
| applied_attenuation_db | float/NA | Known attenuation from reference condition |
| peak_relative_db | float | Measured relative FFT peak |
| local_floor_db | float | Estimated local noise floor |
| peak_above_floor_db | float | Relative peak minus local floor |
| observed_change_db | float/NA | Change from zero/reference attenuation |
| residual_error_db | float/NA | Observed change minus expected change |
| valid | boolean | Observation validity |
| notes | text | Source/gain/environment note |

## `occupancy_noise.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `HV-NF-01`, `HV-OCC-01`, or `HV-OCC-02` |
| configuration_id | text | Frozen hardware configuration |
| session_id | text | Measurement session |
| observation_id | integer | Sequential observation |
| timestamp | datetime | Observation time |
| condition | text | `terminated`, `quiet`, `active`, `source_off`, or `source_on` |
| center_frequency_hz | float | Receiver center |
| span_hz | float | Visible sample-rate span |
| gain_mode | text | `fixed` or `auto` |
| gain_db | float/NA | Fixed gain value if applicable |
| median_noise_floor_db | float/NA | Median estimated local floor |
| median_threshold_db | float | Median adaptive threshold |
| occupancy_percent | float | Spectral-bin occupancy |
| raw_peak_count | integer/NA | Pre-confirmation peak count if retained |
| confirmed_peak_count | integer | Confirmed peaks displayed/used |
| source_state | text/NA | `on` or `off` for controlled test |
| valid | boolean | Observation validity |
| notes | text | Environmental note |

## `smart_survey_runs.csv`

One row describes one completed survey.

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `HV-SMART-01`, `HV-SMART-02`, or `HV-SEQ-01` |
| configuration_id | text | Frozen hardware configuration |
| session_id | text | Session identifier |
| survey_run_id | text | Unique survey identifier |
| timestamp_start | datetime | Survey start |
| timestamp_end | datetime | Survey completion |
| start_mhz | float | Survey start |
| stop_mhz | float | Survey stop |
| step_mhz | float | Survey step |
| decision_mode | text | `FREE`, `ACTIVE`, or `SMART` |
| expected_point_count | integer | Generated survey points |
| completed_point_count | integer | Stored valid measurements |
| recommended_frequency_mhz | float | Winner |
| recommended_score | float/NA | SMART winner score |
| runner_up_frequency_mhz | float/NA | Runner-up |
| runner_up_score | float/NA | Runner-up score |
| score_margin | float/NA | Winner minus runner-up |
| confidence_class | text/NA | `LOW`, `MODERATE`, or `HIGH` |
| auto_tune_confirmed | boolean | Receiver confirmed at recommendation |
| survey_completed | boolean | Successful completion |
| error_code | text/NA | Failure category |
| notes | text | Environmental or procedural note |

## `smart_survey_candidates.csv`

One row describes one frequency candidate within a survey run.

| Column | Type | Meaning |
| --- | --- | --- |
| configuration_id | text | Frozen configuration |
| survey_run_id | text | Parent survey identifier |
| candidate_frequency_mhz | float | Survey frequency |
| occupancy_percent | float | Aggregated spectral-bin occupancy |
| max_relative_power_db | float | Aggregated maximum relative FFT level |
| average_relative_power_db | float | Aggregated mean relative FFT level |
| occupancy_score | float/NA | SMART occupancy contribution |
| power_score | float/NA | SMART relative-power contribution |
| persistence_score | float/NA | SMART persistence contribution |
| age_score | float/NA | SMART age contribution |
| strength_score | float/NA | SMART strength contribution |
| total_score | float/NA | Candidate total |
| rank | integer | Candidate rank by active policy |
| selected | boolean | Recommended candidate |
| diagnostic_observations | integer/NA | Evidence maturity count |
| frequency_stability_percent | float/NA | Observational diagnostic |
| bandwidth_stability_percent | float/NA | Observational diagnostic |
| frequency_drift_khz | float/NA | Observational diagnostic |
| duty_cycle_percent | float/NA | Recent activity diagnostic |
| valid | boolean | Candidate record validity |
| notes | text | Special condition |

## `survey_sequence.csv`

| Column | Type | Meaning |
| --- | --- | --- |
| validation_id | text | `HV-SEQ-01` |
| configuration_id | text | Frozen configuration |
| survey_run_id | text | Parent survey |
| point_index | integer | One-based survey position |
| requested_frequency_hz | float | Frequency requested by controller |
| tune_request_timestamp | datetime | Request time |
| confirmed_frequency_hz | float/NA | Worker-confirmed center |
| tune_confirm_timestamp | datetime/NA | Confirmation time |
| confirmation_error_hz | float/NA | Confirmed minus requested |
| settling_delay_ms | integer | Configured delay |
| measurement_timestamp | datetime/NA | Aggregated measurement time |
| valid_frame_count | integer/NA | Frames available for aggregation |
| result_stored | boolean | Whether point was accepted |
| status | text | `complete`, `tune_failed`, `measurement_failed`, or `cancelled` |
| notes | text | Sequence anomaly |
