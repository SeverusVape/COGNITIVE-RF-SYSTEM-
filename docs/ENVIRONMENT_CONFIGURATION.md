# SPECTRA Environment Configuration

## 1. Verified Platform

The final release environment was captured on:

| Component | Verified value |
| --- | --- |
| Operating system | macOS 26.5.2 |
| Architecture | Apple Silicon (`arm64`) |
| Python implementation | CPython |
| Python version | 3.10.11 |
| Receiver | RTL-SDR Blog V3, RTL2832U/R860, 1 ppm TCXO |
| System RTL-SDR library | Homebrew `librtlsdr 2.0.2` |
| USB library | Homebrew `libusb 1.0.29` |

This is the verified senior-design release platform. The Python packages and
RTL-SDR libraries are portable in principle, but Linux and Windows have not
received the same final release qualification.

## 2. Python Environment

Create an isolated virtual environment with CPython 3.10.11:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The captured project environment was created with `virtualenv 20.38.0` and
does not include system site packages. A standard-library `venv` environment
is suitable for release installation.

## 3. Required Python Packages

### Runtime

| Package | Version | Purpose |
| --- | ---: | --- |
| NumPy | 2.2.6 | IQ arrays, FFT processing, numerical measurement |
| SciPy | 1.15.3 | Peak detection and local percentile filtering |
| PyQt6 | 6.11.0 | Application GUI and threaded Qt signaling |
| PyQt6-Qt6 | 6.11.1 | Qt runtime supplied for PyQt6 |
| PyQt6-sip | 13.11.1 | PyQt6 binding support |
| pyqtgraph | 0.14.0 | FFT, waterfall, and heatmap plots |
| colorama | 0.4.6 | pyqtgraph runtime dependency |
| pyrtlsdr | 0.2.93 | Python access to RTL-SDR hardware |

### Development and validation

The regression suite uses Python's standard-library `unittest`; pytest is not
required. Matplotlib 3.10.9 and its pinned dependencies are required only for
the committed validation scripts that generate engineering plots and reports.
All resolved versions are listed in `requirements.txt`.

## 4. SDR System Dependencies

Live operation requires:

- one RTL-SDR-compatible USB receiver;
- `librtlsdr`;
- the USB backend used by `librtlsdr` (`libusb` on the verified platform);
- an antenna appropriate for the observed frequency range; and
- exclusive access to the receiver.

Install the verified macOS system dependency with Homebrew:

```bash
brew install librtlsdr
```

The verified Apple Silicon installation uses:

```text
/opt/homebrew/opt/librtlsdr/lib
```

Intel Homebrew commonly uses:

```text
/usr/local/opt/librtlsdr/lib
```

The standalone REAL-RF capture utility discovers these standard macOS
locations without requiring the operator to set `DYLD_LIBRARY_PATH`.

Only one process may own the RTL-SDR. Stop `rtl_test`, SDR++, GQRX, GNU Radio,
and other receiver software before starting SPECTRA or a REAL-RF capture.

## 5. Installation Procedure

From the repository root:

```bash
brew install librtlsdr
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Confirm that the receiver is visible:

```bash
rtl_test -t
```

Stop `rtl_test` before launching SPECTRA:

```bash
python main.py
```

## 6. Verification Procedure

Activate the environment:

```bash
source .venv/bin/activate
```

Verify the Python version:

```bash
python --version
```

Expected:

```text
Python 3.10.11
```

Run the complete hardware-independent regression suite:

```bash
python -m unittest discover -s tests -v
```

Expected release result:

```text
Ran 283 tests
OK
```

Verify the standalone REAL-RF command interfaces:

```bash
python -m VALIDATION.real_rf.capture --help
python -m VALIDATION.real_rf.comparison --help
```

Live capture requires the receiver. Test execution and deterministic replay do
not require connected hardware.

## 7. Known Environment Limitations

- Live spectrum acquisition requires compatible RTL-SDR hardware.
- USB behavior, device permissions, and dynamic-library discovery differ by
  operating system.
- The final release was verified on Apple Silicon macOS; other platforms
  require separate installation verification.
- The receiver must not be open in another process.
- `librtlsdr` may report the compatible R820T tuner family for an R860-based
  RTL-SDR Blog V3.
- Displayed FFT values are relative dB, not calibrated dBm.
- Antenna, placement, propagation, front-end behavior, gain, and local
  interference affect live measurements.
- The pinned manifest reproduces the verified package set but does not provide
  platform-specific wheel hashes.
