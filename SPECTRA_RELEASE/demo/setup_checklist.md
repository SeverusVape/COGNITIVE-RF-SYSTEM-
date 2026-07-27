# SPECTRA Demonstration Setup Checklist

## Release Baseline

- [ ] Use the final approved release tag or verified source commit.
- [ ] Confirm `SPECTRA_RELEASE/RELEASE_METADATA.md` matches the selected
  revision.
- [ ] Keep the presentation, release package, and backup screenshots on a
  second storage device.

## Hardware

- [ ] RTL-SDR Blog V3 connected to a reliable USB port.
- [ ] Dipole antenna and coaxial cable firmly connected.
- [ ] Antenna positioned at the rehearsed location and orientation.
- [ ] Laptop power supply connected.
- [ ] USB connection verified.
- [ ] Receiver allowed to warm up for 10–15 minutes if measurement stability
  will be discussed.

## Software

- [ ] Repository checked out at the approved release revision.
- [ ] CPython 3.10.11 virtual environment activated.
- [ ] `python -m pip check` reports no broken requirements.
- [ ] All 283 automated tests pass.
- [ ] SDR++, GQRX, GNU Radio, `rtl_test`, and other RTL-SDR users are closed.
- [ ] No terminal command still owns the receiver.

## Presentation Display

- [ ] Display cable or wireless presentation link tested.
- [ ] Resolution and scaling match the rehearsed setup.
- [ ] SPECTRA panels and plot labels are readable from the audience position.
- [ ] Notifications, email previews, and messaging alerts disabled.
- [ ] Desktop and terminal contain no private information.
- [ ] Mouse pointer size and visibility are appropriate.

## Application

- [ ] Launch succeeds with `python main.py`.
- [ ] `RECEIVER CONNECTED` displayed.
- [ ] FFT updates continuously.
- [ ] Waterfall updates continuously.
- [ ] Peak-candidate markers appear on an active frequency.
- [ ] Receiver status values update.
- [ ] Manual tuning confirmed.
- [ ] Rehearsed survey range completes.
- [ ] Detailed SMART report opens without clipping.
- [ ] Auto-Tune produces `ON RECOMMENDED CHANNEL`.
- [ ] Clean shutdown produces `SDR CLOSED`.

## RF Rehearsal

- [ ] Primary active frequency confirmed at the presentation location.
- [ ] Backup frequency confirmed.
- [ ] 88–92 MHz survey behavior rehearsed.
- [ ] Expected environmental variability understood.
- [ ] No script promises a specific recommendation result.

## Backup Evidence

- [ ] All six final screenshots available.
- [ ] REAL-RF campaign report open or bookmarked.
- [ ] Requirements traceability matrix available.
- [ ] Validation evidence index available.
- [ ] Release-candidate verification report available.
- [ ] Failure-recovery checklist immediately accessible.

## Final Five-Minute Check

- [ ] Receiver connected.
- [ ] Antenna stable.
- [ ] SPECTRA at intended opening screen.
- [ ] Presentation timer ready.
- [ ] Backup screenshots one click away.
