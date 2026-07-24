# SPECTRA Detection Engine Evolution

## Phase 1 — Existing Pipeline Analysis and CFAR Recommendation

**Status:** Analysis complete; implementation not started  
**Decision state:** OS-CFAR approved as the comparison candidate, not selected
as the production detector  
**Production detector:** Existing adaptive detector remains unchanged

## 1. Purpose

This report evaluates whether Ordered Statistics CFAR (OS-CFAR) is the most
appropriate detector to challenge SPECTRA's existing adaptive detector.
It does not assume that CFAR is superior and does not authorize replacement of
the production detector.

The final detector decision must be based on identical synthetic datasets,
identical RTL-SDR captures, quantitative detection metrics, runtime
measurements, regression testing, and documented engineering tradeoffs.

## 2. Current Detection Chain

```text
RTL-SDR complex IQ samples
        |
        v
Coherent-gain-corrected Hann window
        |
        v
8,192-point FFT and magnitude in relative dB
        |
        v
Local 30th-percentile noise-floor estimate
(250 kHz reflected sliding window)
        |
        v
Per-bin threshold = local estimate + 10 dB
        |
        +------------------------------+
        |                              |
        v                              v
Raw local-maximum detector       Spectral-bin occupancy
(75 kHz spacing, top 3)          (% bins above threshold)
        |
        v
2-of-3 temporal confirmation
(25 kHz frequency tolerance)
        |
        v
Confirmed signal observations
        |
        +--------------+---------------+----------------+
        |              |               |                |
        v              v               v                v
Signal history   Feature store   UI/FFT markers   Signal logging
        |              |
        +-------+------+
                |
                v
Persistence, age, strength, stability, and duty-cycle evidence
                |
                v
Survey feature snapshot and SMART score bonuses
```

### 2.1 FFT preprocessing

`SDR/fft_processing.py` applies a Hann window and divides by the window's
coherent gain. It then computes an FFT, shifts zero frequency to the center,
and converts magnitude to relative dB using `20 log10(|FFT|)`.

This is appropriate for spectral peak detection, but the values are not
calibrated dBm. A CFAR comparison must therefore operate on a clearly defined
linear statistic derived from these FFT values and must not imply absolute
power calibration.

### 2.2 Local noise estimation

`SDR/detection.py` estimates the local noise floor with a sliding percentile
filter:

- window width: 250 kHz;
- selected statistic: 30th percentile;
- edge handling: reflected samples;
- minimum window length: three bins;
- window length forced to an odd number.

At the frozen configuration of 2.048 MS/s and 8,192 samples, nominal FFT-bin
spacing is 250 Hz and the 250 kHz window contains approximately 1,001 bins.

The estimator tracks local baseline changes and is resistant to a limited
number of high-power bins because it selects a low percentile rather than an
average. It is conceptually related to an order-statistic estimator, but it is
not a complete OS-CFAR detector:

- the cell under test is not explicitly excluded;
- no guard cells isolate signal energy from the reference set;
- the selected percentile is fixed rather than calibrated to a desired false
  alarm probability;
- the threshold is a fixed 10 dB offset;
- the entire local window is treated as one population;
- edge behavior uses reflection rather than an explicit reduced or one-sided
  reference policy.

### 2.3 Threshold generation

The per-bin threshold is:

```text
threshold[k] = local_30th_percentile[k] + 10 dB
```

The detector therefore adapts spatially across the FFT. The returned threshold
array is also used by `UTILS/occupancy.py`, so detector evolution can change
both raw peaks and the occupancy value even when no other module changes.

The status panel displays the median of this threshold array. That displayed
number is a summary only and is not the threshold applied to every bin.

### 2.4 Raw peak selection

`scipy.signal.find_peaks` selects local maxima whose heights exceed the
per-bin threshold. It enforces a 75 kHz minimum peak distance. Candidate peaks
are sorted by power, and only the three strongest are returned.

Consequences:

- SPECTRA intentionally reports no more than three raw candidates per frame;
- a strong noise maximum can consume a candidate slot;
- two narrow tones below 75 kHz spacing cannot both be represented;
- false-alarm statistics are censored by the three-candidate cap;
- a future detector must preserve the existing public result format while
  comparison metrics must be measured before any top-three truncation when
  scientifically appropriate.

