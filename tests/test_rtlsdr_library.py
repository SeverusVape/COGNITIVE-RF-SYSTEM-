import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from SDR.rtlsdr_library import (
    librtlsdr_import_environment
)


class RtlSdrLibraryDiscoveryTests(unittest.TestCase):

    def test_macos_adds_existing_homebrew_library_directory(self):
        with TemporaryDirectory() as directory:
            library_directory = Path(directory)
            (
                library_directory
                / "librtlsdr.dylib"
            ).touch()

            with patch(
                    "SDR.rtlsdr_library.sys.platform",
                    "darwin"
            ), patch(
                    "SDR.rtlsdr_library."
                    "MACOS_HOMEBREW_LIBRARY_DIRECTORIES",
                    (library_directory,)
            ), patch.dict(
                    os.environ,
                    {},
                    clear=True
            ):
                with librtlsdr_import_environment():
                    self.assertEqual(
                        os.environ["DYLD_LIBRARY_PATH"],
                        str(library_directory)
                    )

                self.assertNotIn(
                    "DYLD_LIBRARY_PATH",
                    os.environ
                )

    def test_macos_preserves_and_restores_existing_path(self):
        with TemporaryDirectory() as directory:
            library_directory = Path(directory)
            (
                library_directory
                / "librtlsdr.dylib"
            ).touch()

            original_path = "/existing/library/path"

            with patch(
                    "SDR.rtlsdr_library.sys.platform",
                    "darwin"
            ), patch(
                    "SDR.rtlsdr_library."
                    "MACOS_HOMEBREW_LIBRARY_DIRECTORIES",
                    (library_directory,)
            ), patch.dict(
                    os.environ,
                    {
                        "DYLD_LIBRARY_PATH": original_path
                    },
                    clear=True
            ):
                with librtlsdr_import_environment():
                    self.assertEqual(
                        os.environ[
                            "DYLD_LIBRARY_PATH"
                        ].split(os.pathsep),
                        [
                            str(library_directory),
                            original_path
                        ]
                    )

                self.assertEqual(
                    os.environ["DYLD_LIBRARY_PATH"],
                    original_path
                )

    def test_missing_macos_library_does_not_change_environment(self):
        with TemporaryDirectory() as directory:
            missing_directory = Path(directory)

            with patch(
                    "SDR.rtlsdr_library.sys.platform",
                    "darwin"
            ), patch(
                    "SDR.rtlsdr_library."
                    "MACOS_HOMEBREW_LIBRARY_DIRECTORIES",
                    (missing_directory,)
            ), patch.dict(
                    os.environ,
                    {},
                    clear=True
            ):
                with librtlsdr_import_environment():
                    self.assertNotIn(
                        "DYLD_LIBRARY_PATH",
                        os.environ
                    )

    def test_non_macos_platform_does_not_change_environment(self):
        original_path = "/system/library/path"

        with patch(
                "SDR.rtlsdr_library.sys.platform",
                "linux"
        ), patch.dict(
                os.environ,
                {
                    "DYLD_LIBRARY_PATH": original_path
                },
                clear=True
        ):
            with librtlsdr_import_environment():
                self.assertEqual(
                    os.environ["DYLD_LIBRARY_PATH"],
                    original_path
                )

            self.assertEqual(
                os.environ["DYLD_LIBRARY_PATH"],
                original_path
            )


if __name__ == "__main__":
    unittest.main()
