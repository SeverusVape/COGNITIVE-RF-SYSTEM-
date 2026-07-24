"""Shared deterministic detector-evaluation support for SPECTRA.

This module belongs to the validation environment. It does not select,
configure, or execute a detector in the production application.
"""

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

import numpy as np

from SDR.detection import (
    detect_peaks as detect_adaptive_peaks
)
from SDR.fft_processing import compute_windowed_fft
from SDR.os_cfar import (
    OSCFARConfig,
    detect_peaks as detect_os_cfar_peaks
)
from UTILS.config import (
    NUM_SAMPLES,
    SAMPLE_RATE
)


REQUIRED_SCENARIOS = (
    "noise_only",
    "single_carrier",
    "weak_beside_strong",
    "multiple_carriers",
    "fft_edge",
    "closely_spaced_carriers",
    "variable_noise_floor",
    "monte_carlo"
)


@dataclass(frozen=True)
class DetectorAdapter:
    name: str
    callback: Callable


@dataclass(frozen=True)
class SyntheticTrial:
    scenario: str
    trial_index: int
    random_seed: int
    power_db: np.ndarray
    freqs_mhz: np.ndarray
    expected_frequencies_mhz: tuple[float, ...]


@dataclass(frozen=True)
class TrialResult:
    detector: str
    scenario: str
    trial_index: int
    random_seed: int
    expected_count: int
    detected_count: int
    true_positive_count: int
    false_positive_count: int
    false_negative_count: int
    frame_has_false_alarm: bool
    frequency_errors_hz: tuple[float, ...]
    runtime_ms: float
    finite_threshold_median_db: float


def build_detector_adapters(
        os_cfar_config=None
):
    """Return both detectors behind the same validation-only interface."""

    if os_cfar_config is None:
        os_cfar_config = OSCFARConfig()

    def run_os_cfar(
            power_db,
            freqs_mhz
    ):
        return detect_os_cfar_peaks(
            power_db,
            freqs_mhz,
            config=os_cfar_config
        )

    return (
        DetectorAdapter(
            name="adaptive",
            callback=detect_adaptive_peaks
        ),
        DetectorAdapter(
            name="os_cfar",
            callback=run_os_cfar
        )
    )


def _frequency_axis_mhz(
        sample_rate,
        fft_size
):
    return (
        np.fft.fftshift(
            np.fft.fftfreq(
                fft_size,
                d=1.0 / sample_rate
            )
        )
        / 1e6
    )


def _complex_noise(
        rng,
        fft_size,
        variable_floor=False
):
    if not variable_floor:
        return (
            rng.normal(
                0.0,
                np.sqrt(0.5),
                fft_size
            )
            + 1j
            * rng.normal(
                0.0,
                np.sqrt(0.5),
                fft_size
            )
        )

    spectral_noise = (
        rng.normal(
            0.0,
            np.sqrt(0.5),
            fft_size
        )
        + 1j
        * rng.normal(
            0.0,
            np.sqrt(0.5),
            fft_size
        )
    )

    normalized_frequency = np.linspace(
        -1.0,
        1.0,
        fft_size
    )

    baseline_db = (
        5.0
        * normalized_frequency
        + 3.0
        * np.sin(
            2.0
            * np.pi
            * normalized_frequency
        )
    )

    shaped_spectrum = (
        spectral_noise
        * 10.0 ** (
            baseline_db / 20.0
        )
    )

    return (
        np.fft.ifft(
            np.fft.ifftshift(
                shaped_spectrum
            )
        )
        * np.sqrt(
            fft_size
        )
    )


