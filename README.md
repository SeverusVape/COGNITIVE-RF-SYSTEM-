# Adaptive SDR Spectrum Analyzer

A real-time RTL-SDR spectrum analyzer and explainable RF survey system built with
Python, PyQt6, NumPy, SciPy, and pyqtgraph.

The application displays a live FFT spectrum and waterfall, detects persistent
signals, measures RF occupancy across a configurable frequency range, and ranks
survey frequencies using three decision modes. It has been developed and
hardware-tested with an RTL-SDR Blog V3 dongle on macOS.

## Current project status

- Stable application baseline
- Non-blocking RTL-SDR acquisition and tuning
- Real-time spectrum, waterfall, and peak markers
- Automated multi-frequency surveys
- Explainable SMART recommendation scoring
- Runner-up, decision margin, and score-separation confidence
- Professional Phase 1 user interface
- 107 automated tests passing

The application is receive-only. It does not transmit or control external RF
equipment.

## Main features

### Real-time spectrum monitoring

- 2.048 MSPS default sample rate
- 8,192 complex samples per FFT frame
- Gain-compensated Hann FFT window
- Smoothed real-time spectrum trace
- Frequency-aligned waterfall history
- Up to three confirmed peak markers

### Adaptive signal detection

- Local percentile-based noise-floor estimation
- Per-bin adaptive detection threshold
- Peak spacing expressed in physical frequency units
- Bandwidth derived from FFT-bin spacing
- Robust bandwidth-stability tracking after five observations
- Robust frequency-drift tracking after five observations
- Rolling 10-second signal duty-cycle tracking
- Survey-report diagnostics for bandwidth stability, frequency stability,
  frequency drift, and recent duty cycle; these measurements are observational
  and do not yet affect recommendation scoring
- Tolerance-based feature association keeps small FFT-bin frequency jitter in
  one diagnostic history while preserving separately detected signals
- Stability diagnostics become available after three matched observations and
  remain explicitly provisional until five observations have been collected
- Diagnostic-only behavior profiles describe frequency stability, bandwidth
  stability, and recent activity without claiming modulation or service type
- Survey reports compare diagnostic evidence and behavior coverage across the
  recommended frequency and other measured candidates
- The detailed survey report opens maximized and uses a readable three-column
  card layout for recommendation, scoring, and signal diagnostics
- Measured occupancy and candidate diagnostic coverage remain grouped in a
  separate comparison row for quick review
- Temporal confirmation to reject single-frame spikes
- Small peak-frequency drift tolerance

### RF survey automation

- Configurable start, stop, and step frequencies
- Inclusive scan-frequency generation
- Multiple post-tune frames per survey point
- Validated median measurement aggregation
- Occupancy-history heatmap
- Most-occupied frequency history
- Automatic tuning to the selected recommendation

### Explainable decision modes

| Mode | Selection policy |
| --- | --- |
| Find Free Channel | Selects the frequency with the lowest measured occupancy |
| Find Active Signal | Selects the frequency with the highest measured occupancy |
| Smart Recommendation | Balances occupancy, relative power, persistence, age, and strength |

SMART mode reports:

- Recommended frequency
- Overall score and maximum possible score
- Runner-up frequency and score
- Decision margin
- LOW, MODERATE, or HIGH score-separation confidence
- Individual score contributions
- Maximum and average relative power
- Measured occupancy ranking

Decision confidence describes the score separation between the winner and
runner-up. It is not a statistical confidence interval or probability of
correctness.

## Hardware and software requirements

### Hardware

- RTL-SDR-compatible receiver
- Tested device: RTL-SDR Blog V3 with Rafael Micro R820T tuner
- Antenna appropriate for the frequency range being monitored
- Direct USB connection is recommended during troubleshooting

### Software

- Python 3.10 or newer
- `librtlsdr`
- NumPy
- SciPy
- PyQt6
- pyqtgraph
- pyrtlsdr

The current development environment uses Python 3.10.11.

## macOS installation

Install the RTL-SDR system library with Homebrew:

