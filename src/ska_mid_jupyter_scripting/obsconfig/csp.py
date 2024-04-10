class CSPconfig(TargetSpecs, CommonConfig, LowCbfConfig, SubarrayConfig):
    csp_subarray_id = "dummy name"
    csp_scan_configure_schema = "https://schema.skao.int/ska-csp-configure/2.5"
    csp_subarray_id_low = "science period 23"
    config_id = "sbi-mvp01-20200325-00001-science_A"

    def __init__(self, **kwargs):
        """
        Initialize CSP Configuration
        :param kwargs: Keyword arguments
        :return: None
        """
        super().__init__(**kwargs)
        self.fsp_config = DEFAULT_FSP_CONFIGURATION

    def _generate_csp_scan_config(
        self,
        target_id: str | None = None,
        subarray_id: int = 1,
        sb_target_flag=False,
    ):
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
                common_config=CommonConfiguration(
                    self.eb_id, band, subarray_id
                ),
                cbf_config=CBFConfiguration(fsp_config_obj),
                pst_config=None,
                pss_config=None,
            )

    @encoded
    def generate_csp_scan_config(
        self,
        target_id: str | None = None,
        subarray_id: int = 1,
        sb_target_flag=False,
    ):
        """
        Generate CSP Scan Configuration by calling _generate_csp_scan_config
        :param target_id: Target ID
        :param subarray_id: Subarray ID
        :param sb_target_flag: Subarray target flag
        :return: CSPConfiguration object
        """
        return self._generate_csp_scan_config(
            target_id, subarray_id, sb_target_flag
        )

    def _generate_csp_assign_resources_config_low(self):
        """
        Generate common assign resource config
        :return: CentralCSPConfiguration object
        """
        interface = "https://schema.skao.int/ska-low-csp-assignresources/2.0"
        common = self.generate_common_assign_resource_config_low().as_object
        lowcbf = self.generate_lowcbf_assign_resource_config().as_object
        return CentralCSPConfiguration(
            interface=interface, common=common, lowcbf=lowcbf
        )

    @encoded
    def generate_csp_assign_resources_config_low(self):
        """
        Generate common assign resource config by calling _generate_csp_assign_resources_config
        :return: CentralCSPConfiguration object
        """
        return self._generate_csp_assign_resources_config_low()

    def _generate_csp_scan_config_low(self):
        """
        Generate CSP Scan Configuration
        :return: CSPConfiguration object
        """
        interface = "https://schema.skao.int/ska-csp-configure/2.5"
        common = self.generate_common_configure_resource_config_low().as_object
        lowcbf = self.generate_lowcbf_configure_resource_config().as_object
        subarray = (
            self.generate_subarray_configure_resource_config_low().as_object
        )

        return CSPConfiguration(
            interface=interface,
            subarray=subarray,
            common=common,
            lowcbf=lowcbf,
        )

    @encoded
    def generate_csp_scan_config_low(self):
        """
        Generate CSP Scan Configuration by calling _generate_csp_scan_config
        :return: CSPConfiguration object
        """
        return self._generate_csp_scan_config_low()

    def add_fsp_configuration(self, fsp_config):
        """
        Add FSP Configuration
        :param fsp_config: FSP Configuration
        :return: None
        """
        self.fsp_config = fsp_config
