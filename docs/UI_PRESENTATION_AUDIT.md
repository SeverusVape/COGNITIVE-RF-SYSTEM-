# SPECTRA UI Presentation Audit

## 1. Executive Summary

SPECTRA's current interface is suitable for a senior-design demonstration. It presents the application as an engineering instrument rather than a development utility: survey controls are grouped on the left, live RF information dominates the center, and receiver and signal state are summarized on the right. The dark navy theme, consistent card treatment, restrained accent colors, and structured survey report create a strong and coherent visual identity.

A professor can understand the principal workflow within approximately ten seconds:

1. select a survey range and decision mode;
2. observe the live spectrum and waterfall;
3. run the survey;
4. review the recommended frequency; and
5. tune the receiver to the recommendation.

The remaining presentation concerns are small but important. The window title does not yet use the SPECTRA product name, several compact signal-table labels can be misread as verified signal identification, and the FFT/status displays do not explicitly say that power is relative rather than calibrated dBm. Small 10–11 px text is readable on a desktop display but should be checked on the actual presentation projector.

No major layout redesign is recommended before release. The safest final polish is limited to branding, conservative terminology, capitalization consistency, and a rehearsed screenshot/demo configuration.

## 2. UI Architecture Review

### 2.1 Main window structure

The main window is constructed in `main.py` as a three-zone horizontal layout:

```text
┌────────────────────┬──────────────────────────────────────┬────────────────────┐
│ Survey controls    │ Receiver tuning                     │ Signal candidates  │
│                    ├──────────────────────────────────────┤ Signal legend      │
│ Range and mode     │ Real-time spectrum                  │                    │
│ Start / clear      ├──────────────────────────────────────┤ System status      │
│                    │ Signal waterfall                    │                    │
│ Survey status      ├──────────────────────────────────────┤ Survey history     │
│ Detailed results   │ Survey occupancy history            │                    │
└────────────────────┴──────────────────────────────────────┴────────────────────┘
```

The center workspace receives the largest layout share, which is correct for an RF analysis application. The side panels remain visible without competing with the plots. The top tuning card provides a clear separation between manual receiver control and the automated survey workflow.

### 2.2 Panel organization

**Left panel — survey operation**

- Survey range, step size, and decision mode appear in expected operating order.
- Primary and secondary actions are visually distinct.
- The survey card communicates no-data, in-progress, recommendation, on-recommendation, and off-recommendation states.
- Detailed results are exposed as a separate, clearly clickable action only when results exist.

**Center panel — measurement workspace**

- The confirmed receiver center is the highest-priority value.
- The FFT, waterfall, and survey occupancy history form a logical top-to-bottom sequence: current spectrum, recent time history, and survey-level history.
- The recommended-frequency line gives a direct visual relationship between the decision output and surveyed spectrum.

**Right panel — operational context**

- The signal table provides compact candidate information.
- The receiver card exposes connection, center frequency, sample rate, displayed range, candidate count, threshold, and occupancy.
- Survey history preserves useful context without displacing the live plots.

**Detailed survey report**

- The report separates recommendation, decision comparison, score breakdown, diagnostics, observed behavior, measured occupancy, and diagnostic coverage.
- Winner/runner-up score separation is explicitly distinguished from statistical certainty.
- The large multi-card layout is much more reviewable than the earlier long text-only report.
- At the minimum supported popup size, some scrolling may still be necessary. This is acceptable for release if the demonstration uses the verified presentation resolution.

### 2.3 Information hierarchy

The strongest immediately visible information is:

- confirmed receiver center frequency;
- RTL-SDR connection state;
- live FFT and waterfall;
- detected peak markers;
- current survey configuration and progress;
- recommended frequency after survey completion;
- current relationship between the receiver and the recommendation;
- recent survey occupancy history.

Information intentionally hidden behind **View detailed results** includes:

- winner and runner-up scores;
- decision margin and confidence category;
- score-component breakdown;
- signal diagnostic maturity and observations;
- decision rationale;
- per-frequency occupancy ranking;
- diagnostic coverage for surveyed frequencies.

This hierarchy is appropriate. The main window answers “what is happening now?” while the report answers “why was this frequency recommended?”

### 2.4 Operator workflow and demo usability

The normal workflow is visually discoverable and requires no menu navigation. Inputs are grouped, buttons are adjacent to the state they affect, and feedback appears in persistent status cards. Tooltips and accessible names provide additional support without adding visual clutter.

The principal demonstration risk is not workflow ambiguity but density. At the 1180 × 760 minimum size, right-panel text, graph labels, and the detailed report can become small. The application should therefore be demonstrated at the already proven 1400 × 900 size or larger, preferably using display mirroring tested before the presentation.

### 2.5 Ten-second comprehension assessment

**Assessment: Yes, with a brief verbal orientation.**

