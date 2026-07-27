# SPECTRA Demo Package Preparation Report

## 1. Files Created or Updated

Updated:

- `SPECTRA_RELEASE/demo/demo_script.md`
- `SPECTRA_RELEASE/demo/setup_checklist.md`
- `SPECTRA_RELEASE/demo/failure_recovery_checklist.md`

Created:

- `SPECTRA_RELEASE/demo/SCREENSHOT_CAPTURE_PLAN.md`
- `docs/DEMO_PACKAGE_PREPARATION_REPORT.md`

No Python source, UI implementation, algorithm, validation measurement, or
generated validation result was changed.

## 2. Demonstration Flow Summary

The final script presents one complete engineering workflow:

1. Introduce SPECTRA as a receive-only adaptive RF survey and
   decision-support system.
2. Launch the verified application and identify the live receiver state.
3. Explain FFT, waterfall, peak candidates, and status information.
4. Demonstrate hardware-confirmed manual tuning.
5. Run the short 88–92 MHz automated survey.
6. Explain tune-confirm-settle-measure sequencing.
7. Present the deterministic SMART recommendation, runner-up, score
   separation, score components, and supporting diagnostics.
8. Demonstrate Auto-Tune and `ON RECOMMENDED CHANNEL`.
9. Summarize automated, synthetic, and nine-dataset REAL-RF validation.
10. State measurement, identification, validation, and environmental
    limitations.

The script includes presenter actions, technically conservative suggested
language, and a 6–8 minute target duration.

## 3. Screenshot Plan Summary

The plan defines six presentation artifacts:

1. Full main interface
2. Live FFT and waterfall
3. Survey in progress
4. Completed survey
5. SMART report
6. Auto-Tune result

Each entry defines its engineering purpose, required visible information,
and content that must be excluded. A common capture standard covers release
revision, resolution, privacy, notifications, transient states, and
terminology.

## 4. Recovery Preparation

The recovery checklist covers:

- receiver detection and device ownership;
- weak or changed RF conditions;
- changed survey recommendations;
- incomplete surveys;
- unclear peak markers;
- display problems; and
- unexpected application closure.

Recovery is time bounded. After one concise retry, the presenter should move
to verified screenshots and release evidence rather than debug live.

## 5. Remaining Manual Actions

1. Select the final presentation resolution and scaling.
2. Confirm a primary and backup active frequency at the presentation site.
3. Rehearse the complete script with a timer.
4. Capture and review all six screenshots.
5. Copy screenshots, reports, and presentation files to backup media.
6. Rehearse one receiver-disconnection recovery.
7. Rehearse the limitations statement and avoid unsupported claims.

## 6. Verification

- Documentation-only scope confirmed.
- No source or validation-result changes.
- `git diff --check` passed.
