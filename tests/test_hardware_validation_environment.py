from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest.mock import patch

from VALIDATION.hardware.validation_environment import (
    get_git_commit_sha,
)


class HardwareValidationEnvironmentTests(unittest.TestCase):

    @patch(
        "VALIDATION.hardware.validation_environment.subprocess.run"
    )
    def test_successful_git_sha_retrieval(self, run_mock):
        commit_sha = "a" * 40
        run_mock.return_value = CompletedProcess(
            args=[],
            returncode=0,
            stdout=commit_sha + "\n",
            stderr=""
        )

        self.assertEqual(
            get_git_commit_sha(
                repository_path=Path("/project")
            ),
            commit_sha
        )
        self.assertEqual(
            run_mock.call_args.kwargs["timeout"],
            1.0
        )

    @patch(
        "VALIDATION.hardware.validation_environment.subprocess.run",
        side_effect=FileNotFoundError("git unavailable")
    )
    def test_git_unavailable_returns_unknown(self, _run_mock):
        self.assertEqual(
            get_git_commit_sha(),
            "unknown"
        )

    def test_non_repository_directory_returns_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(
                get_git_commit_sha(
                    repository_path=temp_dir
                ),
                "unknown"
            )


if __name__ == "__main__":
    unittest.main()
