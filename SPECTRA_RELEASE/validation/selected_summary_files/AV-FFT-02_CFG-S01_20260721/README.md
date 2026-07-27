# AV-FFT-02 — Hann Window and Off-Bin Leakage Validation

This evidence package was generated entirely from deterministic synthetic IQ.
No RTL-SDR hardware was opened or required.

## Frozen method

- Existing application paths: `compute_fft()` and `compute_windowed_fft()`
- Sample rate: 2.048 MSPS
- FFT length: 8192 samples
- Bin spacing: 250 Hz
- Tone locations: -512 kHz, 0 Hz, and +512 kHz from center
- Fractional-bin offsets: 0.00, 0.25, and 0.50 bins
- Repetitions: 20 randomized deterministic phases per condition
- Window responses: rectangular and coherent-gain-corrected Hann
- Leakage: integrated energy outside ±2 bins around the detected peak,
  relative to total spectral energy

## Acceptance criteria declared before execution

1. Absolute bin-centered peak error is no more than 0.01 dB for both windows.
2. Hann improves leakage by at least 10 dB at 0.25- and 0.50-bin offsets
   at every tested frequency location.

## Result

PASS. Maximum centered peak error was 0.000 dB at reported precision. The
minimum observed off-bin Hann leakage improvement was 22.155 dB.

The result validates numerical window behavior only. It does not validate the
RTL-SDR analog chain, calibrated power, arbitrary modulated signals, or a
universal sidelobe specification. Hann reduces leakage with the expected
tradeoff of a wider main lobe.