### 2.5 Temporal confirmation

`SIGNALS/peak_confirmation.py` stores a three-frame history. A current candidate
is confirmed when a peak occurs within 25 kHz in at least two stored frames.

Only current-frame candidates can be returned. Confirmation does not average
frequency, power, or bandwidth, and it does not associate candidates through a
one-to-one track model. The stage reduces isolated candidates, but validation
shows it does not adequately suppress recurrent noise maxima under the tested
conditions.

### 2.6 Bandwidth estimation

For every admitted raw peak, `SDR/detection.py` walks left and right until the
spectrum falls to or below 15 dB beneath the peak. The reported width is the
number of traversed FFT bins multiplied by bin width.

This is a repeatable peak-relative heuristic. It is not regulatory occupied
bandwidth. It is also downstream of raw admission: a broad response rejected by
the detector receives no bandwidth estimate.

### 2.7 Signal classification interaction

Only temporally confirmed peaks reach `UI/signal_panel.py`.

For each confirmed peak:

- history is updated using frequency rounded to 0.1 MHz;
- age and duty cycle are calculated;
- strength is classified from relative FFT power (`W`, `M`, or `S`);
- persistence is classified from observed time (`N`, `A`, `P`, or `L`);
- frequency-allocation context is attached, such as FM Broadcast or Airband;
- bandwidth and frequency stability histories are updated in `FeatureStore`.

The classifier does not identify modulation or transmitter service. Detector
changes can alter classification indirectly by changing which observations
exist, their reported power and bandwidth, and how continuously they recur.

### 2.8 Signal history and feature interaction

Confirmed detections feed:

- first-seen and last-seen timing;
- observation counts;
- recent duty-cycle estimates;
- bandwidth-history stability;
- frequency drift and frequency stability;
- stale-data pruning.

Changing detector false-alarm behavior therefore changes more than the signal
table. Persistent false candidates can accumulate age, persistence, duty-cycle,
and stability evidence.

### 2.9 Occupancy interaction

Occupancy is calculated before temporal confirmation:

```text
occupied bins / total FFT bins * 100
```

A bin is occupied when its power is strictly above the detector threshold for
that bin. The occupancy function itself is exact for this definition, but its
engineering behavior depends directly on the threshold generator.

Any detector comparison must report two separate effects:

1. peak-detection performance;
2. resulting spectral-bin occupancy behavior.

A detector cannot be selected solely on peak Pd/Pfa if it destabilizes survey
occupancy or changes its meaning without justification.

### 2.10 Survey and SMART interaction

After confirmed tuning and a 500 ms settling delay, the survey aggregates at
least three recent measurement frames using medians. Each survey point stores:

- occupancy;
- maximum FFT power;
- average FFT power;
- a nearby feature snapshot, when available.

SMART scoring uses occupancy and relative power for every surveyed frequency.
Confirmed signal features can add persistence, age, and strength bonuses.

Therefore detector evolution can affect SMART through two paths:

- **direct path:** changed threshold changes occupancy;
- **indirect path:** changed confirmed peaks change feature bonuses.

SMART weights and decision logic must remain frozen during detector comparison.

## 3. Existing Quantitative Evidence

| Validation | Existing result | Detector implication |
| --- | --- | --- |
| AV-NF-01 | PASS; worst mean baseline MAE 0.788 dB | Local percentile estimator tracks the tested baselines well. |
| AV-PD-01 | PASS; Pd rises from 0% at -40 dB to 100% at -22 dB input SNR | Existing detector has useful narrow-tone sensitivity. |
| AV-PD-02 | FAIL; 100% of noise-only frames returned three raw candidates | Fixed percentile-plus-margin does not control raw false candidates. |
| AV-PC-01 | FAIL; confirmed false-signal frame probability 37.3% flat and 91.22% uneven | Existing 2-of-3 confirmation does not repair raw specificity sufficiently. |
| AV-PD-03 | PASS; nominal two-tone boundary validated at 75 kHz | Existing spacing behavior is deterministic and must be preserved or explicitly improved. |
| AV-BW-01 | Partial; 5–200 kHz responses repeatable, 400 kHz responses rejected | Local 250 kHz threshold window can be raised by broad signals. |
| AV-OCC-01 | PASS for exact controlled-bin definition | Occupancy arithmetic is correct; threshold behavior remains the controlling uncertainty. |

