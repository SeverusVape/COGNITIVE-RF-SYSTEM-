# REAL-RF Detector Validation Campaign Report

## 1. Executive Summary

This campaign evaluated the SPECTRA Adaptive and OS-CFAR detector engines on nine antenna-connected, real-RF recordings spanning FM broadcast, NOAA weather radio, the 2-meter amateur band, civil airband, and a nominally quiet 300 MHz region. The purpose was to demonstrate a reproducible comparison workflow and characterize detector runtime and frequency agreement under representative received-spectrum conditions.

Each capture was stored as an immutable complex-IQ dataset. Both detectors were then evaluated by deterministic replay of the same recorded frames through shared FFT preprocessing. This method removes live-RF timing differences from the detector comparison and makes every reported result reproducible from the saved dataset.

The campaign contains 1,600 captured frames. Every dataset was replayed twice, producing 3,200 frame evaluations per detector. Both detectors returned identical results on repeated execution for every dataset.

The reported detections are capped top-N results: the Adaptive detector and the evaluated OS-CFAR configuration each return no more than three selected peaks per frame. A count of three therefore does **not** establish that exactly three physical signals were present, and the selected peaks are not ground-truth annotations. The campaign supports runtime, repeatability, and top-three agreement observations; it does not establish probability of detection, false-alarm probability, calibrated measurement accuracy, or detector superiority.

## 2. Validation Architecture

```text
Recorded IQ dataset
        ↓
Immutable replay
        ↓
Shared FFT preprocessing
        ↓
   ┌──────────────────┐
   │                  │
Adaptive Detector   OS-CFAR Detector
   │                  │
   └────────┬─────────┘
            ↓
     Comparison engine
            ↓
     Generated reports
```

The architecture provides the following controls:

- Both detectors receive the same complex-IQ frames and frequency axis.
- Shared FFT preprocessing prevents detector-specific input preparation from biasing the comparison.
- Immutable datasets support deterministic replay and later audit.
- Two complete repetitions verify repeated-execution consistency.
- Detector evaluation is isolated from the production receiver pipeline.
- The production application is not switched to OS-CFAR.
- The comparison engine reports observations and does not automatically select a winning detector.

All captures used a 2.048 MS/s sample rate and an 8,192-point FFT, corresponding to a 250 Hz frequency-bin spacing. Pairwise detections were matched using the framework's one-bin frequency tolerance.

## 3. Dataset Summary

| Test | Frequency | Signal Type | Frames | Capture Duration | Dataset ID |
|---|---:|---|---:|---:|---|
| FM 100.3 | 100.300 MHz | FM broadcast | 100 | 0.402 s | `RF-20260727T154801Z-3bbdf9aa` |
| FM 95.5 | 95.500 MHz | FM broadcast | 100 | 0.402 s | `RF-20260727T155621Z-41e39428` |
| FM 107.1 | 107.100 MHz | FM broadcast | 100 | 0.403 s | `RF-20260727T160255Z-6aac686e` |
| NOAA 162.550 | 162.550 MHz | NOAA weather radio | 100 | 0.401 s | `RF-20260727T160730Z-340871c9` |
| NOAA 162.475 | 162.475 MHz | NOAA weather radio | 100 | 0.401 s | `RF-20260727T161211Z-37309860` |
| 2 m 146.520 | 146.520 MHz | 2-meter amateur band | 200 | 0.802 s | `RF-20260727T161651Z-6c62a346` |
| 2 m 145.500 | 145.500 MHz | 2-meter amateur band | 200 | 0.802 s | `RF-20260727T162129Z-bf3dfb63` |
| Airband 125.000 | 125.000 MHz | Civil airband | 200 | 0.801 s | `RF-20260727T162524Z-c870b554` |
| Quiet 300 | 300.000 MHz | Antenna-connected background spectrum | 500 | 2.000 s | `RF-20260727T162907Z-e95a8e90` |

Capture duration is the recorded acquisition interval for the saved IQ frames, not the total elapsed time of the validation session or replay.

## 4. Detector Runtime Comparison

The following values are the saved mean detector execution times. The runtime ratio is calculated as OS-CFAR mean runtime divided by Adaptive mean runtime.

