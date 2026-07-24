from dataclasses import dataclass

import numpy as np

from scipy.signal import find_peaks


@dataclass(frozen=True)
class OSCFARConfig:
    """Configuration for the experimental OS-CFAR detector.

    ``rank`` is one-based across both reference windows. For example, a
    configuration with 32 reference cells per side has 64 reference samples,
    so rank 48 selects the 48th-lowest sample.

    ``threshold_scale`` is a linear-power multiplier. The detector converts it
    to an additive dB offset before comparing it with SPECTRA's relative FFT
    power values.
    """

    reference_cells: int = 32
    guard_cells: int = 8
    rank: int = 48
    threshold_scale: float = 4.0
    minimum_peak_distance_khz: float = 75.0
    maximum_peaks: int = 3
    bandwidth_drop_db: float = 15.0

    def __post_init__(self):
        integer_fields = (
            ("Reference cells", self.reference_cells, 1),
            ("Guard cells", self.guard_cells, 0),
            ("Rank", self.rank, 1),
            ("Maximum peaks", self.maximum_peaks, 1)
        )

        for name, value, minimum in integer_fields:
            if (
                    isinstance(value, bool)
                    or not isinstance(value, int)
                    or value < minimum
            ):
                raise ValueError(
                    f"{name} must be an integer greater than "
                    f"or equal to {minimum}."
                )

        reference_count = 2 * self.reference_cells

        if self.rank > reference_count:
            raise ValueError(
                "Rank cannot exceed the total number of "
                "reference cells."
            )

        positive_fields = (
            ("Threshold scale", self.threshold_scale),
            (
                "Minimum peak distance",
                self.minimum_peak_distance_khz
            ),
            ("Bandwidth drop", self.bandwidth_drop_db)
        )

        for name, value in positive_fields:
            if (
                    isinstance(value, bool)
                    or not np.isfinite(value)
                    or value <= 0
            ):
                raise ValueError(
                    f"{name} must be a finite, positive number."
                )


def _normalize_inputs(
        power_db,
        freqs_mhz
):
    power_db = np.asarray(
        power_db,
        dtype=float
    )

    freqs_mhz = np.asarray(
        freqs_mhz,
        dtype=float
    )

    if power_db.ndim != 1:
        raise ValueError(
            "Power data must be one-dimensional."
        )

    if freqs_mhz.ndim != 1:
        raise ValueError(
            "Frequency data must be one-dimensional."
        )

    if len(power_db) != len(freqs_mhz):
        raise ValueError(
            "Power and frequency data must have equal lengths."
        )

    if len(freqs_mhz) < 2:
        raise ValueError(
            "At least two frequency bins are required."
        )

    if (
            not np.all(
                np.isfinite(power_db)
            )
            or not np.all(
                np.isfinite(freqs_mhz)
            )
    ):
        raise ValueError(
            "Power and frequency data must be finite."
        )

    frequency_steps = np.diff(
        freqs_mhz
    )

    if (
            np.any(frequency_steps == 0)
            or not (
                np.all(frequency_steps > 0)
                or np.all(frequency_steps < 0)
            )
    ):
        raise ValueError(
            "Frequency data must be strictly monotonic."
        )

    return (
        power_db,
        freqs_mhz,
        float(
            np.median(
                np.abs(
                    frequency_steps
                )
            )
            * 1000
        )
    )


def build_os_cfar_threshold(
        power_db,
        freqs_mhz,
        config=None
):
    """Build a guard-separated OS-CFAR threshold in relative dB.

    Bins without complete leading and lagging reference windows receive an
    infinite threshold and are therefore excluded from detection. This
    explicit edge policy prevents partially populated reference sets from
    changing the configured order statistic.
    """

    if config is None:
        config = OSCFARConfig()

    if not isinstance(
            config,
            OSCFARConfig
    ):
        raise TypeError(
            "OS-CFAR configuration must be an OSCFARConfig instance."
        )

    (
        power_db,
        freqs_mhz,
        _
    ) = _normalize_inputs(
        power_db,
        freqs_mhz
    )

    window_extent = (
        config.reference_cells
        + config.guard_cells
    )

    if len(power_db) < 2 * window_extent + 1:
        raise ValueError(
            "Spectrum is too short for the configured OS-CFAR window."
        )

    threshold = np.full(
        len(power_db),
        np.inf,
        dtype=float
    )

    threshold_offset_db = (
        10
        * np.log10(
            config.threshold_scale
        )
    )

    for index in range(
            window_extent,
            len(power_db) - window_extent
    ):
        left_stop = (
            index
            - config.guard_cells
        )

        left_start = (
            left_stop
            - config.reference_cells
        )

        right_start = (
            index
            + config.guard_cells
            + 1
        )

        right_stop = (
            right_start
            + config.reference_cells
        )

        reference_samples = np.concatenate(
            (
                power_db[
                    left_start:left_stop
                ],
                power_db[
                    right_start:right_stop
                ]
            )
        )

        ordered_reference = np.partition(
            reference_samples,
            config.rank - 1
        )[
            config.rank - 1
        ]

        threshold[index] = (
            ordered_reference
            + threshold_offset_db
        )

    return threshold


def detect_peaks(
        power_db,
        freqs_mhz,
        config=None
):
    """Detect peaks using the independent experimental OS-CFAR engine.

    The return shape intentionally matches ``SDR.detection.detect_peaks`` so
    both detectors can be evaluated on identical datasets without changing
    downstream SPECTRA interfaces.
    """

    if config is None:
        config = OSCFARConfig()

    (
        power_db,
        freqs_mhz,
        bin_width_khz
    ) = _normalize_inputs(
        power_db,
        freqs_mhz
    )

    threshold = build_os_cfar_threshold(
        power_db,
        freqs_mhz,
        config=config
    )

    minimum_peak_distance_bins = max(
        1,
        round(
            config.minimum_peak_distance_khz
            / bin_width_khz
        )
    )

    peak_indices, properties = find_peaks(
        power_db,
        height=threshold,
        distance=minimum_peak_distance_bins
    )

    peak_powers = properties[
        "peak_heights"
    ]

    sorted_indices = np.argsort(
        peak_powers
    )[::-1]

    selected_peaks = peak_indices[
        sorted_indices[
            :config.maximum_peaks
        ]
    ]

    results = []

    for peak in selected_peaks:
        frequency = freqs_mhz[
            peak
        ]

        power = power_db[
            peak
        ]

        bandwidth_threshold = (
            power
            - config.bandwidth_drop_db
        )

        left = peak

        while (
                left > 0
                and power_db[left] > bandwidth_threshold
        ):
            left -= 1

        right = peak

        while (
                right < len(power_db) - 1
                and power_db[right] > bandwidth_threshold
        ):
            right += 1

        bandwidth_khz = (
            right - left
        ) * bin_width_khz

        results.append(
            (
                frequency,
                power,
                bandwidth_khz
            )
        )

    return results, threshold
