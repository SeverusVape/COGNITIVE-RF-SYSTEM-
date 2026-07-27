# Release Test Results Summary

## Automated Tests

Command:

```text
.venv/bin/python -m unittest discover -s tests
```

Verified result on July 27, 2026:

```text
Ran 283 tests
OK
```

No failures, errors, or unexpected skips were reported.

## Dependency Health

Command:

```text
.venv/bin/python -m pip check
```

Result:

```text
No broken requirements found.
```

## Hardware Release Check

The live RTL-SDR release-candidate workflow passed:

- startup and receiver connection;
- FFT, waterfall, peak-marker, and status updates;
- manual tuning;
- five-point 88–92 MHz survey;
- detailed SMART report;
- confirmed Auto-Tune;
- clean `SDR CLOSED` shutdown; and
- successful relaunch.

See `../documentation/RELEASE_CANDIDATE_VERIFICATION_REPORT.md`.