| Dataset | Adaptive Mean Runtime | OS-CFAR Mean Runtime | Runtime Ratio |
|---|---:|---:|---:|
| FM 100.3 | 0.428 ms | 12.976 ms | 30.32× |
| FM 95.5 | 0.440 ms | 13.126 ms | 29.82× |
| FM 107.1 | 0.434 ms | 13.040 ms | 30.07× |
| NOAA 162.550 | 0.415 ms | 13.196 ms | 31.83× |
| NOAA 162.475 | 0.411 ms | 13.285 ms | 32.32× |
| 2 m 146.520 | 0.415 ms | 13.285 ms | 32.01× |
| 2 m 145.500 | 0.416 ms | 13.322 ms | 32.01× |
| Airband 125.000 | 0.422 ms | 13.451 ms | 31.85× |
| Quiet 300 | 0.418 ms | 13.466 ms | 32.19× |

OS-CFAR was approximately 30–32 times slower than the Adaptive detector in this campaign. These measurements characterize the tested computer, implementation, and frozen detector configurations; they are not universal execution-time guarantees.

## 5. Detection Agreement Analysis

Detection count is not the principal comparison metric because both evaluated detector paths return their strongest three peaks. Each detector consequently reported a mean of 3.000 returned detections per frame for every dataset. This is a cap-saturated output condition, not evidence of identical raw candidate populations or exactly three RF emitters.

The table instead reports pairwise agreement among the returned top-three peaks. Values are means per evaluated frame across both deterministic replay repetitions.

| Dataset | Mean Matched Detections | Adaptive-Only | OS-CFAR-Only |
|---|---:|---:|---:|
| FM 100.3 | 1.870 | 1.130 | 1.130 |
| FM 95.5 | 2.040 | 0.960 | 0.960 |
| FM 107.1 | 2.110 | 0.890 | 0.890 |
| NOAA 162.550 | 2.910 | 0.090 | 0.090 |
| NOAA 162.475 | 2.960 | 0.040 | 0.040 |
| 2 m 146.520 | 2.975 | 0.025 | 0.025 |
| 2 m 145.500 | 2.915 | 0.085 | 0.085 |
| Airband 125.000 | 2.775 | 0.225 | 0.225 |
| Quiet 300 | 2.950 | 0.050 | 0.050 |

The equal Adaptive-only and OS-CFAR-only means follow from comparing two lists that each contain three returned peaks. They do not imply symmetric threshold behavior before top-N selection. Agreement describes how often the two detectors selected peaks at matching frequency bins; it does not determine which unmatched selection was physically correct.

## 6. Signal Environment Analysis

### 6.1 FM Broadcast

The FM datasets represent strong, continuously occupied broadcast environments with wide spectral structure relative to narrowband communication channels. Top-three agreement ranged from 1.870 to 2.110 matches per frame, the lowest agreement group in this campaign. This indicates that the detectors often shared major spectral selections but differed in which additional local maxima entered their capped output lists.

Because there are no annotated transmitter frequencies for every visible spectral component, these differences cannot be labeled misses or false detections. Wideband modulation, adjacent stations, multipath, receiver response, and local spectral maxima can all affect which three peaks are selected.

### 6.2 NOAA Weather Radio

NOAA weather-radio captures represent narrowband, normally continuous transmissions. The two NOAA datasets produced 2.910 and 2.960 matched detections per frame. Under these recordings, the detectors therefore selected nearly identical top-three peak frequencies.

This high agreement supports consistency between the two selection paths in these particular narrowband spectral environments. It does not establish absolute frequency accuracy or detection probability because the recordings lack synchronized ground-truth annotations.

### 6.3 2-Meter Amateur Band

The 2-meter datasets represent communication-band monitoring at 146.520 MHz and 145.500 MHz. Agreement was high: 2.975 and 2.915 matched detections per frame. The captures show that the two detectors can produce closely aligned top-three selections in these received environments.

Amateur-band activity can be intermittent, but the saved reports do not label transmitter on/off intervals. The campaign therefore cannot distinguish detections of actual communications from stable receiver features, local interference, or background maxima.

### 6.4 Civil Airband

The 125.000 MHz recording represents an airband environment in which voice transmissions are typically intermittent. The mean agreement was 2.775 matched detections per frame, with 0.225 detector-specific selections on each side.

The capture is suitable for comparing deterministic detector output on the same received data, but it is not sufficient to measure burst-detection probability. Such a claim would require time-aligned ground truth identifying when a transmission was present.

### 6.5 Quiet 300 MHz

The 300 MHz dataset is an antenna-connected observation of a comparatively quiet region, not a terminated-input or controlled-noise measurement. Both detectors returned three peaks because their output lists were filled from available raw candidates. Their top-three selections agreed strongly, with 2.950 matches per frame.

