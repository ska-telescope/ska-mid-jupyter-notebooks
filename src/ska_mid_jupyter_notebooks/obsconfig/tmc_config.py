from datetime import timedelta

from ska_tmc_cdm.messages.subarray_node.configure import TMCConfiguration


class TMCConfig:
    def generate_tmc_scan_config(self, scan_duration: float):
        """
        Generate tmc scan configuration for a given scan duration
        :param scan_duration: Scan Duration
        :return: TMCConfiguration object
        """
        return TMCConfiguration(timedelta(seconds=scan_duration))
