# Demonstration Setup Checklist

## Before Arrival

- [ ] Use verified source commit `b52f77e` or the final approved release tag.
- [ ] Activate the frozen CPython 3.10.11 environment.
- [ ] Confirm `pip check` reports no broken requirements.
- [ ] Confirm all 283 automated tests pass.
- [ ] Copy the release package, presentation, and screenshots to backup media.

## Hardware

- [ ] Connect the RTL-SDR Blog V3 directly to a reliable USB port.
- [ ] Attach and position the dipole antenna.
- [ ] Allow 10–15 minutes of receiver warm-up when measurement stability is
  discussed.
- [ ] Close SDR++, GQRX, GNU Radio, `rtl_test`, and other RTL-SDR users.
- [ ] Confirm the selected demo frequencies are active at the presentation
  location.

## Application

- [ ] Launch with `python main.py`.
- [ ] Confirm `RECEIVER CONNECTED`.
- [ ] Confirm FFT and waterfall updates.
- [ ] Confirm peak markers and status updates.
- [ ] Rehearse the selected survey range.
- [ ] Confirm detailed results and Auto-Tune.
- [ ] Reset the application to the desired opening state.

## Presentation

- [ ] Disable notifications.
- [ ] Connect power and presentation display.
- [ ] Verify resolution and scaling.
- [ ] Open backup screenshots and validation reports.
- [ ] Keep the failure-recovery checklist accessible.