A selection near the exact 300 MHz center appeared persistently in both detector outputs. In a zero-IF RTL-SDR receiver, a center-frequency/DC artifact is a plausible explanation. Other selected frequencies, including approximately 299.7805 MHz and 300.6405 MHz in an example frame, may represent transient noise maxima, local interference, receiver artifacts, or real received energy. Without an antenna-disconnected or terminated reference and independently known signal truth, they cannot be classified reliably.

Accordingly, the quiet-spectrum result must not be presented as a false-alarm test. It demonstrates how the capped detector outputs behave in a low-activity antenna-connected capture.

## 7. Validation Findings

### Confirmed by the campaign

- Immutable IQ capture and loading support repeatable offline evaluation.
- Both detectors receive identical saved IQ frames and shared FFT preprocessing.
- Both detectors produced deterministic peak lists and thresholds across two complete repetitions of all nine datasets.
- Detector execution time differs substantially under the evaluated implementations and configurations.
- Pairwise frequency matching quantifies agreement among the returned top-three detections.
- The framework preserves detector isolation and does not switch the production receiver to OS-CFAR.

### Not proven by the campaign

- Probability of detection.
- Probability or rate of false alarm.
- Absolute frequency, power, or bandwidth accuracy.
- Calibrated received power in dBm.
- Correct physical identity of returned peaks.
- Detector superiority or a production-detector winner.

## 8. Limitations

- The recordings contain no synchronized ground-truth annotations for signal presence, frequency, bandwidth, or power.
- RTL-SDR frequency error, oscillator drift, gain behavior, dynamic range, DC offset, image response, and front-end overload can affect observed spectra.
- Reported FFT power is relative dB, not calibrated dBm.
- The antenna, indoor placement, local propagation, interference, and multipath are part of the measurement environment.
- The quiet 300 MHz capture used a connected antenna and is not equivalent to a shielded or terminated receiver-noise test.
- Both detector outputs are capped at three selected peaks, hiding raw candidate counts above the cap.
- Top-three matching evaluates frequency-selection agreement, not correctness.
- Capture intervals are short and do not fully characterize intermittent channel activity.
- Runtime values are dependent on the tested software build and host computer.
- The evaluated conclusions apply to the frozen detector configurations used to generate the saved reports.

## 9. Future Validation Improvements

Future work should remain in the validation layer and preserve the production detector implementations during evidence collection.

1. **Record raw candidate counts before top-N truncation.** This would expose threshold-stage selectivity independently of the final presentation cap.
2. **Add cap-hit percentage.** Report the fraction of frames in which raw candidates meet or exceed the configured output limit.
3. **Add frequency, power, and bandwidth difference metrics.** For matched peaks, report distributions rather than frequency agreement alone.
4. **Add temporal persistence analysis.** Measure how consistently each selected frequency remains present across consecutive frames.
5. **Add controlled-source validation.** Use a known RF source or available lab generator to establish signal presence and expected frequency.
6. **Add controlled noise-floor validation.** Use an antenna-disconnected or properly terminated input, where practical, to characterize receiver artifacts and false selections under a known condition.

## 10. Final Engineering Conclusion

The REAL-RF validation framework successfully demonstrates repeatable detector comparison using identical recorded IQ data. Across nine datasets and two replay repetitions, both detector engines produced deterministic results from shared FFT inputs. The campaign quantified a substantial runtime difference—OS-CFAR required approximately 30–32 times the Adaptive detector execution time—and measured the frequency agreement of their returned top-three peaks across several received-signal environments.

The results constitute reproducible engineering evidence for detector behavior under the recorded conditions. They do not establish detection accuracy, probability of detection, false-alarm rate, or detector superiority because the captures lack controlled ground truth and both detector outputs are top-N limited. The framework nevertheless provides a sound foundation for future controlled detector evaluation, particularly if raw candidate counts, cap saturation, matched-peak differences, temporal persistence, controlled sources, and controlled noise measurements are added at the validation layer.

For final SPECTRA production, the Adaptive Detector is retained because the
recorded campaign showed comparable capped top-three peak-selection behavior
while OS-CFAR required approximately 30–32 times greater mean detector runtime.
OS-CFAR remains an independent research and validation baseline. This
production decision does not convert the uncontrolled REAL-RF observations
into an accuracy, false-alarm, or detector-superiority claim.
