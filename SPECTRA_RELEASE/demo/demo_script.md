# SPECTRA Demonstration Script

## Demonstration Goal

Demonstrate a complete receive-only workflow:

```text
Observe
  -> tune
  -> survey
  -> evaluate
  -> explain
  -> Auto-Tune
```

Target duration: approximately 6–8 minutes.

## 1. Introduction — 30 Seconds

### Presenter Action

Show the RTL-SDR Blog V3, antenna, and the SPECTRA opening screen.

### Suggested Explanation

> SPECTRA is a receive-only adaptive RF survey and decision-support system.
> It uses RTL-SDR hardware for live acquisition, performs FFT-based spectrum
> processing, detects spectral peak candidates, automates frequency surveys,
> and produces an explainable recommendation.

Clarify immediately:

- SPECTRA does not transmit.
- SPECTRA does not use AI or machine learning.
- Context labels are not transmitter, modulation, or service identification.
- Displayed power is relative and is not calibrated dBm.

## 2. Startup Demonstration — 45 Seconds

### Presenter Action

From the verified virtual environment, launch:

```bash
python main.py
```

Point to:

- `RECEIVER CONNECTED`;
- the confirmed center frequency;
- the live FFT;
- the waterfall;
- peak-candidate markers; and
- the receiver status panel.

### Suggested Explanation

> The RTL-SDR supplies complex IQ samples. SPECTRA applies windowed FFT
> processing to produce the live spectrum. The waterfall shows how relative
> spectral power changes over time. Markers identify peak candidates above
> the adaptive threshold; they are not claims of transmitter identity.

## 3. Manual Tuning Demonstration — 45 Seconds

### Presenter Action

1. Enter the rehearsed active frequency.
2. Select **Tune**.
3. Show the updated center-frequency display and plot range.

### Suggested Explanation

> The displayed receiver center is not updated from the request alone.
> SPECTRA updates its confirmed frequency state only after the SDR worker
> reports successful hardware tuning.

Allow the FFT and waterfall to stabilize before moving on.

## 4. Automated Survey Demonstration — 90 Seconds

### Presenter Action

Configure:

| Setting | Value |
|---|---|
| Start frequency | 88 MHz |
| Stop frequency | 92 MHz |
| Step size | 1 MHz |
| Decision mode | SMART Recommendation |

Select **Start Survey** and point to the survey-progress state.

### Suggested Explanation

> The survey sequence is event driven. For each point, SPECTRA requests a
> tune, waits for hardware confirmation, applies a defined settling interval,
> collects the measurement, stores the result, and then advances.

```text
Tune request
  -> hardware confirmation
  -> RF settling
  -> measurement
  -> aggregation
  -> next point
```

> After the final measurement, candidate frequencies are ranked using the
> selected decision mode.

Do not promise a particular winning frequency; the local RF environment may
change.

## 5. SMART Recommendation Demonstration — 90 Seconds

### Presenter Action

Open **View detailed results** and point to:

- SMART recommendation;
- runner-up;
- score separation;
- score breakdown;
- why-selected explanation; and
- supporting diagnostics.

### Suggested Explanation

> SMART is a deterministic, explainable weighted engineering heuristic. It
> evaluates the measured candidate data using spectral-bin occupancy,
> relative power, and available signal-history factors. The selected
> frequency has the highest resulting SMART score.

> Score separation is the difference between the winner and runner-up. It is
> not statistical confidence.

Mention that diagnostics support interpretation but do not identify a
modulation or service.

## 6. Auto-Tune Demonstration — 45 Seconds

### Presenter Action

1. Close the report.
2. Manually tune away from the recommendation.
3. Show `OFF RECOMMENDED CHANNEL`.
4. Select **Auto-Tune Best**.
5. Show the confirmed center frequency and `ON RECOMMENDED CHANNEL`.

### Suggested Explanation

> Auto-Tune uses the existing survey recommendation and follows the same
> hardware-confirmed tuning path. The status card distinguishes a
> recommendation from the receiver’s confirmed current state.

## 7. Validation Summary — 60 Seconds

### Presenter Action

Show the validation evidence index and campaign report.

### Suggested Explanation

> The release passed 283 automated tests. Synthetic experiments characterize
> FFT behavior, adaptive thresholding, peak detection, temporal confirmation,
> occupancy, bandwidth estimation, and detector behavior.

> Nine REAL-RF datasets were captured and replayed immutably. Both the
> Adaptive Detector and OS-CFAR received the same recorded IQ and shared FFT
> preprocessing. The comparison demonstrated repeatability, top-result
> agreement, and a substantial runtime difference.

> The Adaptive Detector remains the production detector because it provided
> comparable capped peak-selection behavior while executing approximately
> 30–32 times faster in the recorded comparison. OS-CFAR remains an
> independent research baseline.

Do not describe the REAL-RF comparison as a ground-truth accuracy test.

## 8. Limitations Statement — 30 Seconds

### Suggested Explanation

> SPECTRA reports relative spectral power, not calibrated dBm. Spectral-bin
> occupancy is an application metric, not regulatory channel occupancy. The
> system does not identify modulation, protocol, service, or transmitter.
> The current REAL-RF campaign has no controlled ground truth, so it does not
> establish absolute probability of detection, false-alarm probability, or
> detector accuracy. Live results also depend on the receiver, antenna,
> gain, interference, and local RF environment.

## Closing

> SPECTRA demonstrates an integrated, validated receive-only SDR system that
> converts live RF observations into an explainable engineering
> recommendation while preserving clear measurement and validation limits.

Close SPECTRA normally and, when useful, point out the terminal message:

```text
SDR CLOSED
```
