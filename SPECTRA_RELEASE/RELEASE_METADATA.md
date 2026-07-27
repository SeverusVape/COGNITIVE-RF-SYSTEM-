# SPECTRA Release Metadata

| Field | Value |
|---|---|
| Project | SPECTRA |
| Expanded name | Spectrum Processing, Evaluation, Classification, Tracking, Ranking, and Analysis |
| Subtitle | Adaptive SDR Spectrum Analyzer |
| Release version | 1.0.0-rc.1 |
| Verified source commit | `b52f77e` |
| Packaging commit | Pending creation |
| Verification date | July 27, 2026 |
| Operating system | macOS 26.5.2, build 25F84 |
| Python | CPython 3.10.11 |
| Receiver | RTL-SDR Blog V3, RTL2832U/R860, 1 PPM TCXO |
| Production detector | Adaptive Detector |
| Research baseline | Standalone OS-CFAR |
| Automated verification | 283 tests passed |

## Validated Capabilities

- Live RTL-SDR acquisition
- Windowed FFT spectrum processing
- Waterfall and survey heatmap visualization
- Adaptive peak-candidate detection
- Signal history and contextual descriptors
- Event-driven automated frequency surveys
- Deterministic SMART recommendation scoring
- Explainable recommendation reports
- Confirmed receiver Auto-Tune
- Synthetic DSP and detector validation
- Immutable REAL-RF capture/replay detector comparison
- Clean receiver shutdown and relaunch

## Known Limitations

- FFT power is relative and is not calibrated dBm.
- Spectral-bin occupancy is not regulatory channel occupancy.
- Context labels are not ground-truth signal, service, protocol, or
  modulation identification.
- REAL-RF replay establishes repeatability, agreement, and runtime behavior;
  it does not establish absolute detection accuracy.
- Performance depends on the RTL-SDR, gain, antenna, local interference, and
  RF environment.
- Only one process may control the RTL-SDR at a time.

See `documentation/LIMITATIONS.md` for the release limitation statement.