```bash
brew install librtlsdr
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the Python dependencies:

```bash
python -m pip install numpy scipy PyQt6 pyqtgraph pyrtlsdr
```

The pyrtlsdr project also provides an optional installation that bundles its
RTL-SDR library dependency on supported platforms:

```bash
python -m pip install "pyrtlsdr[lib]"
```

Use either the Homebrew `librtlsdr` installation or the bundled pyrtlsdr
approach appropriate for your environment. Avoid mixing conflicting library
installations if the receiver is already detected correctly.

Useful references:

- [Homebrew librtlsdr formula](https://formulae.brew.sh/formula/librtlsdr)
- [pyrtlsdr installation documentation](https://pyrtlsdr.readthedocs.io/en/stable/Overview.html#installation)
- [RTL-SDR Blog V3 user guide](https://www.rtl-sdr.com/rtl-sdr-blog-v-3-dongles-user-guide/)

## Verify the receiver

Connect the RTL-SDR and make sure no other SDR application is using it. Then run:

```bash
rtl_test -t
```

Stop the test before starting the analyzer. Only one application should own the
dongle at a time.

## Run the application

From the project root:

```bash
source .venv/bin/activate
python main.py
```

The receiver starts at 100 MHz by default. The default configuration is defined
in [`UTILS/config.py`](UTILS/config.py).

## Operator guide

### Manual tuning

1. Enter a center frequency in MHz in the Receiver Center panel.
2. Select **Tune**.
3. Wait for the spectrum, waterfall, and system-status values to update.

The application currently validates center frequencies from 24 MHz to
1,766 MHz. Actual useful reception depends on the receiver, antenna, RF
environment, gain behavior, and hardware configuration.

### Run a survey

1. Enter the start frequency in MHz.
2. Enter a stop frequency greater than the start frequency.
3. Enter a positive step size.
4. Select a decision mode.
5. Select **Start Survey**.

The stop frequency is included in the survey. If the chosen step does not land
exactly on the stop frequency, the stop value is added as the final point.

Each point is tuned and measured using multiple valid post-tune frames. A
typical survey therefore takes several seconds per frequency. Do not start a
second survey while one is already running.

When the survey completes:

- The recommended frequency is displayed.
- The receiver automatically tunes to that frequency.
- The survey heatmap and history panel are updated.
- **View detailed results** opens the full decision report.

### Clear a survey

Select **Clear Survey** to stop the survey timer and remove:

- Survey frequencies and measurements
- Recommendation results
- Heatmap history
- Survey-history summary
- Cached detailed report

### Auto-tune best

**Auto-tune best** requires completed survey data. It repeats the current
decision policy and tunes the receiver to the recommended frequency.

## Understanding the display

### Spectrum

The upper graph shows windowed FFT power versus frequency. Peak markers are
displayed only after temporal confirmation.

### Waterfall

The waterfall shows how received energy changes over time. Brighter colors
represent greater relative FFT power.

### Survey occupancy history

Each heatmap column corresponds to a surveyed center frequency. The
recommendation marker identifies the frequency selected by the active decision
mode.

### System status

The status card reports:

- Receiver connection state
- Center frequency
- Sample rate
- Visible frequency range
- Confirmed signal count
- Median adaptive threshold
- Current occupancy

### Signal table

The table uses compact rule-based labels:

| Code | Meaning |
| --- | --- |
| W / M / S | Weak / Medium / Strong |
| N / A / P / L | New / Active / Persistent / Long |
| BC | FM broadcast-band candidate |
| AIRBND | Airband-frequency candidate |
| NOAA / WX | Weather-band candidate |
| 2m / 70cm | Amateur-band candidate |
| GMRS | GMRS-frequency candidate |

These are frequency-band and rule-based context labels, not verified modulation
or service identification. A signal located inside a band is not guaranteed to
belong to the expected service.

## SMART scoring

The configured maximum SMART score is 111 points.

| Component | Maximum | Purpose |
| --- | ---: | --- |
| Occupancy | 50 | Rewards lower occupancy across the full 0-100% range |
| Relative power | 30 | Compares peak power with the survey median |
| Persistence | 15 | Rewards established signal history |
| Age | 10 | Rewards sustained observation |
| Strength | 6 | Provides a bounded supporting contribution |

Scoring constants are centralized in [`UTILS/config.py`](UTILS/config.py).
Candidate ties are resolved deterministically using occupancy, power, and
frequency rather than dictionary insertion order.

SMART scoring is an explainable engineering heuristic. It is not a trained
machine-learning model.

## Signal-processing pipeline

```text
RTL-SDR V3
    |
    v
SDRWorker background thread
    |
    v
Gain-compensated Hann FFT
    |
    v
Local adaptive noise floor
    |
    v
Per-bin detection threshold
    |
    v
Peak spacing and bandwidth estimation
    |
    v
Temporal peak confirmation
    |
    +--> Spectrum, waterfall, status, and signal table
    |
    +--> FeatureStore and signal history
    |
    +--> Survey measurement aggregation
              |
              v
        Decision engine and report
