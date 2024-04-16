import json
import os
import time
from typing import Any, Literal, TypedDict

from tango import DeviceProxy

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

    def dp(self, name: str) -> Any:
        return DeviceProxy(f"{self.tango_host()}/{name}")

    def tmc_central_node_dp(self) -> Any:
        return self.dp("ska_mid/tm_central/central_node")

    def tmc_csp_master_leaf_node_dp(self) -> Any:
        return self.dp("ska_mid/tm_leaf_node/csp_master")

    def csp_subarray_dp(self) -> Any:
        return self.dp("mid-csp/subarray/01")

    def csp_controller_dp(self) -> Any:
        return self.dp("mid-csp/control/0")

    def turn_csp_on(self):
        csp_controller = self.csp_controller_dp()
        csp_controller.write_attribute("adminMode", 0)
        time.sleep(
            4
        )  # we sleep for 4 seconds to ensure cbf is in sync (it has a polling based init that takes 4 s)

    def reset_csp_subarray(self):
        csp_subarray = self.csp_subarray_dp()
        csp_subarray.Abort()
        time.sleep(3)
        csp_subarray.Restart()

    def load_dish_cfg(self):
        central_node_proxy = self.tmc_central_node_dp()
        dish_cfg_json = json.dumps(
            {
                "interface": "https://schema.skao.int/ska-mid-cbf-initial-parameters/2.2",
                "tm_data_sources": [
                    "car://gitlab.com/ska-telescope/ska-telmodel-data?main#tmdata"
                ],
                "tm_data_filepath": "instrument/dishid_vcc_configuration/mid_cbf_parameters.json",
            }
        )
        central_node_proxy.LoadDishCfg(dish_cfg_json)
        csp_master_leaf_node = self.tmc_csp_master_leaf_node_dp()
        print(f"TMC: sourceDishVccConfig={csp_master_leaf_node.sourceDishVccConfig}")
        print(f"TMC: dishVccConfig={csp_master_leaf_node.dishVccConfig}")


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
