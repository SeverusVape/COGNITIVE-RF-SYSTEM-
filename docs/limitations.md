# SPECTRA Engineering Limitations

## Measurement

- FFT power values are relative dB, not calibrated dBm.
- Spectral-bin occupancy is the fraction of bins above the adaptive threshold
  during a measurement window. It is not regulatory channel occupancy.
- Frequency and amplitude observations depend on receiver tolerance, gain,
  antenna response, propagation, local interference, and environmental RF.
- The RTL-SDR is not a laboratory-grade calibrated instrument.

## Detection and Context

- Returned peaks are candidate spectral maxima, not verified emitters.
- Context labels and behavior descriptors summarize observed frequency,
  bandwidth, strength, age, persistence, and activity.
- SPECTRA does not claim transmitter identification, service identification,
  modulation recognition, or protocol recognition.
- Candidate lists are capped at three selected peaks in the current production
  configuration.

## Recommendation

- SMART is deterministic weighted heuristic scoring, not AI or machine
  learning.
- Score separation is the winner/runner-up score difference, not statistical
  confidence.
- Recommendations support engineering observation and do not authorize
  spectrum access or transmission.

## Validation

- Synthetic results apply only to their frozen modeled conditions.
- REAL-RF replay supports repeatability, runtime comparison, and capped
  top-result agreement under recorded conditions.
- Without controlled ground truth, the REAL-RF campaign does not establish
  absolute detection accuracy, probability of detection, or false-alarm
  probability.
- An antenna-connected quiet capture is not a controlled receiver-noise test.
- REAL-RF IQ datasets are stored outside Git and require independent
  checksum-controlled archival storage.

## Operations

- Live use requires compatible RTL-SDR hardware, `librtlsdr`, USB access, and
  exclusive receiver ownership.
- Demonstration results may change as the RF environment changes.
- Final qualification was performed on Apple Silicon macOS; other platforms
  are supported by design but were not equivalently hardware-qualified.
