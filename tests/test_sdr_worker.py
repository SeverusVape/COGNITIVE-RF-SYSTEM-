import unittest
import sys
from types import ModuleType
from unittest.mock import Mock, patch

stub_sdr_manager = ModuleType(
    "SDR.sdr_manager"
)
stub_sdr_manager.SDRManager = Mock
sys.modules.setdefault(
    "SDR.sdr_manager",
    stub_sdr_manager
)

from SDR.sdr_worker import SDRWorker


class SDRWorkerCenterFrequencyTests(unittest.TestCase):

    def _run_worker_with_tune_result(self, tune_result):
        manager = Mock()
        manager.connected = True
        manager.tune.return_value = tune_result
        manager.read_samples.return_value = None

        worker = SDRWorker(
            sample_rate=2.048e6,
            center_freq=100e6,
            gain=20,
            num_samples=1024
        )
        worker._pending_frequency = 120e6

        with patch(
                "SDR.sdr_worker.SDRManager",
                return_value=manager
        ):
            worker.run()

        return worker

    def test_center_frequency_updates_after_confirmed_tune(self):
        worker = self._run_worker_with_tune_result(
            True
        )

        self.assertEqual(
            worker.center_freq,
            120e6
        )

    def test_failed_tune_does_not_change_center_frequency(self):
        worker = self._run_worker_with_tune_result(
            False
        )

        self.assertEqual(
            worker.center_freq,
            100e6
        )


if __name__ == "__main__":
    unittest.main()
