# SPECTRA Detection Engine Final Engineering Assessment

## Project Objective

The detector-evolution project evaluated whether an Ordered Statistics CFAR
(OS-CFAR) detector provides a measurable engineering improvement over
SPECTRA's existing adaptive local percentile-based detector.

The objective was evidence-based detector selection, not CFAR adoption.
Production behavior, survey operation, SMART scoring, signal history,
classification, FFT processing, and the user interface remained protected
throughout the comparison.

## Completed Evolution Phases

### Phase 1 — Existing-System Analysis

The production pipeline was traced through local noise estimation, adaptive
thresholding, peak selection, bandwidth estimation, temporal confirmation,
feature history, classification, occupancy, survey measurement, and SMART
decision support. CA-CFAR, GO-CFAR, SO-CFAR, and OS-CFAR were reviewed as
possible alternatives. OS-CFAR was selected as an experimental challenger,
not assumed to be superior.

### Phase 2 — Independent OS-CFAR Candidate

An isolated OS-CFAR module was implemented with configurable reference cells,
guard cells, rank, threshold scale, minimum spacing, peak limit, and bandwidth
drop. It preserved the detector interface but was not imported by the
production application.

### Phase 3 — Shared Evaluation Framework

A validation-only framework generated deterministic complex-IQ scenarios,
processed them through SPECTRA's FFT path, and supplied identical read-only
spectra to both detectors. Automated tests verified scenario construction,
one-to-one frequency matching, metric accounting, and detector execution.

### Phase 4 — Frozen Comparative Experiment

Detector settings, random seed, scenarios, trial count, matching tolerance,
runtime method, and acceptance gates were frozen before execution. The
comparison then evaluated 800 shared spectra and 1,600 detector calls without
retuning either implementation.

## Evidence Produced

The Phase 4 package contains:

- paired raw trial records;
- detector/scenario summary statistics;
- Wilson 95% intervals for applicable rate metrics;
- predeclared decision-gate results;
- frozen protocol metadata;
- detection, false-alarm, and runtime figures;
- an auditable multi-sheet workbook;
- workbook visual-QA previews; and
- engineering interpretation.

Supporting unit tests cover the production adaptive detector, independent
OS-CFAR implementation, shared evaluation framework, and comparison
statistics.

## Comparison Methodology

Both detectors received identical deterministic FFT arrays. Detector execution
order alternated by trial to reduce fixed timing-order bias. Expected and
detected frequencies were matched one-to-one within one FFT bin.

The experiment measured probability of detection, recall, precision, matched
frequency error, returned-count stability, runtime statistics, and SPECTRA
Frame False Alarm Rate.

Frame False Alarm Rate is not classical per-cell CFAR `Pfa`. A frame is
classified as false when at least one returned raw candidate cannot be matched
to an expected carrier. This frame-level definition was selected because it
better represents the opportunity for an unsupported candidate to enter
SPECTRA's downstream processing.

## Comparison Outcome

The frozen OS-CFAR candidate passed five of six predeclared gates:

- single-carrier sensitivity passed;
- weak-carrier performance beside a strong carrier passed;
- closely spaced carrier performance passed;
- non-ideal-scenario robustness passed; and
- runtime compatibility passed.

The primary false-alarm-improvement gate failed. In deterministic noise-only
frames, both detectors produced a Frame False Alarm Rate of `1.000`. The
candidate therefore did not improve the raw-specificity weakness that
motivated the experiment.

The worst p95 runtime was approximately `0.507 ms` for the adaptive detector
and `14.422 ms` for OS-CFAR. OS-CFAR met the `100 ms` requirement but required
approximately 28 times, or about 30 times, the detector computation. Runtime
alone does not reject the candidate; the decisive issue is that the additional
cost produced no measured false-alarm benefit.

## Production Decision

**Retain the adaptive detector as the production detector.**

The adaptive detector remains the only detector used by the SPECTRA
application. The experimental OS-CFAR module is retained as research evidence
and is not integrated into the production pipeline.

This decision is based on the frozen comparison:

1. OS-CFAR did not pass every eligibility gate.
2. It did not improve the Phase 4 Frame False Alarm Rate.
3. It produced equivalent sensitivity in the tested high-SNR scenarios.
4. It incurred substantially greater computational cost.
5. No measured production advantage offsets that cost or integration risk.

## FFT-Edge Coverage Assessment

Current unit tests verify the full-window exclusion policy and confirm that a
peak in an excluded edge bin is not returned. Phase 4 also tests carriers near
the FFT boundary while they remain inside the valid detection region.

The evidence does not sweep every excluded bin or the boundary between
infinite and finite thresholds. It therefore does not completely characterize
the excluded region, transition boundary, and valid region as a continuous
response. This is a documented limitation, not a defect discovered in the
frozen comparison.

## Repository Evidence Assessment

Raw CSV data, protocol metadata, scripts, summary documents, figures, and the
workbook are primary reproducibility evidence.

Tracked `.inspect.ndjson` files are workbook-generation inspection traces.
They are useful QA/debug records but are not required to reproduce detector
measurements. The recommended cleanup is to move them into a designated
workbook-QA archive in a separate reviewed repository-maintenance change.
They were intentionally not moved or deleted during this assessment.

## Lessons Learned

- A theoretically suitable detector is not automatically superior in the
  target system.
- Metric definitions must reflect the application and must not be confused
  with similarly named classical metrics.
- High-SNR synthetic scenarios can saturate detector outputs and conceal
  sensitivity differences.
- Runtime eligibility and engineering desirability are different decisions.
- Negative results are valuable when criteria are frozen and preserved.
- Parameter optimization and final qualification must use separate data to
  avoid post-result tuning bias.
- Raw detector behavior and temporally confirmed application behavior are
  related but distinct validation layers.

## Engineering Recommendation

Retain the existing production architecture and adaptive detector for final
SPECTRA operation. Preserve the Phase 4 negative result as evidence of an
objective selection process.

Treat live RF comparison, classical per-cell false-alarm characterization,
low-SNR sweeps, complete FFT-edge sweeps, OS-CFAR parameter exploration, and
temporal-confirmation studies as future investigations. None is required to
complete or reinterpret Phase 4.

Any future detector candidate should be evaluated under a newly frozen
protocol and must demonstrate a measurable operational benefit before
production integration is reconsidered.
