"""TMC scan configuration."""

from datetime import timedelta

from ska_tmc_cdm.messages.subarray_node.configure import (  # type: ignore[import-untyped]
    TMCConfiguration,
)


# pylint: disable-next=too-few-public-methods
class TMCConfig:
    """Store the TMC scan configuration."""

    def generate_tmc_scan_config(self, scan_duration: float) -> TMCConfiguration:
        """
        Generate tmc scan configuration for a given scan duration
        :param scan_duration: Scan Duration
        :return: TMCConfiguration object
        """
        return TMCConfiguration(timedelta(seconds=scan_duration))
