def classify_signal_type(feature):

    if (
        feature.bandwidth_khz > 100
        and feature.persistence == "L"
    ):
        return "FM Broadcast"

    return "Unknown"