Within ten seconds, a reviewer can recognize a connected SDR, live spectrum display, automated survey controls, and recommendation output. The terms `Type`, `Str`, and abbreviated band/context codes are not self-explanatory without the legend. SMART scoring and its limitations are appropriately hidden from the first view, but should be explained when the detailed report is opened.

## 3. Visual Quality Assessment

| Area | Score | Assessment |
|---|---:|---|
| Overall visual consistency | 9.0/10 | Cards, borders, spacing, button states, and table treatments are consistent across the main window and report. |
| Professional appearance | 8.5/10 | The interface resembles a focused engineering instrument. Remaining branding and terminology inconsistencies prevent a fully finished release impression. |
| Layout balance | 8.5/10 | The center plots correctly dominate while both side panels remain useful. The layout becomes dense near the minimum window size. |
| Typography | 8.0/10 | Clear weight hierarchy separates titles, values, and secondary text. Several 10–11 px labels may be too small on a projector. |
| Color consistency | 9.5/10 | The centralized navy/cyan/teal/purple palette is disciplined and semantic status colors are used consistently. |
| Panel organization | 9.0/10 | Controls, measurements, and historical information are grouped according to operator tasks. |
| Graph readability | 8.0/10 | Plot titles, axes, grid, markers, and color scale are clear. Peak labels can overlap in dense spectra, and “Power (dB)” does not explicitly identify a relative scale. |
| Status visibility | 9.0/10 | Receiver and survey state are persistent, color-coded, and easy to find. Temporary tuning feedback returns to a meaningful persistent state. |
| Demo readiness | 8.5/10 | The core demonstration path is strong and stable. Final branding, conservative labels, and projector rehearsal remain. |

### Visual strengths

- The main center frequency is immediately recognizable.
- Cyan actions, green success, yellow warning, pink error, and purple recommendation indicators have distinct meanings.
- Graph grid opacity is restrained and does not overpower traces.
- The waterfall and heatmap provide visual impact without adding separate windows.
- The detailed report uses tables and cards rather than an unstructured diagnostic dump.

### Visual constraints

- The right signal table uses highly abbreviated headers and codes.
- A dense set of nearby peaks can produce overlapping FFT labels.
- The report's information density remains high even in its improved layout.
- Minimum-size operation is functional but not ideal for projection.

## 4. Terminology Review

No visible AI or machine-learning claim was found in the reviewed UI. The interface also avoids claiming calibrated RF power or statistical detection accuracy. The main terminology risk is that contextual heuristics may appear to be verified signal identification.

| Current wording | Concern | Recommended wording | Reason |
|---|---|---|---|
| Adaptive SDR Spectrum Analyzer (window title) | Omits final product branding. | SPECTRA — Adaptive SDR Spectrum Analyzer | Aligns the running application with release documentation. |
| Type | Band/context codes can be mistaken for identified signal type. | Context | Makes the heuristic nature of the label clearer. |
| Str | Very compact and unexplained without the legend. | Strength | Improves immediate comprehension if column width permits. |
| Freq | Acceptable but abbreviated. | Frequency | Prefer for a presentation if the right panel can accommodate it safely. |
| SIGNAL LEGEND | Does not explain that `BC`, `AIRBND`, and related values are contextual labels. | SIGNAL CONTEXT LEGEND | Reduces the risk of an identification claim. |
| Signals | May imply confirmed emitters or identified services. | Confirmed peaks or Peak candidates | Matches the actual detector output more closely. |
| Power (dB) | May be interpreted as calibrated absolute power. | Relative power (dB) | Explicitly communicates the measurement limitation. |
| Threshold | Does not state that the displayed value uses the relative FFT scale. | Detection threshold (relative dB) | Safer engineering interpretation; may require compact formatting. |
| Occupancy | Can be interpreted as regulatory channel occupancy. | Spectral-bin occupancy | Matches the implemented metric. Use where space permits, especially in reports. |
| Most occupied frequencies | Technically understandable but potentially broader than the metric. | Highest measured spectral-bin occupancy | More precise, although longer. |
| Smart Recommendation | Capitalization differs from the all-caps report label. | SMART Recommendation | Matches the documented deterministic scoring mode and SPECTRA terminology. |
| Auto-tune best | Slightly informal and inconsistent capitalization. | Auto-Tune Best | Improves label consistency without changing behavior. |
| RF occupancy, recommendation, and decision-score summary | “RF occupancy” can imply a broader channel-use measure. | Spectral-bin occupancy, recommendation, and decision-score summary | Accurately scopes the implemented measurement. |

`SMART Recommendation` is appropriate provided the presentation describes it as deterministic heuristic scoring. `Observed Signal Behavior` and `Signal Diagnostics` are also acceptable because the report already states that these are observational and do not identify modulation or service.

