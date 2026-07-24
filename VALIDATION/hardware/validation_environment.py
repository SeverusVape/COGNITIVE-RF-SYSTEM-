"""Safe environment metadata helpers for hardware-validation evidence."""

from pathlib import Path
import subprocess


def get_git_commit_sha(
        repository_path=None,
        timeout_seconds=1.0
):
    """Return the checked-out commit SHA or ``"unknown"``.

    Git metadata is supporting evidence only. Session creation must continue
    when Git is unavailable, the working directory is not a repository, or
    the command does not finish promptly.
    """
    working_directory = (
        Path(repository_path)
        if repository_path is not None
        else Path.cwd()
    )

    try:
        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "HEAD"
            ],
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False
        )
    except (
            OSError,
            subprocess.SubprocessError
    ):
        return "unknown"

    commit_sha = result.stdout.strip()

    if (
            result.returncode != 0
            or len(commit_sha) != 40
            or any(
                character not in "0123456789abcdefABCDEF"
                for character in commit_sha
            )
    ):
        return "unknown"

    return commit_sha.lower()