The strongest reason to evaluate another detector is not fashion or radar
terminology. It is the measured raw and confirmed false-candidate behavior.
The strongest reason not to replace the current detector immediately is its
validated narrow-tone sensitivity, predictable 75 kHz resolution boundary,
local-baseline tracking, and established integration with occupancy and SMART.

## 4. Candidate Detector Comparison

### 4.1 Current adaptive percentile detector

**Reference estimate:** local 30th percentile across one symmetric window.  
**Strengths:** inexpensive vectorized implementation, robust to high-valued
outliers, smooth local baseline tracking, already integrated and validated.  
**Weaknesses:** no guard cells, no design Pfa, recurrent noise maxima pass the
threshold, broad signals contaminate their own reference window, and only the
top three candidates survive.

This method should remain the production baseline until a challenger wins the
complete comparison.

### 4.2 CA-CFAR

**Reference estimate:** average of leading and lagging reference cells,
excluding the cell under test and guard cells.

CA-CFAR is efficient and performs strongly in a homogeneous background.
However, strong signals inside the reference cells raise the mean and can mask
a weaker nearby signal. A background transition can also make the combined
average inappropriate for the cell under test.

For SPECTRA, CA-CFAR is a useful benchmark but is not the preferred challenger:
FM and other live spectra commonly contain multiple signals, shaped receiver
responses, and nonuniform baselines. These are the conditions in which simple
cell averaging is least robust.

### 4.3 GO-CFAR

**Reference estimate:** the greater of the leading-window and lagging-window
means.

GO-CFAR is conservative around a transition because the higher background side
controls the threshold. This can provide better false-alarm regulation when the
cell under test enters a higher-power region. The cost is detection loss and
masking when a strong adjacent signal contaminates one side.

For SPECTRA, GO-CFAR may suppress false alarms near baseline steps but can be
too conservative beside strong stations and broad responses.

### 4.4 SO-CFAR

**Reference estimate:** the smaller of the leading-window and lagging-window
means.

SO-CFAR can preserve sensitivity when one side contains an interfering signal,
because the cleaner side sets the threshold. The same behavior can produce
excessive false alarms at a clutter or noise-floor edge when the lower side is
not representative of the cell under test.

For SPECTRA, SO-CFAR is relevant as a stress-test comparator for weak signals
beside strong signals, but its false-alarm tendency conflicts with the primary
measured weakness of the existing detector.

### 4.5 OS-CFAR

**Reference estimate:** the `k`th ordered value from guard-separated reference
cells.

OS-CFAR can tolerate a configured number of high reference-cell outliers,
depending on rank selection. This makes it a strong candidate for multi-signal
spectra and strong-adjacent-signal cases. Rohling's foundational work describes
its advantage over cell averaging when multiple targets contaminate the
reference window or the window crosses clutter edges.

Tradeoffs are material:

- rank, reference length, guard length, and scaling require calibration;
- performance depends on the assumed background statistic;
- sorting or selection costs more than a mean;
- a poorly chosen rank can lose weak-signal sensitivity;
- many contaminated reference cells can still cause masking;
- broad signals can occupy guard and reference cells;
- “constant false alarm rate” is not established until measured Pfa is shown
  under SPECTRA's actual data model.

OS-CFAR is therefore a scientifically justified challenger, not a guaranteed
upgrade.

## 5. Comparative Engineering Matrix

| Method | Homogeneous noise | Multiple signals / outliers | Baseline edge | Weak beside strong | Runtime | Fit to measured SPECTRA problem |
| --- | --- | --- | --- | --- | --- | --- |
| Current percentile | Good baseline tracking; poor measured candidate Pfa | Resistant to some high bins | Smoothly tracks gradual change | Existing evidence incomplete | Low | Baseline; specificity is inadequate |
| CA-CFAR | Strong | Susceptible to masking | Susceptible to mixed references | Often weak | Low | Benchmark only |
| GO-CFAR | Conservative | Susceptible when one side is contaminated | Strong false-alarm control in its intended edge case | Detection loss likely | Low | Secondary benchmark |
| SO-CFAR | Sensitive | Useful when one side is clean | Can over-alarm | Potentially strong | Low | Conflicts with current false-alarm weakness |
| OS-CFAR | Rank-dependent | Robust to a bounded number of outliers | Often more robust than CA; still rank-dependent | Strong candidate | Moderate | Best challenger for objective testing |