The band labels produced by the contextual classifier should be described verbally as frequency-range context, not transmitter identification. Strength and persistence codes are relative, observation-based descriptors.

## 5. Recommended Improvements

### 5.1 High value / low risk

| Priority | Improvement | File | Risk | Expected Benefit |
|---|---|---|---|---|
| 1 | Change the window title to `SPECTRA — Adaptive SDR Spectrum Analyzer`. | `main.py` | Low | Makes product identity visible in every live demo and screenshot. |
| 2 | Replace the signal-table `Type` label with `Context`; expand other headers only if the current panel width supports them. | `UI/signal_panel.py` | Low | Prevents contextual classification from appearing to be verified signal identification. |
| 3 | Rename the signal legend to clarify that the abbreviations are context/status descriptors. | `UI/signal_panel.py` | Low | Improves interpretation without changing the table or classifier. |
| 4 | Label FFT amplitude as relative power. | `UI/fft_panel.py` | Low | Prevents accidental calibrated-dBm interpretation during review. |
| 5 | Use `Confirmed peaks` or `Peak candidates` instead of `Signals` in receiver status. | `UI/status_panel.py` | Low | Aligns UI wording with what the detector actually returns. |
| 6 | Standardize `SMART` and `Auto-Tune` capitalization in visible controls and reports. | `UI/survey_controls.py`, `UI/tuning_panel.py`, `SURVEY/survey_manager.py` | Low | Produces a more deliberate, publication-ready vocabulary. |
| 7 | Use “spectral-bin occupancy” in the detailed report and other locations with sufficient space. | `UI/survey_popup.py`, `SURVEY/survey_manager.py` | Low | Makes the occupancy claim technically defensible. |
| 8 | Capture final screenshots at one verified large resolution with a clean application-only frame. | Release evidence; no application change | Very low | Produces consistent report and presentation artifacts. |

Items 1–5 are the only UI text changes considered necessary before release. They are presentational corrections rather than feature work. Each should still receive a normal smoke test because label length can affect a narrow panel.

### 5.2 Medium risk

| Priority | Improvement | File | Risk | Expected Benefit |
|---|---|---|---|---|
| 1 | Increase selected graph, table, and secondary-text sizes after testing on the actual projector. | `UI/theme.py`, `UI/graph_style.py`, report HTML in `SURVEY/survey_manager.py` | Medium | Improves audience readability, but may introduce clipping or force scrolling. |
| 2 | Slightly widen the right information panel if expanded table labels clip. | `main.py`, `UI/signal_panel.py` | Medium | Supports safer terminology while preserving legibility. |
| 3 | Refine report sizing only if the presentation computer still requires vertical scrolling at full screen. | `UI/survey_popup.py`, `UI/theme.py`, `SURVEY/survey_manager.py` | Medium | Makes the full decision explanation visible at once, but the existing layout is already acceptable. |
| 4 | Reduce FFT peak-label collisions through presentation-only decluttering rules. | `UI/fft_panel.py` | Medium | Improves dense-spectrum readability, but changes plotting behavior and should not be attempted without focused regression testing. |

### 5.3 Improvements not recommended for this release

- Migrating to another UI framework.
- Rebuilding the three-panel layout.
- Replacing the report renderer or introducing a dashboard framework.
- Adding graphs, animations, tabs, detachable panes, or new controls.
- Adding a production detector selector.
- Changing FFT smoothing, waterfall timing, tune transitions, or zoom behavior for cosmetic reasons.
- Adding an AI-themed visual treatment or terminology.
- Adding permanent validation controls to the main application.

These changes have little final-presentation value relative to their regression risk.

## 6. Demo Flow

### FINAL DEMO UI FLOW

1. **Prepare the hardware**
   - Connect the RTL-SDR Blog V3 and antenna.
   - Warm the receiver before the presentation.
   - Use a pre-screened indoor antenna position and a known reliable FM range.

2. **Start SPECTRA**
   - Launch at the verified display resolution.
   - Confirm that the right card shows `RECEIVER CONNECTED`.
   - Give a ten-second orientation: survey controls left, live RF center, status/context right.

3. **Explain the live measurement**
   - Point to the confirmed receiver center.
   - Identify the relative-power FFT, frequency axis, peak candidates, and waterfall time history.
   - State explicitly that amplitude is relative, not calibrated dBm.

4. **Demonstrate manual tuning**
   - Tune to a rehearsed local FM frequency.
   - Allow the FFT and waterfall to stabilize.
   - Avoid plot zooming during the formal demo because the known zoom/retune display edge case is not presentation-critical.

5. **Configure a short survey**
   - Use a small, rehearsed range such as 88–92 MHz with a 1 MHz step.
   - Select `SMART Recommendation`.
   - Briefly explain that SMART is deterministic, explainable heuristic scoring.