def _build_spectrum(
        rng,
        tone_definitions,
        sample_rate,
        fft_size,
        variable_floor=False
):
    samples = _complex_noise(
        rng,
        fft_size,
        variable_floor=variable_floor
    )

    sample_indices = np.arange(
        fft_size,
        dtype=float
    )

    for frequency_hz, snr_db in tone_definitions:
        amplitude = np.sqrt(
            10.0 ** (
                snr_db / 10.0
            )
        )

        phase = rng.uniform(
            0.0,
            2.0 * np.pi
        )

        samples = (
            samples
            + amplitude
            * np.exp(
                1j
                * (
                    2.0
                    * np.pi
                    * frequency_hz
                    * sample_indices
                    / sample_rate
                    + phase
                )
            )
        )

    return compute_windowed_fft(
        samples
    )


def _scenario_tones(
        scenario,
        rng
):
    if scenario == "noise_only":
        return ()

    if scenario == "single_carrier":
        return (
            (
                float(
                    rng.uniform(
                        -600_000.0,
                        600_000.0
                    )
                ),
                -18.0
            ),
        )

    if scenario == "weak_beside_strong":
        center = float(
            rng.uniform(
                -500_000.0,
                400_000.0
            )
        )

        return (
            (center, -8.0),
            (center + 100_000.0, -24.0)
        )

    if scenario == "multiple_carriers":
        offset = float(
            rng.uniform(
                -100_000.0,
                100_000.0
            )
        )

        return (
            (-500_000.0 + offset, -12.0),
            (-100_000.0 + offset, -18.0),
            (350_000.0 + offset, -15.0)
        )

    if scenario == "fft_edge":
        side = -1.0 if rng.integers(0, 2) == 0 else 1.0

        return (
            (
                side
                * float(
                    rng.uniform(
                        970_000.0,
                        990_000.0
                    )
                ),
                -12.0
            ),
        )

    if scenario == "closely_spaced_carriers":
        center = float(
            rng.uniform(
                -500_000.0,
                500_000.0
            )
        )

        return (
            (center - 38_000.0, -12.0),
            (center + 38_000.0, -15.0)
        )

    if scenario == "variable_noise_floor":
        return (
            (
                float(
                    rng.uniform(
                        -600_000.0,
                        600_000.0
                    )
                ),
                -16.0
            ),
        )

    if scenario == "monte_carlo":
        tone_count = int(
            rng.integers(
                0,
                4
            )
        )

        if tone_count == 0:
            return ()

        candidate_frequencies = np.linspace(
            -700_000.0,
            700_000.0,
            15
        )

        selected_frequencies = rng.choice(
            candidate_frequencies,
            size=tone_count,
            replace=False
        )

        return tuple(
            (
                float(frequency),
                float(
                    rng.uniform(
                        -26.0,
                        -8.0
                    )
                )
            )
            for frequency in sorted(
                selected_frequencies
            )
        )

    raise ValueError(
        f"Unknown detector-evaluation scenario: {scenario}"
    )


def build_phase3_trials(
        trials_per_scenario=3,
        base_seed=3_102_203,
        sample_rate=float(SAMPLE_RATE),
        fft_size=int(NUM_SAMPLES)
):
    """Build repeatable spectra covering all required Phase 3 scenarios."""

    if (
            isinstance(trials_per_scenario, bool)
            or not isinstance(
                trials_per_scenario,
                int
            )
            or trials_per_scenario < 1
    ):
        raise ValueError(
            "Trials per scenario must be a positive integer."
        )

    if (
            not np.isfinite(sample_rate)
            or sample_rate <= 0
    ):
        raise ValueError(
            "Sample rate must be finite and positive."
        )

    if (
            isinstance(fft_size, bool)
            or not isinstance(fft_size, int)
            or fft_size < 2
    ):
        raise ValueError(
            "FFT size must be an integer greater than one."
        )

    frequency_axis_mhz = _frequency_axis_mhz(
        sample_rate,
        fft_size
    )
    frequency_axis_mhz.setflags(
        write=False
    )

    trials = []
    trial_index = 1

    for scenario_index, scenario in enumerate(
            REQUIRED_SCENARIOS
    ):
        for repetition in range(
                trials_per_scenario
        ):
            seed = (
                base_seed
                + scenario_index
                * 10_000
                + repetition
            )

            rng = np.random.default_rng(
                seed
            )

            tones = _scenario_tones(
                scenario,
                rng
            )

            power_db = _build_spectrum(
                rng,
                tones,
                sample_rate,
                fft_size,
                variable_floor=(
                    scenario
                    == "variable_noise_floor"
                )
            )
            power_db.setflags(
                write=False
            )

            trials.append(
                SyntheticTrial(
                    scenario=scenario,
                    trial_index=trial_index,
                    random_seed=seed,
                    power_db=power_db,
                    freqs_mhz=frequency_axis_mhz,
                    expected_frequencies_mhz=tuple(
                        frequency_hz / 1e6
                        for frequency_hz, _ in tones
                    )
                )
            )

            trial_index += 1

    return tuple(
        trials
    )


