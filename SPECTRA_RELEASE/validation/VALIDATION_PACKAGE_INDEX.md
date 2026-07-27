# SPECTRA Validation Package Index

This folder contains curated summary evidence only.

## Included Evidence

| Artifact | Scope |
|---|---|
| `SYNTHETIC_VALIDATION_SUMMARY.md` | Index of completed synthetic DSP and detector experiments |
| `REAL_RF_VALIDATION_CAMPAIGN_REPORT.md` | Nine-dataset capture/replay campaign |
| `detection_engine_final_assessment.md` | Adaptive production-detector decision |
| `TEST_RESULTS_SUMMARY.md` | Final automated and hardware verification summary |
| `selected_summary_files/AV-*` | Experiment README and summary JSON only |
| `selected_summary_files/DE-CMP-*` | Frozen detector-comparison result and engineering summary |

## External REAL-RF Evidence

The nine IQ datasets remain at:

```text
VALIDATION/real_rf/datasets/
```

Dataset identifiers:

- `RF-20260727T154801Z-3bbdf9aa`
- `RF-20260727T155621Z-41e39428`
- `RF-20260727T160255Z-6aac686e`
- `RF-20260727T160730Z-340871c9`
- `RF-20260727T161211Z-37309860`
- `RF-20260727T161651Z-6c62a346`
- `RF-20260727T162129Z-bf3dfb63`
- `RF-20260727T162524Z-c870b554`
- `RF-20260727T162907Z-e95a8e90`

Archive these datasets separately and record the archive SHA-256 value in
`../checksums/`. Do not place IQ arrays inside the main release archive.

## Deliberate Exclusions

- raw trial CSV files;
- workbooks and previews;
- `.inspect.ndjson` files;
- workbook-generation scripts;
- debug logs;
- temporary captures;
- Python caches; and
- large IQ arrays.

These exclusions reduce package size and prevent debug artifacts from being
mistaken for primary engineering conclusions.
