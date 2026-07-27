# SPECTRA Demonstration Failure-Recovery Checklist

## General Recovery Rule

Do not debug live for more than one minute. State the limitation accurately,
move to verified recorded evidence, and preserve presentation flow.

## Problem: SDR Not Detected

### Actions

1. Close SPECTRA.
2. Close every other SDR application or utility.
3. Disconnect and reconnect the RTL-SDR USB device.
4. Confirm the antenna and USB connections.
5. If necessary, run `rtl_test -t` to verify enumeration.
6. Stop `rtl_test` before restarting SPECTRA.
7. Relaunch using `python main.py`.
8. If the receiver still fails, show the release verification report and
   prepared screenshots.

### Explanation

Only one process may own the RTL-SDR. USB connection and library discovery
are separate from the detector and SMART logic.

## Problem: Device Is Busy

### Actions

1. Close SPECTRA.
2. Stop SDR++, GQRX, GNU Radio, `rtl_test`, REAL-RF capture, or any prior
   Python instance.
3. Reconnect the receiver if ownership is not released.
4. Relaunch once.

## Problem: Weak RF Signal

### Actions

1. Reposition or rotate the antenna.
2. Tune the rehearsed backup frequency.
3. Allow several FFT/waterfall updates to accumulate.
4. If the environment remains quiet, use the verified REAL-RF evidence.

### Explanation

Live RF conditions depend on antenna placement, propagation, interference,
and activity at the presentation location.

## Problem: Survey Recommendation Changes

### Actions

1. Do not rerun repeatedly to force the rehearsed result.
2. Show the measured candidate values and score breakdown.
3. Explain why the current winner received the highest score.

### Explanation

SMART is deterministic for a given set of measured inputs. A changed RF
environment can change occupancy, power, history factors, ranking, and the
resulting recommendation.

## Problem: Survey Does Not Complete

### Actions

1. Do not repeatedly select **Start Survey**.
2. Read the visible status message.
3. Confirm the receiver is still updating.
4. Clear the survey only after the receiver is stable.
5. Retry the short rehearsed range once.
6. If the retry fails, use the completed-survey and SMART-report screenshots.

## Problem: Weak or Unclear Peak Markers

### Actions

1. Use the rehearsed active frequency.
2. Reposition the antenna.
3. Wait for the FFT smoothing and waterfall history to stabilize.
4. Describe markers as peak candidates, not identified transmitters.

## Problem: UI Is Clipped or Difficult to Read

### Actions

1. Restore the rehearsed display resolution and scaling.
2. Maximize or resize SPECTRA to the verified presentation dimensions.
3. Do not modify UI code during the presentation.
4. Switch to prepared screenshots if visibility cannot be restored quickly.

## Problem: Application Closes Unexpectedly

### Actions

1. Confirm the receiver is no longer owned by another process.
2. Relaunch once with `python main.py`.
3. If relaunch fails, continue with screenshots, reports, and immutable
   REAL-RF evidence.

## Evidence Fallback Order

1. Final interface screenshots
2. SMART report screenshot
3. Release-candidate verification report
4. REAL-RF campaign report
5. Requirements traceability and validation evidence index