```

## Architecture

```text
main.py
|
+-- SDR/
|   +-- sdr_manager.py       RTL-SDR device wrapper
|   +-- sdr_worker.py        Background acquisition and tuning
|   +-- fft_processing.py    Windowing and FFT power calculation
|   +-- detection.py         Local threshold and peak detection
|
+-- SIGNALS/
|   +-- peak_confirmation.py Temporal confirmation
|   +-- frequency_band.py    Frequency-allocation context
|   +-- signal_classifier.py Strength, persistence, and band context
|   +-- feature_extractor.py Feature snapshots and freshness
|   +-- signal_history.py    Observation history and stale pruning
|
+-- SURVEY/
|   +-- survey_controller.py Survey lifecycle and hardware coordination
|   +-- survey_manager.py    Survey state, ranking, and report construction
|   +-- decision_engine.py   FREE, ACTIVE, and SMART policies
|
+-- UI/
|   +-- theme.py             Shared visual design system
|   +-- graph_style.py       Performance-safe graph styling
|   +-- *_panel.py           Main-window panels
|   +-- survey_popup.py      Detailed survey report window
|
+-- UTILS/
|   +-- config.py            Receiver and scoring configuration
|   +-- frequency_axis.py    FFT axis and image-edge alignment
|   +-- measurement_aggregation.py
|   +-- occupancy.py
|
+-- tests/                   Automated regression suite
```

The RTL-SDR device is owned by `SDRWorker`, not the Qt GUI thread. Samples and
status changes return to the interface through Qt signals. This prevents normal
device reads and tune requests from blocking the event loop.

## Configuration

Important defaults in [`UTILS/config.py`](UTILS/config.py):

| Setting | Default |
| --- | ---: |
| Center frequency | 100 MHz |
| Center-frequency limits | 24-1,766 MHz |
| Sample rate | 2.048 MSPS |
| FFT samples | 8,192 |
| Gain | Automatic |
| Waterfall history | 200 frames |
| Feature/history stale age | 30 seconds |
| Continuous-detection gap tolerance | 0.5 seconds |
| Persistence thresholds | Active 2 s, Persistent 5 s, Long 15 s |
| Minimum bandwidth-stability samples | 5 |
| Minimum frequency-stability samples | 5 |
| Frequency-stability reference | 25 kHz |
| Signal duty-cycle window | 10 seconds |
| Survey measurement buffer | 10 frames |
| Minimum survey frames | 3 |
| Peak-confirmation requirement | 2 hits in 3 frames |
| Peak-confirmation tolerance | 25 kHz |

Change one parameter at a time and rerun the complete test suite before
accepting a new configuration baseline.

## Run the tests

The tests do not require a connected RTL-SDR:

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Current verified result:

```text
Ran 107 tests
OK
```

The suite covers:

- SMART scoring and decision confidence
- Measurement validation and median aggregation
- FFT windowing and spectral leakage
- Frequency-axis alignment and occupancy calculation
- Local adaptive noise-floor estimation
- Peak detection and temporal confirmation
- Feature freshness and signal-history pruning
- Survey generation, ranking, progress, and report HTML
- Status and survey-history UI output

Automated tests verify deterministic software behavior. Live RTL-SDR tests are
still required for the USB device, driver, tuner, antenna, and RF environment.

## Troubleshooting

### `Could not open SDR` or `LIBUSB_ERROR_IO`

1. Close every other SDR program and terminal test.
2. Disconnect and reconnect the dongle.
3. Prefer a direct USB connection while troubleshooting.
4. Run `rtl_test -t`.
5. Restart the analyzer after the device test releases the dongle.

### `LIBUSB_ERROR_OTHER (-99)` or sample-acquisition failure

The USB/device connection was lost or became unavailable.

1. Stop the application.
2. Reconnect the RTL-SDR.
3. Check the USB port, adapter, or hub.
4. Confirm the receiver with `rtl_test -t`.
5. Restart the application.

The analyzer stops using failed measurements rather than completing a survey
with invalid RF data.

### `PLL not locked`

A brief tuner warning may appear during initialization or tuning. If valid
samples continue and the display updates normally, observe the system status.
If tuning or sample reads fail, reconnect the receiver and restart the
application.

### No peaks are displayed

- Confirm the antenna is appropriate for the selected band.
- Tune to a known active local frequency.
- Check that the waterfall contains visible RF energy.
- Verify the receiver with another trusted SDR application, then close that
  application before restarting this analyzer.
- Remember that peaks require temporal confirmation.

### Survey stops with a measurement error

The required number of valid post-tune frames was not available. Check the
receiver connection and run a smaller survey after reconnecting the dongle.

### Invalid frequency

Enter a finite numeric value between the configured center-frequency limits.
Blank values, text, NaN, infinity, and out-of-range values are rejected.

## Data and logging

Signal logging is implemented in [`LOGGING/signal_logger.py`](LOGGING/signal_logger.py)
but is disabled by default:

```python
LOGGING_ENABLED = False
```

When enabled, new detected signal identifiers are appended to
`signal_log.txt`. Do not enable long-running logging without first defining a
data-retention and rotation policy.

## Current limitations

- Displayed power is relative FFT power in dB, not calibrated dBm.
- The signal classifier is a rule-based baseline, not a professional
  modulation classifier.
- Frequency-band labels indicate context, not confirmed transmitter identity.
- Decision confidence measures score separation, not statistical certainty.
- Only the RTL-SDR Blog V3/macOS configuration has received repeated live
  validation during the current project phase.
- Survey data is not yet exportable as structured CSV or JSON.
- The application currently supports one local RTL-SDR device.

## Planned engineering sequence

1. Preserve this README and the current application as the documentation
   baseline.
2. Upgrade signal classification by separating band context from measured
   signal characteristics.
3. Replace absolute strength thresholds with power above the local noise floor.
4. Add time-based persistence, bandwidth stability, frequency drift, and duty
   cycle features.
5. Validate detection and classification across additional RF bands.
6. Add structured survey-data export after the result schema is stable.

Classifier improvements should be introduced incrementally with new regression
tests and live hardware checks after every bounded change.

## Responsible operation

Use the receiver in accordance with local laws and regulations. This project is
intended for spectrum observation and engineering education. Do not use it to
interfere with radio services or to disclose protected communications.
