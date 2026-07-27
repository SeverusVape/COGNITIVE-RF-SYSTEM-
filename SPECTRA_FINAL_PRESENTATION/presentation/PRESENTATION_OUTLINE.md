# SPECTRA Final Presentation Outline

## Target Format

- Length: 12–15 minutes, excluding questions
- Core slides: 13
- Live demonstration: 3–5 minutes within the presentation
- Style: engineering review, evidence first, restrained claims

## Slide 1 — Title

**SPECTRA**

Spectrum Processing, Evaluation, Classification, Tracking, Ranking, and
Analysis

Subtitle: Adaptive SDR Spectrum Analyzer

Include:

- student and advisor names;
- course or senior-design program;
- institution; and
- presentation date.

## Slide 2 — Engineering Problem

Explain the need to:

- observe live RF conditions;
- summarize spectral activity across a frequency range;
- rank candidate frequencies consistently; and
- explain why a recommendation was selected.

Avoid presenting SPECTRA as an autonomous spectrum-access system.

## Slide 3 — Project Requirements

Summarize:

- RTL-SDR acquisition;
- FFT and waterfall;
- adaptive peak detection;
- signal history and contextual features;
- automated survey;
- deterministic SMART recommendation;
- confirmed Auto-Tune; and
- reproducible validation.

Evidence: requirements traceability matrix.

## Slide 4 — System Architecture

Show:

```text
RTL-SDR
  -> SDR worker
  -> FFT processing
  -> Adaptive Detector
  -> temporal confirmation/history/features
  -> survey aggregation
  -> SMART scoring
  -> explanation and Auto-Tune
```

Separate the production path from the standalone validation path.

## Slide 5 — DSP and Live Visualization

Show:

- windowed FFT;
- frequency axis;
- adaptive threshold;
- peak candidates; and
- waterfall history.

Recommended asset:

`SPECTRA_RELEASE/screenshots/fft_and_waterfall.png`

State that displayed power is relative.

## Slide 6 — Automated Survey Sequencing

Explain:

```text
Tune request
  -> hardware confirmation
  -> settling interval
  -> measurement
  -> aggregation
  -> next survey point
```

Recommended asset:

`SPECTRA_RELEASE/screenshots/survey_running.png`

## Slide 7 — SMART Decision Support

Explain:

- candidate measurement inputs;
- weighted deterministic scoring;
- ranking;
- runner-up comparison;
- score separation; and
- why-selected output.

Recommended asset:

`SPECTRA_RELEASE/screenshots/smart_report_top.png`

Clarify that score separation is not statistical confidence.

## Slide 8 — Signal Context and Diagnostics

Describe:

- persistence and age;
- frequency stability;
- bandwidth stability;
- duty-cycle history; and
- evidence maturity.

Recommended asset:

`SPECTRA_RELEASE/screenshots/smart_report_diagnostics.png`

Do not claim modulation or service identification.

## Slide 9 — Detector Engineering Decision

Compare:

- Adaptive Detector as production detector;
- OS-CFAR as independent research baseline;
- shared replay inputs; and
- observed runtime difference.

State the decision conservatively:

> The Adaptive Detector retained comparable capped peak-selection behavior in
> the recorded comparison while executing approximately 30–32 times faster.

Do not claim absolute detector superiority or accuracy.

## Slide 10 — Validation Architecture

Show:

```text
Synthetic scenarios
  -> deterministic DSP/detector characterization

Recorded IQ
  -> immutable replay
  -> shared FFT preprocessing
  -> Adaptive + OS-CFAR
  -> comparison reports
```

Mention:

- 283 automated tests;
- completed synthetic validation; and
- nine REAL-RF datasets.

## Slide 11 — Validation Results and Limits

Confirmed:

- deterministic replay;
- repeatable outputs;
- detector agreement metrics;
- runtime differences; and
- complete release workflow.

Not proven:

- calibrated RF power;
- absolute probability of detection;
- absolute false-alarm probability;
- signal identity; or
- detector accuracy without controlled ground truth.

## Slide 12 — Live Demonstration

Demonstrate:

1. receiver connection;
2. live FFT and waterfall;
3. manual confirmed tuning;
4. short survey;
5. SMART report; and
6. Auto-Tune to the recommendation.

Use the package in `SPECTRA_RELEASE/demo/`.

## Slide 13 — Conclusions and Future Work

Conclusions:

- integrated receive-only SDR instrument;
- event-driven survey measurement;
- explainable deterministic recommendation;
- validated release candidate; and
- clean separation of production and research detectors.

Realistic future work:

- controlled-source ground-truth RF testing;
- calibrated relative-amplitude experiments;
- per-cell false-alarm characterization; and
- expanded real-interference scenarios.

End with questions.

## Optional Backup Slides

- Detailed score components
- Synthetic validation matrix
- REAL-RF dataset inventory
- Dependency and environment freeze
- Detector limitations
- Failure-recovery workflow
