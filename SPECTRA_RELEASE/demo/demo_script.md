# SPECTRA Final Demonstration Script

## Target Duration

Approximately 6–8 minutes.

## Sequence

1. Introduce SPECTRA as an adaptive SDR spectrum analyzer and explainable RF
   survey system.
2. Show the connected RTL-SDR and antenna arrangement.
3. Launch SPECTRA and point out `RECEIVER CONNECTED`.
4. Identify the live FFT, waterfall, peak candidates, receiver status, and
   survey controls.
5. Tune a rehearsed active frequency and show confirmed center-frequency and
   plot-range updates.
6. Configure the rehearsed survey range and start the survey.
7. Explain event-driven tune-confirm-settle-measure sequencing while progress
   advances.
8. Open the completed SMART report.
9. Explain the recommendation, runner-up, score separation, score breakdown,
   and supporting diagnostics.
10. Tune away from the recommendation and use **Auto-Tune Best**.
11. Show `ON RECOMMENDED CHANNEL`.
12. Close SPECTRA and note the clean receiver shutdown.

## Required Language

- Say “relative power,” not calibrated dBm.
- Say “spectral-bin occupancy,” not regulatory channel occupancy.
- Say “peak candidates” or “context descriptors,” not identified signals.
- Describe SMART as deterministic heuristic scoring.
- Describe score separation as non-statistical.

## Evidence Transition

After the live application, show:

- the requirements traceability matrix;
- the synthetic validation summary;
- the REAL-RF campaign report;
- the Adaptive/OS-CFAR runtime comparison; and
- the release-candidate verification report.
