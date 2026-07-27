"""Platform-safe runtime discovery for the RTL-SDR system library."""

from contextlib import contextmanager
import os
from pathlib import Path
import sys


MACOS_HOMEBREW_LIBRARY_DIRECTORIES = (
    Path("/opt/homebrew/opt/librtlsdr/lib"),
    Path("/usr/local/opt/librtlsdr/lib"),
)


@contextmanager
def librtlsdr_import_environment():
    """Expose Homebrew ``librtlsdr`` while importing pyrtlsdr on macOS.

    Linux and Windows retain their normal system library discovery. The
    caller's original ``DYLD_LIBRARY_PATH`` is restored after the import.
    """

    original_library_path = os.environ.get(
        "DYLD_LIBRARY_PATH"
    )

    if sys.platform == "darwin":
        existing_directories = [
            str(directory)
            for directory
            in MACOS_HOMEBREW_LIBRARY_DIRECTORIES
            if (directory / "librtlsdr.dylib").is_file()
        ]

        if existing_directories:
            current_directories = [
                value
                for value in (
                    original_library_path or ""
                ).split(os.pathsep)
                if value
            ]

            os.environ["DYLD_LIBRARY_PATH"] = (
                os.pathsep.join(
                    dict.fromkeys(
                        existing_directories
                        + current_directories
                    )
                )
            )

    try:
        yield
    finally:
        if original_library_path is None:
            os.environ.pop(
                "DYLD_LIBRARY_PATH",
                None
            )
        else:
            os.environ["DYLD_LIBRARY_PATH"] = (
                original_library_path
            )
