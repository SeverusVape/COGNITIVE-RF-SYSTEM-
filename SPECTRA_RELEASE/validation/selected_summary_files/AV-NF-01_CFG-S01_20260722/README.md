# AV-NF-01 — Adaptive Noise-Floor Validation

Synthetic-only validation of the existing local percentile estimator. Three
known spectral baselines (flat, curved, and stepped) were tested with 100
deterministic randomized trials each. Every trial included 1.5 dB Gaussian
spectral variation and seven narrow peaks.

The evaluation excludes filter-edge bins and, for the stepped case, bins inside
one half-window of the abrupt transition. This prevents claiming that a local
windowed estimator can reproduce a discontinuity inside its own support.

## Result

PASS. Worst condition mean MAE: 0.788 dB. Worst condition 95th-percentile
trial MAE: 0.819 dB. Worst condition 95th-percentile peak-induced mean change:
0.006 dB. The configured 10 dB threshold margin was preserved numerically.

This evidence validates synthetic baseline tracking only. It does not measure
RTL-SDR noise figure, antenna/environmental noise, calibrated dBm, or analog
receiver performance.
