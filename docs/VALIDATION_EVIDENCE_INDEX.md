# SPECTRA Validation Evidence Index

## Purpose and Evidence Boundaries

This index maps release claims to the fastest authoritative evidence for
reviewers. Validation claims are intentionally conservative:

- FFT power is relative dB, not calibrated dBm.
- Occupancy is the fraction of spectral bins above their corresponding
  thresholds during a measurement window.
- Contextual labels and behavior descriptors are not signal identification or
  modulation recognition.
- SMART is deterministic heuristic scoring, not AI or machine learning.
- REAL-RF replay supports repeatability, runtime, and capped top-three
  frequency-agreement observations—not absolute detection accuracy.

## 1. DSP Validation

| Claim | Evidence | Location | Result | Limitation |
| --- | --- | --- | --- | --- |
| A bin-centered complex tone is placed at the expected shifted FFT frequency. | AV-FFT-01 trials, summary, workbook, and frequency-error plot; FFT unit tests | [`VALIDATION/results/AV-FFT-01_CFG-S01_20260721/`](../VALIDATION/results/AV-FFT-01_CFG-S01_20260721/); `tests/test_fft_processing.py`; `tests/test_frequency_and_occupancy.py` | PASS | Synthetic bin-centered tones do not measure RTL-SDR oscillator error. |
| Hann processing preserves tested bin-centered relative amplitude and reduces tested off-bin leakage. | AV-FFT-02 window comparison and raw trials | [`VALIDATION/results/AV-FFT-02_CFG-S01_20260721/`](../VALIDATION/results/AV-FFT-02_CFG-S01_20260721/); `tests/test_fft_processing.py` | PASS | Relative numerical amplitude only; no calibrated analog amplitude claim. |
| Frequency axes and image edges are centered and evenly spaced. | Direct frequency-axis and occupancy unit tests | `tests/test_frequency_and_occupancy.py`; `UTILS/frequency_axis.py` | PASS | Does not characterize physical tuner-frequency accuracy. |
| The local percentile estimator follows the tested flat, curved, and stepped baselines without narrow-peak domination. | AV-NF-01 raw trials, summary, plot, and local-floor unit tests | [`VALIDATION/results/AV-NF-01_CFG-S01_20260722/`](../VALIDATION/results/AV-NF-01_CFG-S01_20260722/); `tests/test_local_noise_floor.py` | PASS | Synthetic baselines cannot predict every real receiver artifact or clutter environment. |

## 2. Detection Validation

| Claim | Evidence | Location | Result | Limitation |
| --- | --- | --- | --- | --- |
| Adaptive-detector response increases with controlled synthetic SNR. | AV-PD-01 SNR sweep and detector tests | [`VALIDATION/results/AV-PD-01_CFG-S01_20260722/`](../VALIDATION/results/AV-PD-01_CFG-S01_20260722/); `tests/test_detection.py` | PASS under tested conditions | Does not establish live-RF probability of detection. |
| Raw noise-only behavior is characterized rather than assumed. | AV-PD-02 false-alarm trials | [`VALIDATION/results/AV-PD-02_CFG-S01_20260722/`](../VALIDATION/results/AV-PD-02_CFG-S01_20260722/) | KNOWN LIMITATION / acceptance criterion failed | Metric is SPECTRA frame-level behavior, not classical per-cell CFAR `Pfa`. |
| Two tones are resolved at the configured 75 kHz spacing boundary under tested conditions. | AV-PD-03 separation sweep and plots | [`VALIDATION/results/AV-PD-03_CFG-S01_20260722/`](../VALIDATION/results/AV-PD-03_CFG-S01_20260722/) | PASS | Strong deterministic tones do not characterize all low-SNR or unequal-amplitude cases. |
| The minus-15 dB bandwidth heuristic is repeatable over part of the tested width range. | AV-BW-01 trials and estimated-versus-controlled plots | [`VALIDATION/results/AV-BW-01_CFG-S01_20260722/`](../VALIDATION/results/AV-BW-01_CFG-S01_20260722/); OS-CFAR bandwidth regression tests | KNOWN LIMITATION / acceptance criterion failed | Descriptive peak width only; not regulatory occupied bandwidth. |
| Spectral-bin occupancy equals the known above-threshold fraction in controlled arrays. | AV-OCC-01 exact-fraction trials and occupancy tests | [`VALIDATION/results/AV-OCC-01_CFG-S01_20260722/`](../VALIDATION/results/AV-OCC-01_CFG-S01_20260722/); `tests/test_frequency_and_occupancy.py` | PASS | Not channel-time occupancy or regulatory utilization. |
| Temporal confirmation behavior is characterized over consecutive noise frames. | AV-PC-01 frame/window records and suppression plots | [`VALIDATION/results/AV-PC-01_CFG-S01_20260722/`](../VALIDATION/results/AV-PC-01_CFG-S01_20260722/); `tests/test_peak_confirmation.py` | KNOWN LIMITATION / acceptance criterion failed | Existing confirmer did not sufficiently suppress the defined synthetic noise candidates. |

