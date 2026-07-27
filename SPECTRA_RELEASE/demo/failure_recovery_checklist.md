# Demonstration Failure-Recovery Checklist

## Receiver Does Not Connect

1. Close SPECTRA.
2. Close all other SDR software.
3. Disconnect and reconnect the RTL-SDR.
4. Confirm the USB connection and antenna.
5. Run `rtl_test -t`, record the result, and stop it before relaunching.
6. Relaunch with `python main.py`.
7. If recovery fails, use the verified screenshots and REAL-RF replay evidence.

## RF Environment Is Quiet or Has Changed

1. Tune the rehearsed alternate frequency.
2. Reposition the antenna near the planned location.
3. Explain that live RF conditions are environmental.
4. Use recorded REAL-RF evidence rather than making unsupported claims.

## Survey Does Not Complete

1. Do not repeatedly click controls.
2. Note the current status message.
3. Clear the survey only after the receiver is stable.
4. Retry the smaller rehearsed range once.
5. If it still fails, switch to the completed-survey screenshot and report.

## Display or UI Problem

1. Restore the verified window size and display scaling.
2. Avoid changing layout or code during the presentation.
3. Use the prepared screenshots if readability cannot be restored quickly.

## General Rule

Do not debug live for more than one minute. State the limitation clearly and
move to verified recorded evidence.
