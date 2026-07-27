# Source Manifest

## Authoritative Source

The complete SPECTRA source tree is defined by Git commit:

```text
b52f77e
```

This package intentionally does not duplicate the full Python tree. Use the
repository and verified commit to reproduce the exact source:

```bash
git checkout b52f77e
```

An archival source bundle may be produced without repository history:

```bash
git archive \
  --format=tar.gz \
  --output=SPECTRA-source-b52f77e.tar.gz \
  b52f77e
```

Record the resulting SHA-256 value in `../checksums/` when the archive is
finalized.

## Included Convenience Copies

| File | Repository source |
|---|---|
| `README.md` | `README.md` |
| `requirements.txt` | `requirements.txt` |
| `ENVIRONMENT_CONFIGURATION.md` | `docs/ENVIRONMENT_CONFIGURATION.md` |

These copies support review and setup. The Git commit remains authoritative
if a copied document differs from the repository.

## Exclusions

- `.git/` history
- `.venv/`
- Python caches
- local logs
- local REAL-RF IQ datasets
- generated report directories
- temporary inspection artifacts
