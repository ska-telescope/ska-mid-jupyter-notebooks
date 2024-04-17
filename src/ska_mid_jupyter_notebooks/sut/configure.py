import json
import os
import time
from typing import Any

from ska_mid_jupyter_notebooks.cluster.cluster import TangoCluster


class TangoSUTCluster(TangoCluster):
    def __init__(
        self,
        branch_name: str,
        dev_mode: bool,
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ):
        namespace = get_sut_namespace(branch_name, dev_mode)
        super().__init__(namespace, database_name, cluster_domain, db_port)
        os.environ["TANGO_HOST"] = self.tango_host()

    @property
    def tmc_central_node_dp(self) -> Any:
        return self.dp("ska_mid/tm_central/central_node")

    @property
    def tmc_subarray_dp(self) -> Any:
        return self.dp("ska_mid/tm_subarray_node/1")

    @property
    def tmc_csp_master_leaf_node_dp(self) -> Any:
        return self.dp("ska_mid/tm_leaf_node/csp_master")

    @property
    def csp_subarray_dp(self) -> Any:
        return self.dp("mid-csp/subarray/01")

    @property
    def csp_controller_dp(self) -> Any:
        return self.dp("mid-csp/control/0")

    @property
    def sdp_controller_dp(self) -> Any:
        return self.dp("mid-sdp/control/0")

    def load_dish_vcc_config(self):
        csp_controller = self.csp_controller_dp
        self.logger.debug(
            f"CSP Controller: adminMode={csp_controller.adminMode}; State={csp_controller.State()}"
        )
        csp_controller.write_attribute("adminMode", 0)
        # we sleep for 4 seconds to ensure cbf is in sync (it has a polling based init that takes 4 s)
        time.sleep(4)
        central_node = self.tmc_central_node_dp
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
            f"CSP Controller: adminMode={csp_controller.adminMode}; State={csp_controller.State()}"
        )
        self.logger.debug(
            f"TMC Central Node: isDishVccConfigSet={central_node.isDishVccConfigSet}; dishvccvalidationstatus={central_node.dishvccvalidationstatus}"
        )
        csp_master_leaf_node = self.tmc_csp_master_leaf_node_dp
        self.logger.debug(
            f"TMC CSP Master Leaf Node: sourceDishVccConfig={csp_master_leaf_node.sourceDishVccConfig}; dishVccConfig={csp_master_leaf_node.dishVccConfig}"
        )

    def turn_csp_on(self):
        csp_controller = self.csp_controller_dp
        csp_controller.write_attribute("adminMode", 0)
        time.sleep(
            4
        )  # we sleep for 4 seconds to ensure cbf is in sync (it has a polling based init that takes 4 s)

    def reset_csp_subarray(self):
        csp_subarray = self.csp_subarray_dp
        csp_subarray.Abort()
        time.sleep(3)
        csp_subarray.Restart()

    def print_csp_diagnostics(self):
        csp_controller = self.csp_controller_dp
        self.logger.debug(f"CSP-LMC Controller adminMode: {csp_controller.adminMode}")
        self.logger.debug(f"CSP-LMC Controller State: {csp_controller.State()}")
        self.logger.debug(f"CSP-LMC Controller dishVCCConfig: {csp_controller.dishVCCConfig}")
        self.logger.debug(
            f"CSP-LMC Controller CBFSimulationMode: {csp_controller.CBFSimulationMode}"
        )
        subarray = self.csp_subarray_dp
        self.logger.debug(f"CSP-LMC Subarray State: {subarray.State()}")
        self.logger.debug(f"CSP-LMC Subarray obsState: {subarray.obsState}")
        self.logger.debug(f"CSP-LMC Subarray dishVCCConfig: {subarray.dishVCCConfig}")

    def print_tmc_diagnostics(self):
        tmc = self.tmc_central_node_dp
        self.logger.debug(f"TMC Central Node state: {tmc.state()}")
        self.logger.debug(f"TMC Central Node healthState: {tmc.healthState}")
        self.logger.debug(f"TMC Central Node telescopeHealthState: {tmc.telescopeHealthState}")
        tmc_subarray = self.tmc_subarray_dp
        self.logger.debug(f"TMC Subarray Node state: {tmc_subarray.state()}")
        self.logger.debug(f"TMC Subarray Node obsState: {tmc_subarray.obsState}")

    def print_sdp_diagnostics(self):
        sdp = self.sdp_controller_dp
        self.logger.debug(f"SDP Controller state: {sdp.state()}")

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