6. **Run the survey**
   - Start the survey and point out the persistent progress card.
   - Explain that each measurement follows confirmed hardware tuning and a defined settling interval.
   - Do not narrate every frequency transition.

7. **Review completion**
   - Highlight the recommended frequency in the survey card.
   - Show the recommendation line in the occupancy history.
   - Point out current receiver/recommendation state.

8. **Open detailed results**
   - Explain the recommended and runner-up frequencies, component scores, decision margin, and confidence-as-score-separation.
   - Briefly identify occupancy ranking and diagnostic evidence.
   - State that contextual labels are not modulation recognition or transmitter identification.

9. **Demonstrate Auto-Tune**
   - Close the report and press `Auto-Tune Best`.
   - Show the temporary confirmation followed by the persistent on-recommended-channel state.
   - Confirm that the receiver center and plots agree.

10. **Present validation evidence**
    - Move to prepared report slides rather than opening repository folders or console output.
    - Explain immutable IQ replay, identical detector input, deterministic comparison, and the adaptive detector's production selection.

### Demo risks and mitigations

| Risk | Mitigation |
|---|---|
| Weak or changing local RF environment | Rehearse two candidate FM ranges and keep validated screenshots available. |
| RTL-SDR connection failure | Connect before presenting, verify USB access, and keep a recorded screen sequence as backup. |
| Projector makes small text unreadable | Test the exact display mode; use 1400 × 900 or larger and avoid OS display scaling changes immediately before the demo. |
| Dense or overlapping peak labels | Select a rehearsed frequency range with a readable spectrum; explain only the strongest visible candidates. |
| Long survey delays audience flow | Use five to seven points and rehearse the expected duration. |
| Low decision margin changes the recommendation between runs | Explain that RF conditions vary and use the score margin as evidence of decision separation, not certainty. |
| Accidental invalid input | Preload the survey values and avoid typing unnecessary values during the presentation. |
| Popup requires scrolling | Use the proven full-screen report resolution and begin with the recommendation/decision section visible. |

### What should not be shown

- Raw terminal logs unless requested during questions.
- Experimental OS-CFAR as a selectable production detector.
- A very broad or long-running survey.
- Manual graph zoom followed by retuning.
- The antenna-connected 300 MHz capture as proof of a controlled noise floor.
- Any claim of signal identity, modulation recognition, calibrated power, probability of detection, or false-alarm accuracy without ground truth.

## 7. Screenshot Plan

| Screenshot | Required content | Why it is valuable |
|---|---|---|
| 1. Main SPECTRA interface | Full application, receiver connected, stable known signal, all three information zones visible | Establishes the complete instrument and product identity. |
| 2. Live spectrum and waterfall | Clear peaks, readable frequency labels, corresponding waterfall traces, receiver status visible | Demonstrates live SDR acquisition, FFT processing, peak detection, and temporal visualization. |
| 3. Survey in progress | Progress card, active center frequency, responsive plots | Demonstrates automated, nonblocking survey operation and clear operator feedback. |
| 4. Survey complete | Recommended frequency, occupancy history, recommendation marker, survey history | Shows the transition from RF measurement to decision support. |
| 5. SMART analysis report | Recommendation, runner-up, margin, confidence, score breakdown, and diagnostic cards | Demonstrates explainability and engineering transparency. |
| 6. Receiver on recommended channel | Confirmed center matches the recommendation and the persistent success state is visible | Closes the control loop from survey result to confirmed hardware tuning. |

Capture all screenshots at the same resolution and theme. Crop only enough to remove desktop distractions; retain the application title bar where branding or window identity is important. Avoid transient tuning frames, overlapping labels, personal file paths, console windows, and unrelated desktop notifications.

## 8. Final Recommendations

### Necessary before release

1. Apply the SPECTRA product name to the application window title.
2. Replace ambiguous identification-like terminology (`Type`, `Signals`) with contextual/detection terminology.
3. Mark FFT power as relative.
4. Standardize SMART and Auto-Tune capitalization.
5. Rehearse and capture the final demo at the actual presentation resolution.

### Optional

- Expand selected abbreviations if the right panel remains readable.
- Increase small fonts only after projector testing proves it necessary.
- Refine report fit only if the presentation display forces inconvenient scrolling.
- Improve peak-label collision behavior only after final release if it can be isolated and tested safely.

### Do not attempt before release

- Major layout or framework changes.
- New visualizations or controls.
- Plot-processing or tune-transition changes motivated only by appearance.
- New signal-identification language or unvalidated intelligence claims.
- Reintroduction of validation controls into the production UI.

The current interface is already presentation-ready in structure and visual identity. A short terminology-and-branding pass, followed by a controlled projector rehearsal, offers the highest engineering value with the lowest release risk.
