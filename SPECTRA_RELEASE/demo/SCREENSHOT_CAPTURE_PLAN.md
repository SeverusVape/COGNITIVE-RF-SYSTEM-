# SPECTRA Screenshot Capture Plan

## Capture Standard

Use the final approved release revision and one consistent presentation
resolution. Before every capture:

- connect the RTL-SDR and confirm `RECEIVER CONNECTED`;
- disable notifications;
- close unrelated applications;
- remove private information from the desktop and terminal;
- use stable antenna placement;
- avoid cursor obstruction and transient error states; and
- verify displayed values are technically defensible.

Do not crop away information required to interpret the image. Minor cropping
is acceptable only when the screenshot purpose explicitly focuses on a
single engineering panel.

## 01_main_interface.png

### Purpose

Establish the complete SPECTRA operator interface and information hierarchy.

### Must Be Visible

- Full SPECTRA window
- `RECEIVER CONNECTED`
- Survey controls
- Receiver center controls
- FFT, waterfall, and survey heatmap
- Right-side peak, status, and history panels
- SPECTRA window title

### Must Not Be Visible

- Notifications or private desktop content
- Error states
- Empty or initializing plots
- Another application covering SPECTRA
- Unexplained validation or debug controls

## 02_live_fft_waterfall.png

### Purpose

Show real-time DSP output and temporal RF activity.

### Must Be Visible

- Stable FFT trace
- At least one clear peak candidate
- Readable frequency and relative-power axes
- Peak marker and frequency label
- Waterfall history aligned with the active spectrum
- Confirmed center frequency

### Must Not Be Visible

- A tuning transient
- A blank waterfall
- Clipped axes or labels
- Claims of calibrated dBm

## 03_survey_progress.png

### Purpose

Demonstrate responsive, automated survey sequencing.

### Must Be Visible

- Survey range and step
- `SURVEY IN PROGRESS` state
- Current progress or point count
- Live receiver plots
- A consistent active survey state

### Must Not Be Visible

- Completed recommendation
- Contradictory `NO SURVEY DATA` status
- Temporary tune-error message
- Frozen or blank plots

## 04_survey_complete.png

### Purpose

Show the completed survey result in the main interface.

### Must Be Visible

- `SURVEY COMPLETE`
- Recommended frequency
- Number of points scanned
- **View detailed results** control
- Survey occupancy history
- High-contrast recommendation marker
- Survey history card

### Must Not Be Visible

- Survey still in progress
- Recommendation marker outside the measured range
- Clipped history labels
- Unsupported accuracy wording

## 05_SMART_report.png

### Purpose

Demonstrate explainable recommendation output.

### Must Be Visible

- SMART recommendation and frequency
- SMART score
- Spectral-bin occupancy
- Recommended and runner-up rows
- Score separation
- Why-selected explanation
- Score breakdown
- Supporting diagnostics when they fit clearly

### Must Not Be Visible

- Scroll position that hides the recommendation
- Clipped table columns
- “Statistical confidence” wording
- Unreadably small text
- Desktop or terminal distractions

If one screenshot cannot show both primary decision content and diagnostics
legibly, prioritize the primary decision view. Supporting evidence remains
available in the release documents.

## 06_auto_tune_result.png

### Purpose

Show that the receiver is following the survey recommendation.

### Must Be Visible

- Confirmed receiver center frequency
- `ON RECOMMENDED CHANNEL`
- Current center matching the recommendation
- Stable FFT and waterfall
- Completed survey state

### Must Not Be Visible

- `TUNING RECEIVER` transient
- `OFF RECOMMENDED CHANNEL`
- Requested-but-unconfirmed frequency
- Invalid-frequency or connection-error state

## Final Acceptance Checklist

- [ ] Exact filenames used
- [ ] All six files are PNG
- [ ] Consistent resolution and visual scaling
- [ ] No private information
- [ ] No notifications
- [ ] No transient or contradictory status
- [ ] Text and axes readable at presentation size
- [ ] Relative measurement terminology preserved
- [ ] Recommendation and score values internally consistent
- [ ] Screenshots copied to backup media