## 3. Decision-Engine Validation

| Claim | Evidence | Location | Result | Limitation |
| --- | --- | --- | --- | --- |
| SMART score components and maximum score are deterministic. | Component, maximum-score, fallback, and feature-snapshot tests | `tests/test_decision_engine.py`; `SURVEY/decision_engine.py`; `UTILS/config.py` | PASS | Weights are an explainable engineering heuristic, not learned or optimized against ground truth. |
| Free, active, and SMART modes rank candidates according to their declared objectives. | Ranking and opposite-mode tests | `tests/test_decision_engine.py`; `tests/test_survey_manager.py` | PASS | Recommendation quality depends on measurement quality and configured rules. |
| Candidate ties are resolved independently of insertion order. | Explicit tie-breaking test | `tests/test_decision_engine.py` | PASS | Deterministic resolution is not proof that tied candidates differ physically. |
| Reports expose winner, runner-up, margin, confidence, component scores, rationale, and diagnostics. | HTML/text output tests and reviewed report UI | `tests/test_survey_manager.py`; `tests/test_ui_status_html.py`; `SURVEY/survey_manager.py`; `UI/survey_popup.py` | PASS | Confidence is score separation, not statistical confidence. Diagnostics are observational. |

## 4. Hardware and Operational Validation

| Claim | Evidence | Location | Result | Limitation |
| --- | --- | --- | --- | --- |
| SPECTRA opens, reads, and closes the RTL-SDR Blog V3 during normal operation. | Repeated manual smoke tests and successful REAL-RF capture sessions | Historical operator records; nine REAL-RF dataset metadata records; `tests/test_sdr_worker.py` | Operationally verified | No commercial reliability, calibrated sensitivity, or cross-platform guarantee. |
| Confirmed receiver center changes only after successful tuning. | Worker confirmed-center and failed-tune tests | `tests/test_sdr_worker.py`; `SDR/sdr_worker.py` | PASS | Successful driver tuning is not calibrated frequency-accuracy evidence. |
| Survey measurements follow confirmed tune and settling rather than a blocking fixed wait. | Event-order, stale-confirmation, failure, cancellation, and completion tests; live surveys | `tests/test_survey_controller.py`; `SURVEY/survey_controller.py` | PASS and operationally verified | Settling adequacy is configuration- and receiver-dependent. |
| Auto-Tune and recommendation status remain consistent across success, failure, clear, and manual-tune actions. | Status-state and timer-cancellation tests; manual hardware testing | `tests/test_survey_controller.py`; `tests/test_ui_status_html.py` | PASS | Hardware disconnection may still require operator recovery. |

The retired GUI validation logger is documented in the four historical
hardware-validation documents. Those files preserve engineering history but
are not the current operator workflow.

## 5. REAL-RF Validation