These are expected behaviors, not SPECTRA results. They must not be presented
as measured conclusions until Phase 3 and Phase 4 are complete.

## 6. Phase 1 Recommendation

### Recommendation

Implement **OS-CFAR as an independent experimental detector** in Phase 2 and
compare it with the unchanged adaptive detector.

### Why OS-CFAR is the correct challenger

1. SPECTRA's measured limitation is false-candidate specificity, not a lack of
   narrow-tone sensitivity.
2. The live use case contains multiple spectral signals and nonuniform
   baselines, making robustness to contaminated reference cells important.
3. OS-CFAR provides explicit guard cells, reference cells, rank selection, and
   threshold scaling—parameters that can be frozen and tested.
4. It directly supports controlled Pd/Pfa tradeoff measurement.
5. It is sufficiently different from the current low-percentile estimator to
   test whether a calibrated ordered statistic improves specificity without
   sacrificing useful sensitivity.

### What is not recommended

- Do not replace the current detector now.
- Do not call the current percentile detector “CFAR.”
- Do not claim that OS-CFAR will provide constant Pfa before calibration and
  measurement.
- Do not integrate multiple selectable production detectors into the GUI.
- Do not tune SMART weights to compensate for detector differences.
- Do not change temporal confirmation during detector comparison.
- Do not use only radar-style exponential simulations; include complex-IQ and
  FFT-domain conditions representative of SPECTRA.

## 7. Required Decision Gates

OS-CFAR should replace the current detector only if it demonstrates, on
identical inputs:

1. materially lower noise-only raw and confirmed false-alarm rates;
2. equal or acceptably bounded loss in Pd across the tested SNR range;
3. improved weak-carrier detection beside strong carriers;
4. no unacceptable regression in two-tone resolution;
5. documented behavior for broad and modulated responses;
6. stable occupancy values with an explicitly preserved metric definition;
7. acceptable runtime at the application's live frame rate;
8. repeatable results on saved RTL-SDR captures;
9. no regression in survey, SMART, history, classification, heatmap, FFT,
   waterfall, or shutdown behavior.

If OS-CFAR does not meet these gates, the current detector should remain in
production and its measured limitations should be documented.

## 8. Phase 2 Boundary

The next phase may create an independent OS-CFAR module and unit tests. It must
not modify `SDR/detection.py`, redirect `main.py`, change occupancy behavior, or
remove the current detector.

Recommended experimental interface:

```text
detect_peaks(power_db, freqs_mhz) -> (results, threshold)
```

Preserving this interface will allow identical downstream evaluation without
premature production integration.

## 9. Technical References

- Hermann Rohling, “Radar CFAR Thresholding in Clutter and Multiple Target
  Situations,” *IEEE Transactions on Aerospace and Electronic Systems*,
  AES-19(4), 608–621, 1983.
  [DOI: 10.1109/TAES.1983.309350](https://doi.org/10.1109/TAES.1983.309350)
- Hermann Rohling, “Ordered statistic CFAR technique: an overview,”
  *International Radar Symposium*, 2011.
  [TU Hamburg research record](https://tore.tuhh.de/entities/publication/998eb722-ae06-47d1-bb18-93f64697da5f)
- G. A. Zimmerman and E. T. Olsen, “An analysis of I/O efficient
  order-statistic-based techniques for noise power estimation in the HRMS sky
  survey's operational system,” 1992.
  [NASA Technical Reports Server](https://ntrs.nasa.gov/citations/19930009737)

## 10. Phase 1 Decision

**Proceed to independent OS-CFAR implementation and controlled comparison.**

This is approval to build and test a challenger only. The existing adaptive
detector remains SPECTRA's sole production detector until quantitative
synthetic and hardware evidence supports a final engineering decision.
