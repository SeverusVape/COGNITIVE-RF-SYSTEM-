from rtlsdr import RtlSdr


class SDRManager:

    def __init__(
        self,
        sample_rate,
        center_freq,
        gain
    ):

        self.sdr = None
        self.connected = False

        try:
            self.sdr = RtlSdr()

            self.sdr.sample_rate = sample_rate
            self.sdr.center_freq = center_freq
            self.sdr.gain = gain

            self.connected = True

            print("SDR CONNECTED")

        except Exception as error:
            self.sdr = None
            self.connected = False

            print("SDR NOT CONNECTED")
            print(error)

    def read_samples(
        self,
        num_samples
    ):

        if not self.connected:
            return None

        try:
            return self.sdr.read_samples(
                num_samples
            )

        except Exception as error:
            self.connected = False

            print("SDR READ ERROR")
            print(error)

            return None

    def tune(
        self,
        freq_hz
    ):

        if not self.connected:
            return False

        try:
            self.sdr.center_freq = freq_hz
            return True

        except Exception as error:
            self.connected = False

            print("SDR TUNE ERROR")
            print(error)

            return False

    def close(self):

        if self.sdr is not None:
            try:
                self.sdr.close()
                print("SDR CLOSED")

            except Exception as error:
                print("SDR CLOSE ERROR")
                print(error)

        self.connected = False
