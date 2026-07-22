# AV-PD-01 — Synthetic Peak-Detector Performance

## Result

PASS under frozen configuration `CFG-S01`.

- 900 deterministic tone-plus-noise trials
- 100 trials at each of nine input SNR levels from -40 to -20 dB
- Detection probability: 0% at -40 dB, 57% at -28 dB, 93% at
  -26 dB, 99% at -24 dB, and 100% at -22 and -20 dB
- Detection-probability rise from -40 to -22 dB: 100 percentage points
- Maximum median matched-frequency error across detected conditions: 87.7 Hz
- FFT-bin spacing and frequency-error acceptance limit: 250 Hz

## Method

Each trial generated circular complex Gaussian noise with expected unit power
and one complex tone at a deterministic randomized off-bin frequency and phase.
Input SNR was defined before windowing as tone power divided by expected complex
noise power. Samples passed through the existing coherent-gain-corrected Hann
FFT and existing adaptive peak detector. A trial counted as a successful
detection only when one returned peak was within one FFT bin of the injected
tone.

## Engineering interpretation

The existing detector exhibits the expected probability-of-detection transition
as input SNR increases. FFT processing gain permits reliable narrow-tone
detection below 0 dB time-domain input SNR. Matched frequency estimates remain
bin limited and meet the declared criterion.

The detector returned its configured maximum of three peak candidates in these
noise-containing spectra, including at low SNR. This experiment does not treat
those unrelated candidates as false alarms. Noise-only false-alarm behavior is
reserved for `AV-PD-02` and must be evaluated before making a detector
specificity claim.

## Scope limitation

This is synthetic algorithm validation. It does not establish RTL-SDR hardware
sensitivity, calibrated received power, false-alarm rate, or performance for
modulated and bandwidth-limited signals.