def match_detections(
        expected_frequencies_mhz,
        detected_peaks,
        tolerance_hz
):
    """Perform deterministic one-to-one nearest-frequency matching."""

    if (
            not np.isfinite(tolerance_hz)
            or tolerance_hz < 0
    ):
        raise ValueError(
            "Match tolerance must be finite and non-negative."
        )

    expected = tuple(
        float(frequency)
        for frequency in expected_frequencies_mhz
    )

    detected = tuple(
        float(peak[0])
        for peak in detected_peaks
    )

    candidate_pairs = []

    for expected_index, expected_frequency in enumerate(
            expected
    ):
        for detected_index, detected_frequency in enumerate(
                detected
        ):
            error_hz = (
                detected_frequency
                - expected_frequency
            ) * 1e6

            if abs(error_hz) <= tolerance_hz:
                candidate_pairs.append(
                    (
                        abs(error_hz),
                        expected_index,
                        detected_index,
                        error_hz
                    )
                )

    matched_expected = set()
    matched_detected = set()
    frequency_errors_hz = []

    for (
            _,
            expected_index,
            detected_index,
            error_hz
    ) in sorted(
            candidate_pairs
    ):
        if (
                expected_index in matched_expected
                or detected_index in matched_detected
        ):
            continue

        matched_expected.add(
            expected_index
        )

        matched_detected.add(
            detected_index
        )

        frequency_errors_hz.append(
            float(error_hz)
        )

    true_positive_count = len(
        matched_expected
    )

    return {
        "true_positive_count": true_positive_count,
        "false_positive_count": (
            len(detected)
            - true_positive_count
        ),
        "false_negative_count": (
            len(expected)
            - true_positive_count
        ),
        "frequency_errors_hz": tuple(
            frequency_errors_hz
        )
    }


def evaluate_trial(
        trial,
        detector,
        tolerance_hz=None
):
    if not isinstance(
            trial,
            SyntheticTrial
    ):
        raise TypeError(
            "Trial must be a SyntheticTrial instance."
        )

    if not isinstance(
            detector,
            DetectorAdapter
    ):
        raise TypeError(
            "Detector must be a DetectorAdapter instance."
        )

    if tolerance_hz is None:
        tolerance_hz = float(
            np.median(
                np.abs(
                    np.diff(
                        trial.freqs_mhz
                    )
                )
            )
            * 1e6
        )

    start_time = perf_counter()

    peaks, threshold = detector.callback(
        trial.power_db,
        trial.freqs_mhz
    )

    runtime_ms = (
        perf_counter()
        - start_time
    ) * 1000

    threshold = np.asarray(
        threshold,
        dtype=float
    )

    if threshold.shape != trial.power_db.shape:
        raise ValueError(
            "Detector threshold must match the trial spectrum shape."
        )

    finite_threshold = threshold[
        np.isfinite(
            threshold
        )
    ]

    if len(finite_threshold) == 0:
        raise ValueError(
            "Detector threshold must contain finite interior values."
        )

    match = match_detections(
        trial.expected_frequencies_mhz,
        peaks,
        tolerance_hz
    )

    return TrialResult(
        detector=detector.name,
        scenario=trial.scenario,
        trial_index=trial.trial_index,
        random_seed=trial.random_seed,
        expected_count=len(
            trial.expected_frequencies_mhz
        ),
        detected_count=len(
            peaks
        ),
        true_positive_count=match[
            "true_positive_count"
        ],
        false_positive_count=match[
            "false_positive_count"
        ],
        false_negative_count=match[
            "false_negative_count"
        ],
        frame_has_false_alarm=(
            match["false_positive_count"] > 0
        ),
        frequency_errors_hz=match[
            "frequency_errors_hz"
        ],
        runtime_ms=float(
            runtime_ms
        ),
        finite_threshold_median_db=float(
            np.median(
                finite_threshold
            )
        )
    )


