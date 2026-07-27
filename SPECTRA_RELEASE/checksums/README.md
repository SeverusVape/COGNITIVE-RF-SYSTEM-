# Release Checksum Preparation

Checksums must be generated only after the corresponding archives are final.
Use SHA-256.

## Expected Records

| Future record | Target |
|---|---|
| `release_archive.sha256` | Complete `SPECTRA_RELEASE` archive |
| `validation_archive.sha256` | Curated validation archive |
| `iq_datasets.sha256` | Separately archived REAL-RF IQ datasets |

## Example Commands

```bash
shasum -a 256 SPECTRA_RELEASE-1.0.0-rc.1.tar.gz \
  > release_archive.sha256

shasum -a 256 SPECTRA-validation-1.0.0-rc.1.tar.gz \
  > validation_archive.sha256

shasum -a 256 SPECTRA-real-rf-iq-datasets.tar.gz \
  > iq_datasets.sha256
```

Each checksum file should contain the archive filename and digest. Do not
record a directory checksum or a checksum for an archive that may still
change.

The IQ dataset archive must remain separate from the primary release archive.
