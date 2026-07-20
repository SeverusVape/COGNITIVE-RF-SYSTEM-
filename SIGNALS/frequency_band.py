from dataclasses import dataclass
import math


@dataclass(frozen=True)
class FrequencyBandContext:
    code: str
    name: str
    start_mhz: float | None
    stop_mhz: float | None


UNKNOWN_BAND = FrequencyBandContext(
    code="Unknown",
    name="Unknown",
    start_mhz=None,
    stop_mhz=None
)


# These entries describe frequency-allocation context only. They do not prove
# the modulation, transmitter identity, or service carried by a detected peak.
FREQUENCY_BANDS = (
    FrequencyBandContext(
        code="BC",
        name="FM Broadcast",
        start_mhz=88.0,
        stop_mhz=108.0
    ),
    FrequencyBandContext(
        code="AIRBND",
        name="Airband",
        start_mhz=118.0,
        stop_mhz=137.0
    ),
    FrequencyBandContext(
        code="2m",
        name="Amateur 2m",
        start_mhz=144.0,
        stop_mhz=148.0
    ),
    FrequencyBandContext(
        code="NOAA",
        name="NOAA Weather",
        start_mhz=162.4,
        stop_mhz=162.6
    ),
    FrequencyBandContext(
        code="WX",
        name="Weather Band",
        start_mhz=162.0,
        stop_mhz=163.0
    ),
    FrequencyBandContext(
        code="70cm",
        name="Amateur 70cm",
        start_mhz=420.0,
        stop_mhz=450.0
    ),
    FrequencyBandContext(
        code="GMRS",
        name="GMRS",
        start_mhz=462.0,
        stop_mhz=468.0
    ),
)


def get_frequency_band_context(
        frequency_mhz
):
    if frequency_mhz is None:
        return UNKNOWN_BAND

    try:
        normalized_frequency = float(
            frequency_mhz
        )
    except (TypeError, ValueError):
        return UNKNOWN_BAND

    if not math.isfinite(
            normalized_frequency
    ):
        return UNKNOWN_BAND

    for band in FREQUENCY_BANDS:
        if (
                band.start_mhz
                <= normalized_frequency
                <= band.stop_mhz
        ):
            return band

    return UNKNOWN_BAND


def classify_frequency_band(
        frequency_mhz
):
    return get_frequency_band_context(
        frequency_mhz
    ).code