def evaluate_detectors(
        trials,
        detectors=None
):
    """Evaluate every detector on the exact same immutable trial objects."""

    if detectors is None:
        detectors = build_detector_adapters()

    results = []

    for trial in trials:
        for detector in detectors:
            results.append(
                evaluate_trial(
                    trial,
                    detector
                )
            )

    return tuple(
        results
    )


def summarize_results(
        results
):
    """Calculate common Pd, Pfa, precision, recall, runtime, and stability."""

    summaries = []

    detector_names = sorted(
        {
            result.detector
            for result in results
        }
    )

    scenario_names = sorted(
        {
            result.scenario
            for result in results
        }
    )

    for detector_name in detector_names:
        for scenario_name in scenario_names:
            group = [
                result
                for result in results
                if (
                        result.detector == detector_name
                        and result.scenario == scenario_name
                )
            ]

            if not group:
                continue

            true_positives = sum(
                result.true_positive_count
                for result in group
            )

            false_positives = sum(
                result.false_positive_count
                for result in group
            )

            false_negatives = sum(
                result.false_negative_count
                for result in group
            )

            expected_count = sum(
                result.expected_count
                for result in group
            )

            precision_denominator = (
                true_positives
                + false_positives
            )

            recall_denominator = (
                true_positives
                + false_negatives
            )

            errors = np.asarray(
                [
                    error
                    for result in group
                    for error in result.frequency_errors_hz
                ],
                dtype=float
            )

            runtimes = np.asarray(
                [
                    result.runtime_ms
                    for result in group
                ],
                dtype=float
            )

            detected_counts = np.asarray(
                [
                    result.detected_count
                    for result in group
                ],
                dtype=float
            )

            summaries.append({
                "detector": detector_name,
                "scenario": scenario_name,
                "trial_count": len(group),
                "probability_of_detection": (
                    true_positives / expected_count
                    if expected_count
                    else None
                ),
                "frame_false_alarm_rate": (
                    sum(
                        result.frame_has_false_alarm
                        for result in group
                    )
                    / len(group)
                ),
                "precision": (
                    true_positives
                    / precision_denominator
                    if precision_denominator
                    else None
                ),
                "recall": (
                    true_positives
                    / recall_denominator
                    if recall_denominator
                    else None
                ),
                "mean_runtime_ms": float(
                    np.mean(
                        runtimes
                    )
                ),
                "p95_runtime_ms": float(
                    np.percentile(
                        runtimes,
                        95
                    )
                ),
                "runtime_coefficient_of_variation": (
                    float(
                        np.std(
                            runtimes
                        )
                        / np.mean(
                            runtimes
                        )
                    )
                    if np.mean(runtimes) > 0
                    else 0.0
                ),
                "detected_count_standard_deviation": float(
                    np.std(
                        detected_counts
                    )
                ),
                "frequency_error_standard_deviation_hz": (
                    float(
                        np.std(
                            errors
                        )
                    )
                    if len(errors)
                    else None
                )
            })

    return tuple(
        summaries
    )
