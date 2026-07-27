# SPECTRA Release Limitations

SPECTRA is an engineering spectrum-observation and decision-support system.
The release is bounded by the following limitations.

## Measurement Limits

- Displayed FFT power is relative and is not calibrated dBm.
- The occupancy metric represents the fraction of spectral bins above an
  adaptive threshold during the application measurement window. It is not
  regulatory channel occupancy.
- Frequency and amplitude observations are affected by receiver tolerance,
  gain, antenna response, propagation, local interference, and RF
  conditions.
- The RTL-SDR is not a laboratory-grade calibrated instrument.

## Detection and Context Limits

- Returned peaks are candidate spectral maxima, not verified emitters.
- Context descriptors summarize measured bandwidth, frequency stability,
  strength, age, and activity history.
- The application does not claim modulation recognition, protocol
  identification, service identification, or transmitter identification.
- The application does not use AI or machine learning.

## Recommendation Limits

- SMART is deterministic heuristic scoring.
- Score separation describes the difference between the winner and
  runner-up scores; it is not statistical confidence.
- Recommendations are decision support based on the configured scoring
  model and observed environment, not authorization for spectrum access.

## Validation Limits

- Synthetic validation characterizes deterministic modeled conditions.
- REAL-RF replay proves repeatability, runtime comparison, and top-result
  agreement under recorded conditions.
- The REAL-RF campaign has no controlled ground-truth annotations and
  therefore does not establish absolute detection probability, false-alarm
  probability, or detector accuracy.
- An antenna-connected quiet capture is not a controlled receiver-noise
  measurement.

## Operational Limits

- Live use requires compatible RTL-SDR hardware and `librtlsdr`.
- Only one process may own the receiver at a time.
- Local RF conditions can change between demonstrations.
