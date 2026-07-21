from datetime import datetime


LOG_FILE = "signal_log.txt"

LOGGING_ENABLED = False

last_logged_signals = set()


def log_signals(peaks):

    global last_logged_signals

    current_signals = set()

    for freq, power, bandwidth_khz in peaks:

        signal_id = round(freq * 2) / 2

        current_signals.add(
            signal_id
        )

        if LOGGING_ENABLED and signal_id not in last_logged_signals:

            timestamp = datetime.now().strftime(
                "%H:%M:%S"
            )

            with open(LOG_FILE, "a") as file:

                file.write(
                    f"{timestamp}, "
                    f"{freq:.2f} MHz, "
                    f"{power:.1f} dB\n"
                )

    last_logged_signals = current_signals.copy()