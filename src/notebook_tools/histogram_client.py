from time import sleep

from PyTango import DeviceProxy


class HistogramClient:
    def __init__(self, fqdn, timeout=3000):
        self.dp = DeviceProxy(fqdn)
        self.timeout = timeout

    def set_channel(self, channel):
        self.dp.histogram_channel = channel

    def capture(self):
        self.dp.histogram_timeout = self.timeout
        self.dp.start_histogram_capture()
        success = self._wait_done()
        data = None
        if success:
            data = self._read_histogram_data()
        return success, data

    def _wait_done(self):
        timeout_s = int(self.timeout / 1000)

        for i in range(timeout_s):
            status = self.dp.read_attribute("histogram_capture_status").value
            if not status:
                print(f"capture ended after {i} seconds")
                break
            sleep(1)

        success = self.dp.read_attribute("histogram_capture_success").value
        return success

    def _read_histogram_data(self):
        pol_x_data = self.dp.read_attribute("histogram_result_polX").value
        pol_y_data = self.dp.read_attribute("histogram_result_polY").value
        return [pol_x_data, pol_y_data]
