import json
import os
import time

from ska_control_model import HealthState

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment, TangoDeviceProxy


class TMCCentralNode(TangoDeviceProxy):
    def __init__(self, tango_deployment: TangoDeployment):
        super().__init__(tango_deployment.dp("ska_mid/tm_central/central_node"))

    @property
    def telescope_health_state(self) -> HealthState:
        return HealthState(self._device_proxy.telescopeHealthState)


class TMCSubarrayNode(TangoDeviceProxy):
    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        super().__init__(
            tango_deployment.dp(f"ska_mid/tm_subarray_node/{tango_deployment.subarray_index}")
        )


class TMCCSPMasterLeafNode(TangoDeviceProxy):
    def __init__(self, tango_deployment: TangoDeployment):
        super().__init__(tango_deployment.dp("ska_mid/tm_leaf_node/csp_master"))


class CSPController(TangoDeviceProxy):
    def __init__(self, tango_deployment: TangoDeployment):
        super().__init__(tango_deployment.dp("mid-csp/control/0"))


class CSPSubarray(TangoDeviceProxy):
    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        super().__init__(
            tango_deployment.dp(f"mid-csp/subarray/0{tango_deployment.subarray_index}")
        )


class SDPController(TangoDeviceProxy):
    def __init__(self, tango_deployment: TangoDeployment):
        super().__init__(tango_deployment.dp("mid-sdp/control/0"))


class SDPSubarray(TangoDeviceProxy):
    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        super().__init__(
            tango_deployment.dp(f"mid-sdp/subarray/0{tango_deployment.subarray_index}")
        )


class CBFController(TangoDeviceProxy):
    def __init__(self, tango_deployment: TangoDeployment):
        super().__init__(tango_deployment.dp("mid_csp_cbf/sub_elt/controller"))


class CBFSubarray(TangoDeviceProxy):
    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        super().__init__(
            tango_deployment.dp(f"mid_csp_cbf/sub_elt/subarray_0{tango_deployment.subarray_index}")
        )


