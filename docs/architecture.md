# SPECTRA Architecture

## System Purpose

SPECTRA is a receive-only adaptive SDR spectrum analyzer and explainable RF
survey system. It observes spectral activity, records relative measurements,
ranks surveyed frequencies, and presents deterministic engineering
recommendations. It does not transmit, identify emitters, recognize
modulation, or provide calibrated RF power.

## Production Data Path

```text
RTL-SDR hardware
  -> SDRManager device ownership and configuration
  -> SDRWorker threaded acquisition and confirmed tuning
  -> Hann-window FFT and shifted frequency axis
  -> Adaptive Detector peak candidates
  -> temporal confirmation and signal history
  -> contextual features and behavior descriptors
  -> survey measurement aggregation
  -> deterministic SMART scoring
  -> explainable recommendation
  -> hardware-confirmed Auto-Tune
```

## Subsystem Boundaries

| Subsystem | Responsibility |
| --- | --- |
| `SDR/` | Receiver access, worker-thread acquisition, FFT processing, production Adaptive Detector, standalone OS-CFAR baseline |
| `SIGNALS/` | Candidate confirmation, history, feature extraction, contextual classification, observed behavior |
| `SURVEY/` | Event-driven survey sequencing, aggregation, candidate ranking, report data |
| `UI/` | Qt panels, graphs, status presentation, and the survey analysis popup |
| `UTILS/` | Frozen configuration, frequency axes, occupancy, measurement aggregation, and platform library discovery |
| `LOGGING/` | Optional local signal-observation logging |
| `VALIDATION/` | Synthetic experiments and isolated REAL-RF capture/replay comparison |
| `tests/` | Deterministic unit, integration, regression, and isolation tests |

## Survey Sequence

```text
request canonical survey frequency
  -> SDR tune command
  -> tune_succeeded confirmation
  -> configured settling interval
  -> aggregate valid measurement frames
  -> store result
  -> advance or complete
```

Measurement begins only after confirmed receiver tuning. The survey controller
owns the sequence; the SDR layer reports hardware events.

## Detector Selection

The Adaptive Detector in `SDR/detection.py` is the production engine. OS-CFAR
in `SDR/os_cfar.py` remains independently callable for research and validation
and is not connected to the production UI, survey, or SMART path.

## Validation Architecture

```text
Recorded complex-IQ dataset
  -> immutable deterministic replay
  -> shared production FFT preprocessing
  -> Adaptive Detector and OS-CFAR
  -> normalized pairwise comparison
  -> reviewer-facing reports
```

Both detectors receive identical replayed spectra. The REAL-RF campaign
supports repeatability, runtime, and capped top-result agreement observations;
it does not create ground truth or prove absolute detection accuracy.

See the [requirements traceability matrix](REQUIREMENTS_TRACEABILITY_MATRIX.md)
for implementation and evidence locations.
