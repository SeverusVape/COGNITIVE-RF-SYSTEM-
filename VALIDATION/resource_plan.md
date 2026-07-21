# Validation Resource Plan

## Freeze status

The software environment and processing baseline are recorded. No measurements
have been collected. The available RF chain is an RTL-SDR Blog V3 with an
R860 tuner, RTL2832U, 1-PPM TCXO, and the supplied telescopic dipole antenna
kit. No signal generator, known attenuator, 50-ohm termination, secondary
receiver, or frequency counter is available.

## Experiment-to-resource mapping

| Experiment | Minimum resources | Preferred resources | Current readiness | Fallback |
| --- | --- | --- | --- | --- |
| AV-FFT / AV-NF / AV-PD / AV-BW / AV-OCC | Project Python environment; deterministic synthetic IQ generator | None beyond available computer | Ready after synthetic conventions and seeds are frozen | None needed |
| HV-FREQ-02 cold-start drift | RTL-SDR; antenna; one stable narrow reference | Controlled reference carrier | Equipment ready; exact receive-only reference still required | Use a documented narrow broadcast/beacon; do not use FM as primary drift reference |
| HV-FREQ-01 frequency accuracy | Warm RTL-SDR; antenna; at least three credible references | Controlled source or independent reference | Exact receive-only references still required | Reduce claim to indicative system error and state reference limitations |
| HV-AMP-01 relative linearity | RTL-SDR at fixed gain; stable source; known attenuators | Calibrated step attenuator | Not feasible with available equipment | Omit linearity claim |
| HV-AMP-02 amplitude repeatability | RTL-SDR at fixed gain; stable received signal; fixed geometry | Controlled source | Feasible with dipole and live signal after geometry is frozen | Use stable live signal and report propagation limitation |
| HV-NF-01 noise/threshold | RTL-SDR; fixed gain; recorded antenna setup | 50-ohm termination plus quiet and active spans | Feasible only as antenna-connected comparison | Compare quiet and active antenna spans; do not claim receiver-only noise floor |
| HV-OCC-01 live occupancy | RTL-SDR; fixed settings; quiet and active spans | Recorded RF geometry | Pending span selection | Use 88-92 and 115-121 MHz comparative spans after prescreening |
| HV-OCC-02 controlled ON/OFF | RTL-SDR; legal controlled source | Signal generator plus attenuation | Not feasible with available equipment | Omit controlled ON/OFF claim |
| HV-SMART-01 / 02 | RTL-SDR; dipole; frozen survey settings | Stable placement and RF environment | Ready after antenna geometry and session location are recorded | Existing 88-92 and 115-121 MHz ranges are suitable |
| HV-SEQ-01 | RTL-SDR; application; frozen survey settings | Same setup as SMART tests | Ready after antenna geometry and session location are recorded | None needed |

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

1. Before each hardware comparison series photograph or record the selected
   dipole angle, element orientation, mounting, window distance, height, and
   cable routing. The available geometry is documented but is intentionally
   configurable between separately identified series.
2. Record the receiver serial if available.
3. Pre-screen the FCC-documented 91.5 MHz WNYE, 90.7 MHz WFUV, and 88.3 MHz
   WBGO assignments without treating the pre-screen as validation data. Select
   the clearest stable center and record the reason. These wideband FM signals
   provide secondary evidence only, not laboratory-grade calibration.
4. Create `CFG-H02` when fixed-gain repeatability, noise, or occupancy tests
   begin. Controlled linearity and controlled ON/OFF tests are omitted.
5. Enter session start time only when data collection actually begins.
6. Photograph or otherwise record the physical setup without including a
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
