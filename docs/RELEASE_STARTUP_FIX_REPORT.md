# SPECTRA Release Startup Fix Report

## Problem Description

The documented macOS launch command failed before the SPECTRA user
interface initialized:

```text
python main.py
```

`pyrtlsdr` raised `ImportError: Error loading librtlsdr` while importing
`RtlSdr`. The working Homebrew library was installed at:

```text
/opt/homebrew/opt/librtlsdr/lib/librtlsdr.dylib
```

## Root Cause

`SDR/sdr_manager.py` imported `RtlSdr` at module load time. On the frozen
macOS environment, the dynamic loader did not search the Homebrew
`librtlsdr` directory automatically. The import therefore failed before
SPECTRA could initialize the receiver worker or display connection status.

The standalone REAL-RF capture utility already demonstrated a safe
discovery method: on macOS only, detect standard Apple Silicon and Intel
Homebrew library directories and expose them through `DYLD_LIBRARY_PATH`
during the `pyrtlsdr` import.

## Files Changed

- `SDR/rtlsdr_library.py`
  - Adds the focused, platform-safe import environment helper.
- `SDR/sdr_manager.py`
  - Applies library discovery before importing `RtlSdr`.
- `tests/test_rtlsdr_library.py`
  - Adds focused discovery, restoration, and cross-platform tests.
- `docs/RELEASE_STARTUP_FIX_REPORT.md`
  - Records the release-startup defect, correction, and verification.

No detector, FFT, survey, SMART, UI, or validation file was modified.

## Fix Approach

On macOS, SPECTRA now checks the standard Homebrew locations:

```text
/opt/homebrew/opt/librtlsdr/lib
/usr/local/opt/librtlsdr/lib
```

A directory is used only when it contains `librtlsdr.dylib`. Discovered
directories are prepended without duplicating existing entries. The
original `DYLD_LIBRARY_PATH` is restored immediately after the `pyrtlsdr`
import.

Linux and Windows receive no environment modification and retain their
normal system library discovery.

## Verification Results

### Focused Tests

Command:

```text
.venv/bin/python -m unittest tests.test_rtlsdr_library -v
```

Result:

```text
4 tests passed
```

Coverage includes:

- macOS Homebrew path discovery;
- preservation and restoration of an existing library path;
- missing-library behavior; and
- non-macOS no-op behavior.

### Full Regression Suite

Command:

```text
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
283 tests passed
```

The previous 279-test suite remains passing; the new total includes four
focused library-discovery tests.

### Application Startup Smoke Test

Command:

```text
.venv/bin/python main.py
```

Observed:

- the prior `librtlsdr` import error did not occur;
- the process remained active;
- `librtlsdr` detected the Rafael Micro R820T-compatible tuner; and
- the application reached live receiver execution.

Terminal output included the existing tuner PLL warning:

```text
Found Rafael Micro R820T tuner
[R82XX] PLL not locked!
```

This warning is emitted by the receiver library and is separate from the
corrected dynamic-library discovery failure.

The rendered receiver-status card requires operator visual confirmation
because it is not observable from the terminal-only verification channel.

## Release Assessment

The macOS dynamic-library startup blocker is corrected. The documented
launch path now discovers the installed Homebrew `librtlsdr` without a
manual shell-level `DYLD_LIBRARY_PATH` setting. Cross-platform behavior and
all production algorithms remain unchanged.
