# SPECTRA Environment Freeze Report

## 1. Environment Captured

The final release environment was inspected directly from the working SPECTRA
virtual environment and host system. Repository imports, existing installation
instructions, virtual-environment metadata, Python distributions, and RTL-SDR
system libraries were reviewed before creating the dependency manifest.

Reference platform:

```text
macOS 26.5.2
Apple Silicon arm64
RTL-SDR Blog V3
librtlsdr 2.0.2
libusb 1.0.29
```

## 2. Python Version

```text
CPython 3.10.11
```

The inspected interpreter was the project-local `.venv/bin/python`. The
environment does not inherit system site packages.

## 3. Dependency Freeze

The exact required package set is stored in the repository-root
`requirements.txt`.

Runtime packages:

- NumPy 2.2.6
- SciPy 1.15.3
- PyQt6 6.11.0
- PyQt6-Qt6 6.11.1
- PyQt6-sip 13.11.1
- pyqtgraph 0.14.0
- colorama 0.4.6
- pyrtlsdr 0.2.93

Development/validation packages:

- Matplotlib 3.10.9
- contourpy 1.3.2
- cycler 0.12.1
- fonttools 4.63.0
- kiwisolver 1.5.0
- packaging 26.2
- Pillow 12.2.0
- pyparsing 3.3.2
- python-dateutil 2.9.0.post0
- six 1.17.0

Installed packages unrelated to application execution, automated tests, or
validation report generation were excluded.

## 4. Files Created or Modified

Created:

- `requirements.txt`
- `docs/ENVIRONMENT_CONFIGURATION.md`
- `docs/ENVIRONMENT_FREEZE_REPORT.md`

Modified:

- `README.md` — installation now references the pinned manifest and detailed
  environment document.

## 5. Verification

Verification was performed on 2026-07-27 using the captured project virtual
environment. Package metadata passed `pip check`, both standalone REAL-RF
command interfaces loaded successfully, and the complete hardware-independent
regression suite reported:

```text
Ran 279 tests in 0.448s
OK
```

The repeatable release verification procedure is:

```bash
source .venv/bin/activate
python --version
python -m unittest discover -s tests -v
python -m VALIDATION.real_rf.capture --help
python -m VALIDATION.real_rf.comparison --help
```

Expected regression result:

```text
Ran 279 tests
OK
```

Final repository checks for this phase include:

```bash
git diff --check
git status --short
```

## 6. Scope Confirmation

This environment-freeze phase changes release metadata and documentation only.
No Python source code, detector setting, algorithm, validation dataset, or
generated validation result is changed or regenerated.

## 7. Remaining Reproducibility Limits

- `librtlsdr` and USB installation remain operating-system-specific.
- The manifest pins versions but does not include platform-specific package
  hashes.
- Live RF observations cannot be reproduced exactly because the RF environment
  changes with time, placement, propagation, and interference.
- Large immutable IQ datasets remain outside normal source-control history and
  require separate checksum-controlled archival storage.