class TangoSUTDeployment(TangoDeployment):
    def __init__(
        self,
        branch_name: str,
        dev_mode: bool,
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
        subarray_index: int = 1,
    ):
        namespace = get_sut_namespace(branch_name, dev_mode)
        self.subarray_index = subarray_index
        super().__init__(namespace, database_name, cluster_domain, db_port)
        os.environ["TANGO_HOST"] = self.tango_host()

    @property
    def tmc_central_node(self) -> TMCCentralNode:
        return TMCCentralNode(self)

    @property
    def tmc_subarray(self) -> TMCSubarrayNode:
        return TMCSubarrayNode(self)

    @property
    def tmc_csp_master_leaf_node(self) -> TMCCSPMasterLeafNode:
        return TMCCSPMasterLeafNode(self)

    @property
    def csp_subarray(self) -> CSPSubarray:
        return CSPSubarray(self)

    @property
    def csp_controller(self) -> CSPController:
        return CSPController(self)

    @property
    def cbf_subarray(self) -> CBFSubarray:
        return CBFSubarray(self)

    @property
    def cbf_controller(self) -> CBFController:
        return CBFController(self)

    @property
    def sdp_controller(self) -> SDPController:
        return SDPController(self)

    @property
    def sdp_subarray(self) -> SDPSubarray:
        return SDPSubarray(self)

    def load_dish_vcc_config(self):
        csp_controller = self.csp_controller
        self.logger.debug(
            f"CSP Controller: adminMode={csp_controller.admin_mode}; State={csp_controller.State()}"
        )
        csp_controller.write_attribute("adminMode", 0)
        # we sleep for 4 seconds to ensure cbf is in sync (it has a polling based init that takes 4 s)
        time.sleep(10)
        central_node = self.tmc_central_node
        dish_cfg_json = json.dumps(
            {
                "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
                "tm_data_sources": [
                    "car://gitlab.com/ska-telescope/ska-telmodel-data?ska-sdp-tmlite-repository-1.0.0#tmdata"
                ],
                "tm_data_filepath": "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json",
            }
        )
        central_node.LoadDishCfg(dish_cfg_json)
        self.logger.debug(
            f"CSP Controller: adminMode={csp_controller.admin_mode}; State={csp_controller.State()}"
        )
        self.logger.debug(
            f"TMC Central Node: isDishVccConfigSet={central_node.isDishVccConfigSet}; "
            f"dishvccvalidationstatus={central_node.dishvccvalidationstatus}"
        )
        csp_master_leaf_node = self.tmc_csp_master_leaf_node
        self.logger.debug(
            f"TMC CSP Master Leaf Node: sourceDishVccConfig={csp_master_leaf_node.sourceDishVccConfig}; "
            f"dishVccConfig={csp_master_leaf_node.dishVccConfig}"
        )

    def turn_csp_on(self):
        csp_controller = self.csp_controller
        csp_controller.write_attribute("adminMode", 0)
        time.sleep(
            4
        )  # we sleep for 4 seconds to ensure cbf is in sync (it has a polling based init that takes 4 s)

    def reset_csp_subarray(self):
        csp_subarray = self.csp_subarray
        csp_subarray.Abort()
        time.sleep(3)
        csp_subarray.Restart()

    def print_sut_diagnostics(self):
        self.logger.debug("TMC Diagnostics")
        self.print_tmc_diagnostics()
        self.logger.debug("CSP-LMC Diagnostics")
        self.print_csp_diagnostics()
        self.logger.debug("CBF Diagnostics")
        self.print_cbf_diagnostics()
        self.logger.debug("SDP Diagnostics")
        self.print_sdp_diagnostics()

    def print_cbf_diagnostics(self):
        cbf_controller = self.cbf_controller
        self.logger.debug(f"CBF Controller adminMode: {str(cbf_controller.admin_mode)}")
        self.logger.debug(f"CBF Controller State: {cbf_controller.State()}")
        cbf_subarray = self.cbf_subarray
        self.logger.debug(f"CBF Subarray adminMode: {str(cbf_subarray.admin_mode)}")
        self.logger.debug(f"CBF Subarray State: {cbf_subarray.State()}")
        self.logger.debug(f"CBF Subarray obsState: {str(cbf_subarray.obs_state)}")

    def print_csp_diagnostics(self):
        csp_controller = self.csp_controller
        self.logger.debug(f"CSP-LMC Controller adminMode: {str(csp_controller.admin_mode)}")
        self.logger.debug(f"CSP-LMC Controller State: {csp_controller.State()}")
        self.logger.debug(f"CSP-LMC Controller dishVccConfig: {csp_controller.dishVccConfig}")
        self.logger.debug(
            f"CSP-LMC Controller CBFSimulationMode: {csp_controller.cbfSimulationMode}"
        )
        subarray = self.csp_subarray
        self.logger.debug(f"CSP-LMC Subarray adminMode: {str(subarray.admin_mode)}")
        self.logger.debug(f"CSP-LMC Subarray State: {subarray.State()}")
        self.logger.debug(f"CSP-LMC Subarray obsState: {str(subarray.obs_state)}")
        self.logger.debug(f"CSP-LMC Subarray dishVccConfig: {subarray.dishVccConfig}")

    def print_tmc_diagnostics(self):
        tmc = self.tmc_central_node
        self.logger.debug(f"TMC Central Node state: {tmc.State()}")
        self.logger.debug(f"TMC Central Node adminMode: {str(tmc.admin_mode)}")
        self.logger.debug(f"TMC Central Node healthState: {str(tmc.health_state)}")
        self.logger.debug(
            f"TMC Central Node telescopeHealthState: {str(tmc.telescope_health_state)}"
        )
        tmc_subarray = self.tmc_subarray
        self.logger.debug(f"TMC Subarray Node state: {tmc_subarray.State()}")
        self.logger.debug(f"TMC Subarray adminMode: {str(tmc_subarray.admin_mode)}")
        self.logger.debug(f"TMC Subarray Node obsState: {str(tmc_subarray.obs_state)}")

    def print_sdp_diagnostics(self):
        sdp_controller = self.sdp_controller
        self.logger.debug(f"SDP Controller state: {sdp_controller.State()}")
        self.logger.debug(f"SDP Controller adminMode: {str(sdp_controller.admin_mode)}")
        sdp_subarray = self.sdp_subarray
        self.logger.debug(f"SDP Subarray state: {sdp_subarray.State()}")
        self.logger.debug(f"SDP Subarray adminMode: {str(sdp_subarray.admin_mode)}")
        self.logger.debug(f"SDP Subarray obsState: {str(sdp_subarray.obs_state)}")

    @property
    def signal_displays_endpoint(self) -> str:
        return f"https://k8s.{self._cluster_domain}/{self.namespace}/signal/display/"


def get_sut_namespace(branch_name: str, dev_mode: bool) -> str:
    if dev_mode:
        return f"ci-ska-mid-itf-{branch_name}"
    return "integration"


def disable_qa():
    """
    Disable QA
    :return: None
    """
    os.environ["DISABLE_QA"] = "True"
