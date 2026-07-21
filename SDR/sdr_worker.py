from threading import Lock

from PyQt6.QtCore import QThread, pyqtSignal

from SDR.sdr_manager import SDRManager


class SDRWorker(QThread):

    samples_ready = pyqtSignal(object)
    connected = pyqtSignal()
    connection_error = pyqtSignal(str)
    tune_succeeded = pyqtSignal(float)
    tune_failed = pyqtSignal(float, str)

    def __init__(
            self,
            sample_rate,
            center_freq,
            gain,
            num_samples
    ):
        super().__init__()

        self.sample_rate = sample_rate
        self.center_freq = center_freq
        self.gain = gain
        self.num_samples = num_samples

        self._tune_lock = Lock()
        self._pending_frequency = None

    def request_tune(self, freq_hz):
        if not self.isRunning():
            return False

        with self._tune_lock:
            self._pending_frequency = float(
                freq_hz
            )

        return True

    def get_center_frequency(self):
        if not self.isRunning():
            return None

        with self._tune_lock:
            return self.center_freq

    def _take_pending_frequency(self):
        with self._tune_lock:
            frequency = self._pending_frequency
            self._pending_frequency = None

        return frequency

    def run(self):
        sdr_manager = SDRManager(
            self.sample_rate,
            self.center_freq,
            self.gain
        )

        if not sdr_manager.connected:
            self.connection_error.emit(
                "SDR is not available."
            )
            return

        self.connected.emit()

        try:
            while not self.isInterruptionRequested():
                pending_frequency = (
                    self._take_pending_frequency()
                )

                if pending_frequency is not None:
                    if not sdr_manager.tune(
                            pending_frequency
                    ):
                        self.tune_failed.emit(
                            pending_frequency,
                            "Unable to tune SDR."
                        )
                        return

                    with self._tune_lock:
                        self.center_freq = pending_frequency

                    self.tune_succeeded.emit(
                        pending_frequency
                    )

                samples = sdr_manager.read_samples(
                    self.num_samples
                )

                if samples is None:
                    self.connection_error.emit(
                        "SDR sample acquisition failed."
                    )
                    return

                self.samples_ready.emit(
                    samples
                )

                self.msleep(
                    100
                )

        finally:
            sdr_manager.close()
