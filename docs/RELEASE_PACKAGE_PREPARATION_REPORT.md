# SPECTRA Release Package Preparation Report

## 1. Created Structure

The release-candidate package was created at:

```text
SPECTRA_RELEASE/
├── source/
├── documentation/
├── validation/
├── screenshots/
├── demo/
└── checksums/
```

Top-level release metadata identifies SPECTRA 1.0.0-rc.1, verified source
commit `b52f77e`, the frozen environment, validated hardware, production
detector, and known limitations.

## 2. Included Artifacts

### Source

- immutable Git source reference;
- README;
- pinned requirements; and
- environment configuration.

The full Python tree is not duplicated. Git commit `b52f77e` is the
authoritative source.

### Documentation

- requirements traceability matrix;
- validation evidence index;
- environment configuration;
- release-candidate verification;
- macOS startup-fix verification;
- detector final assessment;
- REAL-RF campaign report;
- REAL-RF evaluation contract;
- architecture reference; and
- consolidated limitations statement.

### Validation

- synthetic experiment index;
- each synthetic experiment README and summary JSON;
- frozen detector-comparison summary and result JSON;
- REAL-RF campaign summary;
- detector selection assessment; and
- release test summary.

### Presentation

- final screenshot checklist;
- demonstration script;
- setup checklist; and
- failure-recovery checklist.

### Archival

- archive-checksum instructions and expected checksum filenames.

## 3. Excluded Artifacts

The package deliberately excludes:

- REAL-RF IQ arrays;
- raw synthetic trial data;
- debug and validation logs;
- `.inspect.ndjson` files;
- generated workbook previews;
- workbook-generation scripts;
- Python caches;
- virtual environments; and
- duplicate source code.

Large IQ datasets remain in `VALIDATION/real_rf/datasets/` and require a
separate archive and checksum.

## 4. Verification Results

Packaging verification checks:

- source and algorithm files were not modified;
- validation measurements and generated results were not modified;
- only package/documentation additions were created;
- `git diff --check` passed; and
- the full automated suite passed with 283 tests.

## 5. Remaining Release Tasks

1. Create or designate the institution-formatted final engineering report.
2. Capture the six final screenshots listed in
   `SPECTRA_RELEASE/screenshots/README.md`.
3. Replace the pending packaging commit in `RELEASE_METADATA.md` after commit.
4. Create the final release and validation archives.
5. Create a separate REAL-RF IQ dataset archive.
6. Generate and verify SHA-256 records for all finalized archives.
7. Apply the final release tag after review.
