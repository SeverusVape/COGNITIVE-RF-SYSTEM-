"""Standalone RTL-SDR capture utility for immutable real-RF datasets."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import sys
from time import perf_counter
from uuid import uuid4

import numpy as np

from UTILS.config import (
    CENTER_FREQ,
    GAIN,
    MAX_CENTER_FREQ_MHZ,
    MIN_CENTER_FREQ_MHZ,
    NUM_SAMPLES,
    SAMPLE_RATE,
)
from VALIDATION.real_rf.dataset import create_dataset


DEFAULT_DATASET_ROOT = (
    Path(__file__).resolve().parent
    / "datasets"
)

MACOS_HOMEBREW_LIBRARY_DIRECTORIES = (
    Path("/opt/homebrew/opt/librtlsdr/lib"),
    Path("/usr/local/opt/librtlsdr/lib"),
)


def _load_sdr_manager():
    """Load the production SDR manager with Homebrew discovery on macOS."""

    original_library_path = os.environ.get(
        "DYLD_LIBRARY_PATH"
    )

    if sys.platform == "darwin":
        existing_directories = [
            str(directory)
            for directory in MACOS_HOMEBREW_LIBRARY_DIRECTORIES
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
            combined_directories = list(
                dict.fromkeys(
                    existing_directories
                    + current_directories
                )
            )
            os.environ["DYLD_LIBRARY_PATH"] = (
                os.pathsep.join(
                    combined_directories
                )
            )

    try:
        from SDR.sdr_manager import SDRManager

        return SDRManager
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


def generate_dataset_id(timestamp=None):
    """Generate a filesystem-safe, collision-resistant dataset ID."""

    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    return (
        "RF-"
        + timestamp.strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid4().hex[:8]
    )


def parse_gain(value):
    """Accept the production ``auto`` mode or a numeric gain in dB."""

    if isinstance(value, str) and value.strip().lower() == "auto":
        return "auto"

    try:
        gain = float(value)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            "Gain must be 'auto' or a finite numeric value."
        ) from error

    if not np.isfinite(gain):
        raise argparse.ArgumentTypeError(
            "Gain must be 'auto' or a finite numeric value."
        )

    return gain


def capture_dataset(
        output_root,
        *,
        dataset_id,
        scenario,
        notes,
        center_frequency_hz,
        sample_rate_hz,
        gain,
        frame_count,
        iq_samples_per_frame,
        manager_factory=None
):
    """Capture complete IQ frames and persist them only after success."""

    if (
            isinstance(frame_count, bool)
            or not isinstance(frame_count, int)
            or frame_count < 1
    ):
        raise ValueError("Frame count must be a positive integer.")

    if (
            isinstance(iq_samples_per_frame, bool)
            or not isinstance(iq_samples_per_frame, int)
            or iq_samples_per_frame < 2
    ):
        raise ValueError(
            "IQ samples per frame must be an integer of at least two."
        )

    center_frequency_hz = float(center_frequency_hz)
    sample_rate_hz = float(sample_rate_hz)

    if (
            not np.isfinite(center_frequency_hz)
            or center_frequency_hz <= 0
    ):
        raise ValueError(
            "Center frequency must be finite and positive."
        )

    if (
            not np.isfinite(sample_rate_hz)
            or sample_rate_hz <= 0
    ):
        raise ValueError(
            "Sample rate must be finite and positive."
        )

    if manager_factory is None:
        manager_factory = _load_sdr_manager()

    manager = manager_factory(
        sample_rate_hz,
        center_frequency_hz,
        gain
    )

    started = perf_counter()

    try:
        if not manager.connected:
            raise RuntimeError(
                "RTL-SDR connection failed; no dataset was created."
            )

        frames = np.empty(
            (
                frame_count,
                iq_samples_per_frame
            ),
            dtype=np.complex64
        )

        for frame_index in range(frame_count):
            samples = manager.read_samples(
                iq_samples_per_frame
            )

            if samples is None:
                raise RuntimeError(
                    "RTL-SDR sample acquisition failed; "
                    "no dataset was created."
                )

            samples = np.asarray(samples)

            if (
                    samples.ndim != 1
                    or len(samples) != iq_samples_per_frame
                    or not np.issubdtype(
                        samples.dtype,
                        np.complexfloating
                    )
                    or not np.all(np.isfinite(samples))
            ):
                raise RuntimeError(
                    "RTL-SDR returned an invalid IQ frame; "
                    "no dataset was created."
                )

            frames[frame_index] = samples

        duration_seconds = perf_counter() - started

        return create_dataset(
            output_root,
            dataset_id=dataset_id,
            scenario=scenario,
            notes=notes,
            center_frequency_hz=center_frequency_hz,
            sample_rate_hz=sample_rate_hz,
            gain=gain,
            iq_frames=frames,
            capture_duration_seconds=duration_seconds
        )
    finally:
        manager.close()


def build_argument_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Capture an immutable real-RF IQ dataset for offline "
            "detector comparison."
        )
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_DATASET_ROOT
    )
    parser.add_argument("--dataset-id")
    parser.add_argument(
        "--scenario",
        required=True
    )
    parser.add_argument(
        "--notes",
        default=""
    )
    parser.add_argument(
        "--center-mhz",
        type=float,
        default=CENTER_FREQ / 1e6
    )
    parser.add_argument(
        "--sample-rate",
        type=float,
        default=SAMPLE_RATE
    )
    parser.add_argument(
        "--gain",
        type=parse_gain,
        default=GAIN
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=100
    )
    parser.add_argument(
        "--samples-per-frame",
        type=int,
        default=NUM_SAMPLES
    )
    return parser


def main(argv=None):
    parser = build_argument_parser()
    arguments = parser.parse_args(argv)

    if not (
            MIN_CENTER_FREQ_MHZ
            <= arguments.center_mhz
            <= MAX_CENTER_FREQ_MHZ
    ):
        parser.error(
            "Center frequency must be between "
            f"{MIN_CENTER_FREQ_MHZ} and "
            f"{MAX_CENTER_FREQ_MHZ} MHz."
        )

    dataset = capture_dataset(
        arguments.output_root,
        dataset_id=(
            arguments.dataset_id
            or generate_dataset_id()
        ),
        scenario=arguments.scenario,
        notes=arguments.notes,
        center_frequency_hz=arguments.center_mhz * 1e6,
        sample_rate_hz=arguments.sample_rate,
        gain=arguments.gain,
        frame_count=arguments.frames,
        iq_samples_per_frame=arguments.samples_per_frame
    )

    metadata = dataset.metadata

    print("REAL-RF CAPTURE COMPLETE")
    print(f"Dataset: {metadata.dataset_id}")
    print(f"Directory: {dataset.path}")
    print(
        "Center: "
        f"{metadata.center_frequency_hz / 1e6:.6f} MHz"
    )
    print(
        f"Frames: {metadata.frame_count} × "
        f"{metadata.iq_samples_per_frame} IQ samples"
    )
    print(
        f"Duration: {metadata.capture_duration_seconds:.3f} s"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
