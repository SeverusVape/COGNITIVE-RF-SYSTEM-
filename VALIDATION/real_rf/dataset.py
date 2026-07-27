"""Immutable real-RF dataset storage and deterministic FFT replay."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from typing import Any, Iterator

import numpy as np

from SDR.fft_processing import compute_windowed_fft
from UTILS.frequency_axis import build_frequency_axis


DATASET_SCHEMA_VERSION = "1.0"
METADATA_FILENAME = "metadata.json"
SAMPLES_FILENAME = "samples.npy"
DETECTOR_INPUT_TYPE = "complex_iq_frames"
PREPROCESSING_NAME = "compute_windowed_fft"
WINDOW_NAME = "hann_coherent_gain_compensated"
SAFE_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
)


def _finite_number(name, value, *, positive=False):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number.")

    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{name} must be a finite number."
        ) from error

    if (
            not math.isfinite(numeric_value)
            or (positive and numeric_value <= 0)
    ):
        requirement = "finite and positive" if positive else "finite"
        raise ValueError(f"{name} must be {requirement}.")

    return numeric_value


def _positive_integer(name, value):
    if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 1
    ):
        raise ValueError(f"{name} must be a positive integer.")

    return value


def _required_text(name, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text.")

    return value.strip()


def validate_identifier(name, value):
    value = _required_text(name, value)

    if (
            value in {".", ".."}
            or SAFE_IDENTIFIER_PATTERN.fullmatch(value) is None
    ):
        raise ValueError(
            f"{name} may contain only letters, numbers, '.', '_', "
            "and '-', and must start with a letter or number."
        )

    return value


@dataclass(frozen=True)
class RealRFDatasetMetadata:
    """Metadata required to reproduce detector input from recorded IQ."""

    schema_version: str
    dataset_id: str
    timestamp_utc: str
    scenario: str
    notes: str
    center_frequency_hz: float
    sample_rate_hz: float
    gain: str | float
    iq_samples_per_frame: int
    fft_size: int
    frame_count: int
    sample_count: int
    capture_duration_seconds: float
    detector_input_type: str
    preprocessing: str
    window: str
    array_file: str
    array_dtype: str
    array_shape: tuple[int, int]

    def __post_init__(self):
        if self.schema_version != DATASET_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported dataset schema: {self.schema_version!r}."
            )

        validate_identifier("Dataset ID", self.dataset_id)
        _required_text("Timestamp", self.timestamp_utc)
        _required_text("Scenario", self.scenario)

        if not isinstance(self.notes, str):
            raise ValueError("Notes must be text.")

        _finite_number(
            "Center frequency",
            self.center_frequency_hz,
            positive=True
        )
        _finite_number(
            "Sample rate",
            self.sample_rate_hz,
            positive=True
        )

        if (
                isinstance(self.gain, str)
                and not self.gain.strip()
        ):
            raise ValueError("Gain text must not be empty.")

        if not isinstance(self.gain, str):
            _finite_number("Gain", self.gain)

        _positive_integer(
            "IQ samples per frame",
            self.iq_samples_per_frame
        )
        _positive_integer("FFT size", self.fft_size)
        _positive_integer("Frame count", self.frame_count)
        _positive_integer("Sample count", self.sample_count)
        _finite_number(
            "Capture duration",
            self.capture_duration_seconds,
            positive=True
        )

        if self.fft_size != self.iq_samples_per_frame:
            raise ValueError(
                "Current replay requires FFT size to equal IQ samples "
                "per frame."
            )

        expected_sample_count = (
            self.frame_count
            * self.iq_samples_per_frame
        )

        if self.sample_count != expected_sample_count:
            raise ValueError(
                "Sample count does not match frame count and frame size."
            )

        if self.detector_input_type != DETECTOR_INPUT_TYPE:
            raise ValueError(
                "Unsupported detector input type."
            )

        if self.preprocessing != PREPROCESSING_NAME:
            raise ValueError("Unsupported FFT preprocessing.")

        if self.window != WINDOW_NAME:
            raise ValueError("Unsupported FFT window.")

        if self.array_file != SAMPLES_FILENAME:
            raise ValueError("Unsupported IQ array filename.")

        if not isinstance(self.array_shape, tuple):
            raise ValueError("Array shape must be a two-value tuple.")

        if self.array_shape != (
                self.frame_count,
                self.iq_samples_per_frame
        ):
            raise ValueError(
                "Array shape does not match dataset dimensions."
            )

        try:
            dtype = np.dtype(self.array_dtype)
        except TypeError as error:
            raise ValueError("Array dtype is invalid.") from error

        if not np.issubdtype(dtype, np.complexfloating):
            raise ValueError("IQ array dtype must be complex.")

    def to_dict(self):
        payload = asdict(self)
        payload["array_shape"] = list(self.array_shape)
        return payload

    @classmethod
    def from_dict(cls, payload):
        if not isinstance(payload, dict):
            raise TypeError("Dataset metadata must be a dictionary.")

        expected_fields = set(cls.__dataclass_fields__)
        supplied_fields = set(payload)

        if supplied_fields != expected_fields:
            missing = sorted(expected_fields - supplied_fields)
            extra = sorted(supplied_fields - expected_fields)
            raise ValueError(
                "Dataset metadata fields do not match the schema. "
                f"Missing: {missing}; extra: {extra}."
            )

        normalized = dict(payload)

        array_shape = normalized["array_shape"]

        if (
                not isinstance(array_shape, (list, tuple))
                or len(array_shape) != 2
        ):
            raise ValueError(
                "Array shape must contain frame and sample dimensions."
            )

        normalized["array_shape"] = tuple(array_shape)

        return cls(**normalized)


@dataclass(frozen=True)
class ReplayFrame:
    """One immutable detector input reconstructed from recorded IQ."""

    frame_index: int
    iq_samples: np.ndarray
    power_db: np.ndarray
    freqs_mhz: np.ndarray


@dataclass(frozen=True)
class RealRFDataset:
    """Validated immutable dataset loaded from one dataset directory."""

    path: Path
    metadata: RealRFDatasetMetadata
    iq_frames: np.ndarray

    def replay(self) -> Iterator[ReplayFrame]:
        """Yield deterministic, read-only FFT detector inputs."""

        _, freqs_mhz = build_frequency_axis(
            self.metadata.fft_size,
            self.metadata.sample_rate_hz,
            self.metadata.center_frequency_hz
        )
        freqs_mhz.setflags(write=False)

        for frame_index in range(self.metadata.frame_count):
            iq_samples = np.asarray(
                self.iq_frames[frame_index]
            )
            iq_samples.setflags(write=False)

            power_db = np.asarray(
                compute_windowed_fft(iq_samples),
                dtype=float
            )
            power_db.setflags(write=False)

            yield ReplayFrame(
                frame_index=frame_index,
                iq_samples=iq_samples,
                power_db=power_db,
                freqs_mhz=freqs_mhz
            )


def build_metadata(
        *,
        dataset_id,
        scenario,
        notes,
        center_frequency_hz,
        sample_rate_hz,
        gain,
        iq_frames,
        capture_duration_seconds,
        timestamp_utc=None
):
    """Build validated metadata for a two-dimensional complex IQ array."""

    frames = np.asarray(iq_frames)

    if frames.ndim != 2:
        raise ValueError(
            "IQ samples must be a two-dimensional frame array."
        )

    if not np.issubdtype(frames.dtype, np.complexfloating):
        raise ValueError("IQ samples must use a complex dtype.")

    if frames.shape[0] < 1 or frames.shape[1] < 2:
        raise ValueError(
            "IQ samples require at least one frame with two samples."
        )

    if not np.all(np.isfinite(frames)):
        raise ValueError("IQ samples must be finite.")

    if timestamp_utc is None:
        timestamp_utc = datetime.now(timezone.utc).isoformat()

    frame_count, samples_per_frame = frames.shape

    return RealRFDatasetMetadata(
        schema_version=DATASET_SCHEMA_VERSION,
        dataset_id=str(dataset_id),
        timestamp_utc=str(timestamp_utc),
        scenario=str(scenario),
        notes=str(notes),
        center_frequency_hz=float(center_frequency_hz),
        sample_rate_hz=float(sample_rate_hz),
        gain=gain,
        iq_samples_per_frame=int(samples_per_frame),
        fft_size=int(samples_per_frame),
        frame_count=int(frame_count),
        sample_count=int(frames.size),
        capture_duration_seconds=float(capture_duration_seconds),
        detector_input_type=DETECTOR_INPUT_TYPE,
        preprocessing=PREPROCESSING_NAME,
        window=WINDOW_NAME,
        array_file=SAMPLES_FILENAME,
        array_dtype=str(frames.dtype),
        array_shape=(
            int(frame_count),
            int(samples_per_frame)
        )
    )


def create_dataset(
        root_directory,
        *,
        dataset_id,
        scenario,
        notes,
        center_frequency_hz,
        sample_rate_hz,
        gain,
        iq_frames,
        capture_duration_seconds,
        timestamp_utc=None
):
    """Create one collision-safe dataset directory."""

    root_directory = Path(root_directory)
    dataset_id = validate_identifier("Dataset ID", dataset_id)
    dataset_directory = root_directory / dataset_id

    if dataset_directory.exists():
        raise FileExistsError(
            f"Dataset already exists: {dataset_directory}"
        )

    frames = np.asarray(iq_frames)
    metadata = build_metadata(
        dataset_id=dataset_id,
        scenario=scenario,
        notes=notes,
        center_frequency_hz=center_frequency_hz,
        sample_rate_hz=sample_rate_hz,
        gain=gain,
        iq_frames=frames,
        capture_duration_seconds=capture_duration_seconds,
        timestamp_utc=timestamp_utc
    )

    root_directory.mkdir(
        parents=True,
        exist_ok=True
    )
    dataset_directory.mkdir()

    try:
        np.save(
            dataset_directory / SAMPLES_FILENAME,
            frames,
            allow_pickle=False
        )
        (
            dataset_directory
            / METADATA_FILENAME
        ).write_text(
            json.dumps(
                metadata.to_dict(),
                indent=2,
                sort_keys=True
            )
            + "\n",
            encoding="utf-8"
        )
    except Exception:
        for child in dataset_directory.iterdir():
            child.unlink()
        dataset_directory.rmdir()
        raise

    return load_dataset(dataset_directory)


def load_dataset(dataset_directory):
    """Load and validate a dataset without granting write access."""

    dataset_directory = Path(dataset_directory)
    metadata_path = dataset_directory / METADATA_FILENAME
    samples_path = dataset_directory / SAMPLES_FILENAME

    if not metadata_path.is_file():
        raise FileNotFoundError(
            f"Dataset metadata is missing: {metadata_path}"
        )

    if not samples_path.is_file():
        raise FileNotFoundError(
            f"Dataset IQ samples are missing: {samples_path}"
        )

    try:
        payload: Any = json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Dataset metadata is not valid JSON."
        ) from error

    metadata = RealRFDatasetMetadata.from_dict(payload)

    iq_frames = np.load(
        samples_path,
        mmap_mode="r",
        allow_pickle=False
    )

    if iq_frames.ndim != 2:
        raise ValueError("Stored IQ array must be two-dimensional.")

    if iq_frames.shape != metadata.array_shape:
        raise ValueError(
            "Stored IQ array shape does not match metadata."
        )

    if str(iq_frames.dtype) != metadata.array_dtype:
        raise ValueError(
            "Stored IQ array dtype does not match metadata."
        )

    if not np.issubdtype(
            iq_frames.dtype,
            np.complexfloating
    ):
        raise ValueError("Stored IQ array must use a complex dtype.")

    if not np.all(np.isfinite(iq_frames)):
        raise ValueError("Stored IQ array contains non-finite values.")

    iq_frames.setflags(write=False)

    return RealRFDataset(
        path=dataset_directory,
        metadata=metadata,
        iq_frames=iq_frames
    )
