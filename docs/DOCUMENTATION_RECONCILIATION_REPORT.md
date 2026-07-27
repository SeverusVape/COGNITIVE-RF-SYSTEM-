# SPECTRA Documentation Reconciliation Report

## Scope

This Phase 1 reconciliation aligns release-facing documentation with the
current SPECTRA repository state. It changes documentation only. No Python
source, detector algorithm, SMART logic, survey behavior, validation data, or
generated validation result was modified or regenerated.

## Changes

| File | Old issue | Correction | Reason |
| --- | --- | --- | --- |
| `README.md` | Reported 138 tests and described hardware characterization as the next validation phase | Records 279 passed tests, completed synthetic and nine-dataset REAL-RF validation, the production detector decision, and remaining controlled ground-truth work | Align the primary project document with current release evidence |
| `VALIDATION/README.md` | Described all package contents as planning artifacts | Adds current evidence status while preserving original plans and templates as historical records | Distinguish completed evidence from unexecuted controlled tests |
| `VALIDATION/validation_matrix.csv` | Did not represent the completed REAL-RF campaign or explicitly separate future ground-truth testing | Adds one completed REAL-RF comparison row and one future controlled ground-truth row; existing planned rows remain | Maintain traceability without erasing historical plans |
| `docs/hardware_validation_framework.md` | Presented retired GUI logging as current | Adds a historical-workflow notice and points to standalone capture/replay documentation | Prevent operator confusion while preserving engineering history |
| `docs/hardware_validation_operator_guide.md` | Instructed use of removed GUI controls | Marks the guide historical and links the current workflow | Prevent obsolete operating instructions from being followed |
| `docs/hardware_validation_safety_performance.md` | Described the retired GUI validation workflow | Adds a historical notice while preserving conclusions | Retain evidence without presenting obsolete integration as current |
| `docs/hardware_validation_framework_final_report.md` | Presented the temporary GUI subsystem as active | Marks the subsystem retired and the report historical | Preserve the completed milestone accurately |
| `docs/real_rf_detector_evaluation.md` | Correctly kept selection outside the framework but did not state the later project-level production decision | Adds the Adaptive production decision and its conservative evidence boundary | Connect framework documentation to final release status |
| `docs/REAL_RF_VALIDATION_CAMPAIGN_REPORT.md` | Correctly avoided an automatic winner but did not state the later production disposition | Adds the final Adaptive production decision without making an accuracy claim | Separate project engineering selection from framework calculations |
| `docs/detection_engine_final_assessment.md` | Predated completion of the REAL-RF campaign and listed live RF comparison as future | Adds a release-status addendum describing the completed campaign and remaining ground-truth limitation | Preserve the original Phase 4 decision while incorporating later evidence |

## Preserved Evidence

- Existing validation measurements and result values were not edited.
- Historical planned tests were not removed.
- The frozen OS-CFAR configuration and comparison conclusions were not changed.
- The REAL-RF framework still makes no automatic detector-winner decision.
- Unsupported claims about signal identification, modulation recognition,
  calibrated dBm, detection accuracy, probability of detection, or false-alarm
  probability were not introduced.

## Code-Change Confirmation

No application or validation source code was changed during this
documentation-reconciliation phase.
