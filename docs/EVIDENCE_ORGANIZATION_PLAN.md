# SPECTRA Evidence Organization Plan

## Objective

The final release should let a reviewer move from requirement to conclusion to
primary evidence without navigating development-only artifacts. This plan does
not delete, rewrite, or regenerate existing evidence.

## Recommended Release Structure

```text
SPECTRA_RELEASE/
├── documentation/
│   ├── README.md
│   ├── REQUIREMENTS_TRACEABILITY_MATRIX.md
│   ├── VALIDATION_EVIDENCE_INDEX.md
│   ├── ENVIRONMENT_CONFIGURATION.md
│   ├── detection_engine_final_assessment.md
│   ├── REAL_RF_VALIDATION_CAMPAIGN_REPORT.md
│   ├── architecture_and_operator_guide.pdf
│   └── limitations.md
├── validation/
│   ├── synthetic/
│   │   ├── campaign_index.md
│   │   ├── primary_summaries/
│   │   ├── selected_tables/
│   │   └── selected_figures/
│   ├── real_rf/
│   │   ├── campaign_report.md
│   │   ├── dataset_manifest.csv
│   │   ├── checksums.sha256
│   │   └── selected_comparison_summaries/
│   ├── detector_selection/
│   │   ├── frozen_protocol.json
│   │   ├── decision_gates.csv
│   │   └── engineering_summary.md
│   └── regression/
│       ├── final_test_log.txt
│       └── environment_freeze_report.md
├── screenshots/
│   ├── main_receiver_view.png
│   ├── live_fft_waterfall.png
│   ├── survey_in_progress.png
│   ├── completed_heatmap.png
│   ├── smart_report.png
│   └── recommended_channel_status.png
├── demo/
│   ├── demo_script.md
│   ├── setup_checklist.md
│   ├── recovery_checklist.md
│   ├── backup_demo.mp4
│   └── backup_results/
└── paper/
    ├── final_engineering_report.pdf
    ├── final_presentation.pdf
    └── editable_sources/
```

The source tree and pinned `requirements.txt` should be distributed through the
tagged repository release rather than duplicated inside every evidence folder.

## Folder Responsibilities

### `documentation/`

Contains reviewer-facing explanations and traceability:

- project overview and operating boundaries;
- final requirements matrix;
- evidence index;
- environment/install record;
- architecture and operator guidance;
- production detector decision;
- REAL-RF campaign interpretation; and
- explicit limitations and future-work boundaries.

Historical phase reports may be included in a labeled `historical/` subfolder
if the submission requires full design history. Retired GUI validation guides
must not appear as current operator instructions.

### `validation/`

Contains primary quantitative evidence:

- frozen protocols and configuration identifiers;
- raw summary CSV/JSON necessary to audit conclusions;
- selected plots and tables used in the report;
- detector-selection gates and engineering interpretation;
- REAL-RF dataset metadata and checksums; and
- final regression output.

Large IQ arrays should be archived externally. The release package should
contain their immutable IDs, metadata, byte sizes, checksums, and retrieval
location rather than duplicating them in Git.

Workbook files may be included when requested by the program, but CSV/JSON
should remain the machine-readable source. Workbook `*.inspect.ndjson` traces
belong in an optional QA archive, not the primary evidence folder.

### `screenshots/`

Contains a small, curated set of release-resolution images demonstrating:

- connected receiver state;
- live FFT and waterfall;
- survey progression;
- completed heatmap;
- explainable SMART report; and
- Auto-Tune/recommendation state.

Each screenshot should have a caption, date, configuration, frequency range,
and statement that displayed power is relative.

### `demo/`

Contains operational presentation material:

- exact startup and survey sequence;
- hardware and dependency preflight;
- known-good frequencies and backup range;
- USB/receiver recovery instructions;
- fallback screenshots and report outputs; and
- a short backup screen recording.

The demo should not depend on browsing raw validation folders live.

### `paper/`

Contains the final senior-design report, presentation, and editable source
documents. The report should cite requirement IDs and evidence identifiers from
the traceability documents. It should state:

- SMART is deterministic heuristic scoring;
- classification is context and behavior, not signal identity;
- FFT levels are relative dB, not calibrated dBm; and
- REAL-RF comparison establishes repeatability/runtime/agreement, not absolute
  detector accuracy.

## Existing Evidence Disposition

| Existing material | Recommended disposition | Reason |
| --- | --- | --- |
| `VALIDATION/results/AV-*` | Preserve; copy primary summary, table, and figure into `validation/synthetic/` | Authoritative synthetic evidence |
| `VALIDATION/results/DE-CMP-01_*` | Preserve complete frozen protocol, result, decision gates, and engineering summary | Supports detector production decision |
| `VALIDATION/real_rf/reports/RF-*` | Preserve externally/local archive; package campaign summary and selected per-dataset reports | Nine distinct captures use a common report schema |
| REAL-RF IQ datasets | External checksum-controlled archive | Too large and environment-specific for normal source history |
| `VALIDATION/templates/` | Keep in repository; omit from primary evidence unless procedures are reviewed | Templates are not measurement results |
| `*.inspect.ndjson` | Move later to optional workbook-QA archive or document retention | Debug/inspection records are not needed to interpret measurements |
| Detector evolution phase documents | Place under `documentation/historical/` in release copy | Important design history, not the shortest path to final conclusions |
| Legacy GUI hardware-validation documents | Place under `documentation/historical/legacy_gui_validation/` | Workflow retired; conclusions preserved |
| `signal_log.txt` | Exclude unless deliberately selected and annotated | Runtime log is not controlled release evidence |

## Evidence Selection Rules

1. Preserve original measurements and frozen configurations.
2. Do not edit negative results or failed acceptance criteria.
3. Prefer machine-readable CSV/JSON as the authoritative numerical source.
4. Use workbooks and plots as presentation views of the same source.
5. Give every externally stored IQ dataset a checksum and metadata record.
6. Record the final Git commit, environment, command, and timestamp for the
   release regression log.
7. Never label antenna-connected quiet spectrum as controlled noise.
8. Never infer signal identity, modulation, calibrated power, detection
   accuracy, or false-alarm probability without the required ground truth.

## Remaining Packaging Work

- Capture the final test log from the release commit.
- Produce the REAL-RF external dataset manifest and SHA-256 checksums.
- Select and caption final screenshots.
- Record a short backup demonstration.
- Create final report and presentation PDFs.
- Build a release manifest listing every included artifact and its checksum.

