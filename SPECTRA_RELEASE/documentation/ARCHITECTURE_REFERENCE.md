# SPECTRA Architecture Reference

The authoritative architecture description is maintained in:

1. `source/README.md`, section **Architecture**;
2. `documentation/REQUIREMENTS_TRACEABILITY_MATRIX.md`; and
3. the source tree at verified commit `b52f77e`.

The operational data path is:

```text
RTL-SDR
  -> SDR worker and manager
  -> windowed FFT processing
  -> adaptive peak-candidate detector
  -> temporal confirmation and signal history
  -> feature extraction and contextual descriptors
  -> survey aggregation
  -> deterministic SMART scoring
  -> explainable recommendation
  -> confirmed Auto-Tune
```

The standalone validation path is:

```text
Recorded IQ dataset
  -> immutable replay
  -> shared FFT preprocessing
  -> Adaptive Detector + OS-CFAR
  -> comparison reports
```

OS-CFAR is not connected to production detection, survey, SMART scoring, or
the operator UI.