| Claim | Evidence | Location | Result | Limitation |
| --- | --- | --- | --- | --- |
| Nine antenna-connected RF environments were captured and replayed. | FM 100.3/95.5/107.1 MHz; NOAA 162.550/162.475 MHz; 2-meter 146.520/145.500 MHz; airband 125 MHz; nominally quiet 300 MHz | [REAL-RF campaign report](REAL_RF_VALIDATION_CAMPAIGN_REPORT.md); local `VALIDATION/real_rf/reports/RF-*` report sets | COMPLETE | Datasets are local/external release evidence and require checksum-controlled archival storage. |
| Both detectors receive identical immutable IQ-derived FFT input. | Dataset immutability, replay equivalence, and read-only adapter tests | `tests/test_real_rf_validation.py`; [REAL-RF framework document](real_rf_detector_evaluation.md) | PASS | Identical input controls comparison conditions but does not create signal ground truth. |
| Detector outputs are deterministic on repeated replay. | Two complete replays per dataset and automated repeatability tests | Campaign report; per-dataset `adaptive_results.json`, `os_cfar_results.json`, and `comparison.json`; `tests/test_real_rf_validation.py` | PASS | Reproducibility applies to saved data and frozen software/configuration. |
| Adaptive and OS-CFAR capped top-three frequency selections can be compared. | Pairwise frequency matching and per-dataset summaries | Per-dataset `pairwise_comparison.csv`, `detections.csv`, and `summary.txt`; campaign report | COMPLETE | Agreement is not correctness; both output lists are capped at three. |
| OS-CFAR required approximately 30–32 times greater mean detector runtime in the recorded campaign. | Saved per-dataset runtime summaries | [REAL-RF campaign report](REAL_RF_VALIDATION_CAMPAIGN_REPORT.md) | OBSERVED | Host-, build-, dataset-, and configuration-specific; not a universal benchmark. |
| Adaptive remains the production detector and OS-CFAR remains a standalone baseline. | Frozen synthetic comparison, final assessment, and REAL-RF review | [DE-CMP-01 engineering summary](../VALIDATION/results/DE-CMP-01_CFG-C01_20260724/DE-CMP-01_CFG-C01_engineering_summary.md); [final assessment](detection_engine_final_assessment.md); campaign report | DECISION COMPLETE | This is an engineering production decision, not a claim of universal detector superiority. |

## 6. Regression and Release Verification

| Claim | Evidence | Location | Result | Limitation |
| --- | --- | --- | --- | --- |
| Current deterministic software behavior passes the complete automated suite. | 279 tests across 28 test modules | `tests/`; [environment freeze report](ENVIRONMENT_FREEZE_REPORT.md) | `Ran 279 tests` — `OK` | Automated tests do not validate USB hardware, antenna conditions, propagation, or calibrated RF performance. |
| The pinned Python environment is internally consistent. | Exact dependency audit, `pip check`, CLI smoke checks | `requirements.txt`; [environment configuration](ENVIRONMENT_CONFIGURATION.md); environment freeze report | PASS | Package hashes and non-macOS platform qualification remain outside the current freeze. |

## Evidence-Document Review

### Authoritative release evidence

- `docs/REAL_RF_VALIDATION_CAMPAIGN_REPORT.md`
- `docs/detection_engine_final_assessment.md`
- `docs/real_rf_detector_evaluation.md`
- `VALIDATION/validation_matrix.csv`
- `VALIDATION/results/*/README.md` and primary summaries
- `docs/ENVIRONMENT_CONFIGURATION.md`
- `docs/ENVIRONMENT_FREEZE_REPORT.md`

### Historical documents

- `docs/detection_engine_evolution_phase1.md` through `phase4.md`
- `docs/hardware_validation_framework.md`
- `docs/hardware_validation_operator_guide.md`
- `docs/hardware_validation_safety_performance.md`
- `docs/hardware_validation_framework_final_report.md`

The detector-evolution documents preserve decision history. The hardware
validation documents describe the retired GUI workflow and are explicitly
marked historical.

### Duplicate and supporting artifacts

- CSV, JSON, workbook, and PNG outputs within one experiment are complementary
  formats, not contradictory results.
- `*.inspect.ndjson` files are workbook-generation QA traces and are not
  primary measurement evidence.
- Header-only files under `VALIDATION/templates/` are procedures/templates,
  not completed evidence.
- Per-dataset REAL-RF reports intentionally repeat the same output schema for
  nine distinct captures.

### Missing final-release references

- A final tagged-commit test log has not yet been packaged as a standalone
  release artifact.
- Final UI/demo screenshots and a backup demonstration recording remain to be
  selected.
- External IQ archives need a dataset manifest, storage location, and
  cryptographic checksums.
- A final report/paper and presentation should cite this index rather than
  linking directly to every raw artifact.

