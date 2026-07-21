# Required Plots and Final Report Outputs

All figures must state the configuration ID, sample count, and whether the data
are synthetic or RTL-SDR hardware measurements. Error bars must be identified
as standard deviation, range, confidence interval, or another explicitly named
quantity.

## Algorithm-validation outputs

### Figure AV-1 — FFT frequency error

- X-axis: expected tone frequency or FFT offset
- Y-axis: signed frequency error in Hz
- Separate series: bin-centered and off-bin tones
- Caption conclusion: numerical FFT-axis accuracy under known synthetic input

### Figure AV-2 — Window leakage comparison

- X-axis: frequency offset from tone
- Y-axis: relative level in dB
- Series: rectangular and gain-corrected Hann window
- Caption conclusion: leakage reduction and main-lobe tradeoff

### Figure AV-3 — Local noise-floor tracking

- X-axis: frequency
- Y-axis: relative dB
- Curves: known baseline, noisy observation, estimated floor, detection threshold
- Include one flat and one uneven/curved example

### Figure AV-4 — Probability of detection versus SNR

- X-axis: declared SNR in dB
- Y-axis: detected trials / total trials
- Include trial count and matching tolerance
- Do not call this receiver sensitivity; it is algorithm performance

### Table AV-1 — Noise-only false alarms

Required columns:

| Baseline | Frames | Frames with false peaks | Total false peaks | False peaks/frame |
| --- | ---: | ---: | ---: | ---: |

### Figure AV-5 — Two-tone resolution

- X-axis: tone separation in kHz
- Y-axis: probability of detecting both tones
- Series: equal amplitude, -6 dB, and -12 dB secondary tone
- Mark configured 75 kHz spacing

### Figure AV-6 — Bandwidth heuristic

- X-axis: controlled spectral width in kHz
- Y-axis: estimated minus-15 dB width in kHz
- Add ideal-reference line for context only
- Caption must state that this is not regulatory occupied bandwidth

### Figure AV-7 — Synthetic occupancy accuracy

- X-axis: expected above-threshold bin fraction (%)
- Y-axis: measured occupancy (%)
- Include clustered and distributed occupied-bin conditions

## Hardware/system-validation outputs

### Figure HV-1 — Cold-start frequency drift

- X-axis: elapsed minutes after connection
- Y-axis: signed frequency error in kHz
- Mark the selected normal warm-up interval

### Table HV-1 — Multi-frequency accuracy

| Reference | Expected MHz | Mean measured MHz | Mean error kHz | Mean error ppm | Std. dev. kHz | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |

### Figure HV-2 — Frequency error versus carrier frequency

- X-axis: expected carrier frequency in MHz
- Y-axis: signed error in kHz or ppm
- Include repeated-observation error bars
- Caption must describe reference-source limitations

### Figure HV-3 — Relative amplitude linearity

- X-axis: applied attenuation in dB
- Y-axis: observed relative change in dB
- Include ideal-reference line and residual-error summary
- Omit this claim if known attenuation was not available

### Figure HV-4 — Relative amplitude repeatability

- Box plot or time series of unchanged-source observations
- Report mean, standard deviation, and range
- Label values as relative dB

### Figure HV-5 — Noise and threshold by condition

- Conditions: terminated if available, quiet antenna, active antenna, gain cases
- Values: median floor and median threshold with variation
- Accompany with occupancy and peak-count table

### Figure HV-6 — Quiet versus active occupancy

- Box plot of repeated occupancy observations
- Same span, gain, FFT size, and sample rate for compared conditions
- Report mean, standard deviation, and effect size

### Figure HV-7 — Controlled source ON/OFF occupancy

- Paired or grouped comparison of OFF and ON observations
- Include threshold and peak-count context

### Table HV-2 — SMART survey run summary

| Run | Range MHz | Winner MHz | Runner-up MHz | Winner score | Margin | Confidence | Completed points |
| ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |

### Figure HV-8 — Recommendation repeatability

- Winner-frequency histogram for each survey range
- Display run count and configuration ID

### Figure HV-9 — Candidate occupancy and score variation

- Per-frequency mean occupancy with standard-deviation bars
- Per-frequency mean SMART score with standard-deviation bars
- Use separate panels because units differ

### Case Study HV-1 — Explainable winner change

Include two surveys with different winners and a component table:

| Candidate | Occupancy score | Power | Persistence | Age | Strength | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |

Explain the observed measurement change and the exact contribution that changed
the ranking. Do not describe the change as learning.

### Table HV-3 — Survey sequencing verification

| Survey | Requested points | Confirmed tunes | Stored results | Auto-tune confirmed | Errors |
| --- | ---: | ---: | ---: | --- | --- |

Pair the table with the event-driven sequence diagram and the automated test
result.

## Required discussion sections

1. **Measurement definitions**
   - Relative FFT dB
   - Spectral-bin occupancy
   - Peak-frequency estimate
   - Minus-15 dB bandwidth heuristic
   - Score-separation confidence
2. **Uncertainty and limitations**
   - 250 Hz FFT-bin spacing versus actual frequency accuracy
   - RTL-SDR oscillator error and temperature drift
   - 8-bit ADC dynamic range
   - Automatic gain and fixed-gain differences
   - DC spike, overload, images, and intermodulation
   - Antenna and environmental dependence
   - Reference-source uncertainty
3. **Repeatability versus accuracy**
   - Clearly separate small measurement spread from closeness to a true value
4. **Decision-engine interpretation**
   - Explainable heuristic, not ML
   - Existing weights remained unchanged during validation
5. **Scope statement**
   - Results characterize this RTL-SDR configuration and test environment
   - No laboratory-grade or regulatory-grade claim

## Final evidence checklist

- [ ] Configuration records complete
- [ ] Raw synthetic CSV files preserved
- [ ] Raw hardware CSV files preserved
- [ ] Invalid trials retained and labeled
- [ ] Derived summary tables reproducible from raw data
- [ ] Plot scripts record their input filenames
- [ ] Every figure has units and sample count
- [ ] Relative values are never labeled dBm
- [ ] Occupancy scope is stated correctly
- [ ] Frequency references and their limitations are identified
- [ ] SMART winner changes are explained from recorded components
- [ ] Final conclusions distinguish pass evidence from observed limitations

