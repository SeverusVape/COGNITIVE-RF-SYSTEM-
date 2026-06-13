from rtlsdr import RtlSdr


class SDRManager:

    def __init__(
        self,
        sample_rate,
        center_freq,
        gain
    ):

        self.sdr = RtlSdr()

        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = center_freq
        self.sdr.gain = gain

        print("SDR CONNECTED")

    def read_samples(
        self,
        num_samples
    ):

        return self.sdr.read_samples(
            num_samples
        )

    def tune(
        self,
        freq_hz
    ):

        self.sdr.center_freq = freq_hz

    def close(self):

        self.sdr.close()

        print("SDR CLOSED")