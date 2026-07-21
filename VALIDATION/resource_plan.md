# Validation Resource Plan

## Freeze status

The software environment and processing baseline are recorded. No measurements
have been collected. Physical RF-chain details remain pending operator
confirmation and must be resolved before assigning the first measurement
session ID.

## Experiment-to-resource mapping

| Experiment | Minimum resources | Preferred resources | Current readiness | Fallback |
| --- | --- | --- | --- | --- |
| AV-FFT / AV-NF / AV-PD / AV-BW / AV-OCC | Project Python environment; deterministic synthetic IQ generator | None beyond available computer | Ready after synthetic conventions and seeds are frozen | None needed |
| HV-FREQ-02 cold-start drift | RTL-SDR; antenna; one stable narrow reference | Controlled reference carrier | Blocked by unconfirmed antenna and reference | Use a documented narrow broadcast/beacon; do not use FM as primary drift reference |
| HV-FREQ-01 frequency accuracy | Warm RTL-SDR; antenna; at least three credible references | Controlled source or independent reference | Blocked by unconfirmed references | Reduce claim to indicative system error and state reference limitations |
| HV-AMP-01 relative linearity | RTL-SDR at fixed gain; stable source; known attenuators | Calibrated step attenuator | Blocked by unconfirmed source and attenuation | Omit linearity claim |
| HV-AMP-02 amplitude repeatability | RTL-SDR at fixed gain; stable received signal; fixed geometry | Controlled source | Pending antenna/source details | Use stable live signal and report propagation limitation |
| HV-NF-01 noise/threshold | RTL-SDR; fixed gain; recorded antenna setup | 50-ohm termination plus quiet and active spans | Pending termination and antenna details | Compare quiet and active antenna spans only |
| HV-OCC-01 live occupancy | RTL-SDR; fixed settings; quiet and active spans | Recorded RF geometry | Pending span selection | Use 88-92 and 115-121 MHz comparative spans after prescreening |
| HV-OCC-02 controlled ON/OFF | RTL-SDR; legal controlled source | Signal generator plus attenuation | Blocked by unconfirmed source | Omit controlled ON/OFF claim |
| HV-SMART-01 / 02 | RTL-SDR; antenna; frozen survey settings | Stable placement and RF environment | Nearly ready; physical setup must be recorded | Existing 88-92 and 115-121 MHz ranges are suitable |
| HV-SEQ-01 | RTL-SDR; application; frozen survey settings | Same setup as SMART tests | Nearly ready; physical setup must be recorded | None needed |

## Configuration IDs

- `CFG-BASE`: immutable processing and software baseline.
- `CFG-S01`: synthetic algorithm series; seed, noise model, and SNR definition
  must be frozen before execution.
- `CFG-H01`: current auto-gain system-demonstration baseline.
- `CFG-H02`: reserve for fixed-gain hardware measurements. Create it only after
  selecting and recording the fixed gain, antenna, cable, location, and source.

Auto gain is appropriate for preserving the current application baseline but
is not valid for a relative-amplitude linearity claim. Amplitude, noise-floor,
and controlled occupancy comparisons must use a separately recorded fixed-gain
configuration.

## Pre-measurement gates

1. Confirm antenna, cable/adapters, receiver serial or label, and general test
   location.
2. Confirm whether a 50-ohm termination, known attenuators, and controlled RF
   source are available.
3. Identify exact reference carriers and record the basis for their expected
   frequency.
4. Freeze `CFG-S01` random-seed policy, noise model, and SNR definition.
5. Create `CFG-H02` if any fixed-gain experiment will be run.
6. Enter session start time only when data collection actually begins.
7. Photograph or otherwise record the physical setup without including a
   personal address.

## Recommended order after the gates are satisfied

1. Synthetic FFT frequency/window response.
2. Synthetic noise-floor and threshold tracking.
3. Synthetic probability of detection, false alarms, and two-tone resolution.
4. Synthetic bandwidth and occupancy checks.
5. Cold-start RTL-SDR drift (performed before the normal warm-up).
6. Warm frequency-accuracy observations.
7. Fixed-gain amplitude repeatability; linearity only if known attenuation is
   available.
8. Noise-floor/threshold and quiet-versus-active occupancy comparisons.
9. SMART repeatability on 88-92 MHz and 115-121 MHz.
10. Event-driven survey sequence verification.

## First experiment release condition

The first executable experiment is `AV-FFT-01`, synthetic FFT frequency
accuracy. It may begin only after the synthetic generator convention and random
seed policy are written into `CFG-S01`. This test requires no RF transmission,
does not access the RTL-SDR, and establishes the processing-chain reference
before hardware uncertainty is introduced.
