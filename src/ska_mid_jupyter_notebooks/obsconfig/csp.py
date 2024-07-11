"""This is the Central Signal Processor."""
from ska_oso_pdm.entities.csp.csp_configuration import CSPConfiguration as CSPConfigurationPDM
from ska_tmc_cdm.messages.central_node.csp import CommonConfiguration as CentralCommonConfiguration
from ska_tmc_cdm.messages.central_node.csp import CSPConfiguration as CentralCSPConfiguration
from ska_tmc_cdm.messages.subarray_node.configure.csp import (
    CBFConfiguration,
    CommonConfiguration,
    CSPConfiguration,
    FSPConfiguration,
    FSPFunctionMode,
    SubarrayConfiguration,
)

from ska_mid_jupyter_notebooks.obsconfig.base import encoded
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpecs

# pylint: disable=E1101

DEFAULT_FSP_CONFIGURATION = {
    "fsp1": {
        "fsp_id": 1,
        "function_mode": FSPFunctionMode.CORR,
        "frequency_slice_id": 1,
        "integration_factor": 10,  # cannot use 1: see https://jira.skatelescope.org/browse/CIP-1708
        "zoom_factor": 0,
        # "channel_averaging_map": [(0, 2), (744, 0)], channel averaging is not supported by CBF yet
        "output_link_map": [(0, 0), (200, 1)],
        "channel_offset": 0,
    },
    "fsp2": {
        "fsp_id": 2,
        "function_mode": FSPFunctionMode.CORR,
        "frequency_slice_id": 1,
        "integration_factor": 10,  # cannot use 1: see https://jira.skatelescope.org/browse/CIP-1708
        # "zoom_factor": 1, # zoom is not supported by cbf yet
        "zoom_factor": 0,
        # "channel_averaging_map": [(0, 2), (744, 0)], channel averaging is not supported by CBF yet
        "output_link_map": [(0, 4), (200, 5)],
        "channel_offset": 744,
        # "zoom_window_tuning": 1050000,
    },
}


class CommonConfig:
    """Store common configuration here."""
    def _generate_common_assign_resource_config_low(self) -> CentralCommonConfiguration:
        """
        Generate common assign resource config.

        :return: CentralCommonConfiguration object
        """
        return CentralCommonConfiguration(subarray_id=1)

    @encoded
    def generate_common_assign_resource_config_low(self) -> CentralCommonConfiguration:
        """
        Generate common assign resource config.

        :return:  CentralCommonConfiguration object
        """
        return self._generate_common_assign_resource_config_low()

    def _generate_common_configure_resource_config_low(self) -> CommonConfiguration:
        """
        Generate common configure resource config.

        :return: CommonConfiguration object
        """
        return CommonConfiguration(config_id="sbi-mvp01-20200325-00001-science_A")

    @encoded
    def generate_common_configure_resource_config_low(self) -> CommonConfiguration:
        """
        Generate common configure resource config.

        :return: CommonConfiguration object
        """
        return self._generate_common_configure_resource_config_low()


class SubarrayConfig:
    """Store configuration for subarray."""
    def _generate_subarray_configure_resource_config_low(self) -> SubarrayConfiguration:
        """
        Generate subarray configure resource config.

        :return: SubarrayConfiguration object
        """
        return SubarrayConfiguration(subarray_name="science period 23")

    @encoded
    def generate_subarray_configure_resource_config_low(self) -> SubarrayConfiguration:
        """
        Generate subarray configure resource config.
        :return: SubarrayConfiguration object
        """
        return self._generate_subarray_configure_resource_config_low()


class CSPconfig(TargetSpecs, CommonConfig, SubarrayConfig):
    """Store configuration for CSP."""
    csp_subarray_id = "dummy name"
    csp_scan_configure_schema = "https://schema.skao.int/ska-csp-configure/2.5"
    csp_subarray_id_low = "science period 23"
    config_id = "sbi-mvp01-20200325-00001-science_A"

    def __init__(self, **kwargs):
        """
        Initialize CSP Configuration.

        :param kwargs: Keyword arguments
        :return: None
        """
        super().__init__(**kwargs)
        self.fsp_config = DEFAULT_FSP_CONFIGURATION

    def _generate_csp_scan_config(
        self,
        target_id: str | None = None,
        subarray_id: int = 1,
        sb_target_flag: bool = False,
    ) -> CSPConfiguration | CSPConfigurationPDM:
        """
        Generate CSP Scan Configuration
        :return: CSPConfiguration object
        """
        fsp_config_obj = []
        spec = self.get_target_spec(target_id)

        for k, v in self.fsp_config.items():
            fsp_config_obj.append(FSPConfiguration(**v))
        band = spec.band
        if not sb_target_flag:
            return CSPConfiguration(
                self.csp_scan_configure_schema,
                SubarrayConfiguration(self.csp_subarray_id),
                CommonConfiguration(self.eb_id, band, subarray_id),
                CBFConfiguration(fsp_config_obj),
            )
        else:
            return CSPConfigurationPDM(
                config_id=self.config_id,
                subarray_config=SubarrayConfiguration(self.csp_subarray_id),
                common_config=CommonConfiguration(self.eb_id, band, subarray_id),
                cbf_config=CBFConfiguration(fsp_config_obj),
                pst_config=None,
                pss_config=None,
            )

    @encoded
    def generate_csp_scan_config(
        self,
        target_id: str | None = None,
        subarray_id: int = 1,
        sb_target_flag: bool = False,
    ) -> CSPConfiguration:
        """
        Generate CSP Scan Configuration.

        :param target_id: Target ID
        :param subarray_id: Subarray ID
        :param sb_target_flag: Subarray target flag
        :return: CSPConfiguration object
        """
        return self._generate_csp_scan_config(target_id, subarray_id, sb_target_flag)

    def _generate_csp_assign_resources_config_low(self) -> CentralCSPConfiguration:
        """
        Generate common assign resource config.
        :return: CentralCSPConfiguration object
        """
        interface = "https://schema.skao.int/ska-low-csp-assignresources/2.0"
        common = self.generate_common_assign_resource_config_low().as_object
        return CentralCSPConfiguration(interface=interface, common=common)

    @encoded
    def generate_csp_assign_resources_config_low(self) -> CentralCSPConfiguration:
        """
        Generate common assign resource config.

        :return: CentralCSPConfiguration object
        """
        return self._generate_csp_assign_resources_config_low()

    def _generate_csp_scan_config_low(self) -> CSPConfiguration:
        """
        Generate CSP Scan Configuration.

        :return: CSPConfiguration object
        """
        interface = "https://schema.skao.int/ska-csp-configure/2.5"
        common = self.generate_common_configure_resource_config_low().as_object
        subarray = self.generate_subarray_configure_resource_config_low().as_object

        return CSPConfiguration(
            interface=interface,
            subarray=subarray,
            common=common,
        )

    @encoded
    def generate_csp_scan_config_low(self) -> CSPConfiguration:
        """
        Generate CSP Scan Configuration.

        :return: CSPConfiguration object
        """
        return self._generate_csp_scan_config_low()

    def add_fsp_configuration(self, fsp_config: FSPConfiguration) -> None:
        """
        Add FSP Configuration.

        :param fsp_config: FSP Configuration
        """
        self.fsp_config = fsp_config
