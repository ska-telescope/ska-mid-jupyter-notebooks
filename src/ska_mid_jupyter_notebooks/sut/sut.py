"""Implement system under test."""

# pylint: disable=duplicate-code

import json
import os
import time
from typing import Callable

from ska_control_model import HealthState

from ska_mid_jupyter_notebooks.cluster.cluster import (
    Environment,
    TangoDeployment,
    TangoDeviceProxy,
)


class TMCCentralNode(TangoDeviceProxy):
    """Implement Telescope monitor and control central node."""

    def __init__(self, tango_deployment: TangoDeployment):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("ska_mid/tm_central/central_node"))

    @property
    def telescope_health_state(self) -> HealthState:
        """
        Read health state of telescope.

        :return: health state
        """
        return HealthState(self._device_proxy.telescopeHealthState)


class TMCSubarrayNode(TangoDeviceProxy):
    """Implement Telescope monitor and control subarray node."""

    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(
            tango_deployment.dp(f"ska_mid/tm_subarray_node/{tango_deployment.subarray_index}")
        )


class DishLeafNode001(TangoDeviceProxy):
    """Implement dish leaf node 001."""

    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("ska_mid/tm_leaf_node/d0001"))


class DishLeafNode036(TangoDeviceProxy):
    """Implement dish leaf node 036."""

    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("ska_mid/tm_leaf_node/d0036"))


class TMCCSPMasterLeafNode(TangoDeviceProxy):
    """Implement Telescope monitor and control master leaf node."""

    def __init__(self, tango_deployment: TangoDeployment):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("ska_mid/tm_leaf_node/csp_master"))


class CSPController(TangoDeviceProxy):
    """Implement CSP controller."""

    def __init__(self, tango_deployment: TangoDeployment):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("mid-csp/control/0"))


class CSPSubarray(TangoDeviceProxy):
    """Implement CSP subarray."""

    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(
            tango_deployment.dp(f"mid-csp/subarray/0{tango_deployment.subarray_index}")
        )


class SDPController(TangoDeviceProxy):
    """Implement science data processor controller."""

    def __init__(self, tango_deployment: TangoDeployment):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("mid-sdp/control/0"))


class SDPSubarray(TangoDeviceProxy):
    """Implement science data processor subarray."""

    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(
            tango_deployment.dp(f"mid-sdp/subarray/0{tango_deployment.subarray_index}")
        )


class CBFController(TangoDeviceProxy):
    """Implement correlator beam former controller."""

    def __init__(self, tango_deployment: TangoDeployment):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(tango_deployment.dp("mid_csp_cbf/sub_elt/controller"))


class CBFSubarray(TangoDeviceProxy):
    """Implement correlator beam former subarray."""

    def __init__(self, tango_deployment: "TangoSUTDeployment"):
        """
        Rock and roll.

        :param tango_deployment: handle for Tango device
        """
        super().__init__(
            tango_deployment.dp(f"mid_csp_cbf/sub_elt/subarray_0{tango_deployment.subarray_index}")
        )


class TangoSUTDeployment(TangoDeployment):
    """Deploy a Tango system under test."""

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        branch_name: str,
        environment: Environment,
        namespace_override: str = "",
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
        subarray_index: int = 1,
    ):
        """
        Rock and roll.

        :param branch_name: git branch name
        :param environment: environmental stuff
        :param namespace_override: override namespace
        :param database_name: database server
        :param cluster_domain: domain for cluster
        :param db_port: database port
        :param subarray_index: index number for subarray
        """
        self.environment = environment
        if namespace_override:
            namespace = namespace_override
        else:
            namespace = get_sut_namespace(self.environment, branch_name)
        self.subarray_index = subarray_index
        super().__init__(namespace, database_name, cluster_domain, db_port)
        os.environ["TANGO_HOST"] = self.tango_host

    def __str__(self) -> str:
        """
        Do the string thing.

        :return: string representation
        """
        return f"TangoSUTDeployment{{subarray_index={self.subarray_index}; {super().__str__()}}}"

    @property
    def tmc_central_node(self) -> TMCCentralNode:
        """
        Get handle for TMC Central Node.

        :return: TMC Central Node
        """
        return TMCCentralNode(self)

    @property
    def tmc_subarray(self) -> TMCSubarrayNode:
        """
        Get handle for TMC Subarray Node.

        :return: TMC Subarray Node
        """
        return TMCSubarrayNode(self)

    @property
    def tmc_dish_leafnode_001(self) -> DishLeafNode001:
        """Get dish leaf node 001."""
        return DishLeafNode001(self)

    @property
    def tmc_dish_leafnode_036(self) -> DishLeafNode036:
        """Get dish leaf node 036."""
        return DishLeafNode036(self)

    @property
    def tmc_csp_master_leaf_node(self) -> TMCCSPMasterLeafNode:
        """
        Get handle for TMC CSP Master Leaf Node.

        :return: TMC CSP Master Leaf Node
        """
        return TMCCSPMasterLeafNode(self)

    @property
    def csp_subarray(self) -> CSPSubarray:
        """
        Get handle for CSP Subarray.

        :return: CSP Subarray
        """
        return CSPSubarray(self)

    @property
    def csp_controller(self) -> CSPController:
        """
        Get handle for CSP Controller.

        :return: CSP Controller
        """
        return CSPController(self)

    @property
    def cbf_subarray(self) -> CBFSubarray:
        """
        Get handle for CBF Subarray.

        :return: CBF Subarray
        """
        return CBFSubarray(self)

    @property
    def cbf_controller(self) -> CBFController:
        """
        Get handle for CBF Controller.

        :return: CBF Controller
        """
        return CBFController(self)

    @property
    def sdp_controller(self) -> SDPController:
        """
        Get handle for SDP Controller.

        :return: SDP Controller
        """
        return SDPController(self)

    @property
    def sdp_subarray(self) -> SDPSubarray:
        """
        Get handle for SDP Subarray.

        :return: SDP Subarray
        """
        return SDPSubarray(self)

    def load_dish_vcc_config(self) -> None:
        """Load dish VCC configuration."""
        self.switch_csp_to_online()
        central_node = self.tmc_central_node

        def is_dish_vcc_config_set(sleep_time: int) -> bool:
            print(
                f"TMC Central Node isDishVccConfigSet={central_node.isDishVccConfigSet}"
                f" after {sleep_time}s"
            )
            return bool(central_node.isDishVccConfigSet)

        wait_for_state(is_dish_vcc_config_set, max_sleep=360)
        dish_cfg_json = json.dumps(
            {
                "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
                "tm_data_sources": [
                    "car://gitlab.com/ska-telescope/"
                    "ska-telmodel-data?ska-sdp-tmlite-repository-1.0.0#tmdata"
                ],
                "tm_data_filepath": "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json",
            }
        )
        central_node.LoadDishCfg(dish_cfg_json)
        csp_controller = self.csp_controller
        print(
            f"CSP Controller: adminMode={csp_controller.admin_mode};"
            f" State={csp_controller.State()}"
        )
        print(
            f"TMC Central Node: isDishVccConfigSet={central_node.isDishVccConfigSet}; "
            f"dishvccvalidationstatus={central_node.dishvccvalidationstatus}"
        )
        csp_master_leaf_node = self.tmc_csp_master_leaf_node
        print(
            "TMC CSP Master Leaf Node:"
            f" sourceDishVccConfig={csp_master_leaf_node.sourceDishVccConfig};"
            f" dishVccConfig={csp_master_leaf_node.dishVccConfig}"
        )

    def switch_csp_to_online(self) -> None:
        """Switch CSP to online."""
        csp_controller = self.csp_controller
        print(
            f"CSP Controller: adminMode={csp_controller.admin_mode};"
            f" State={csp_controller.State()}"
        )
        csp_controller.write_attribute("adminMode", 0)

        def csp_off(total_sleep: int) -> bool:
            print(
                f"CSP Controller: adminMode={csp_controller.admin_mode};"
                f" State={csp_controller.State()} after {total_sleep}s."
            )
            return str(csp_controller.State()) == "OFF"

        wait_for_state(csp_off, max_sleep=360)
        print(
            f"CSP Controller: adminMode={csp_controller.admin_mode};"
            f" State={csp_controller.State()}"
        )

    def print_sut_diagnostics(self) -> None:
        """Print all diagnostics."""
        print("TMC Diagnostics")
        self.print_tmc_diagnostics()
        print("CSP-LMC Diagnostics")
        self.print_csp_diagnostics()
        print("CBF Diagnostics")
        self.print_cbf_diagnostics()
        print("SDP Diagnostics")
        self.print_sdp_diagnostics()

    def print_cbf_diagnostics(self) -> None:
        """Print CBF diagnostics."""
        cbf_controller = self.cbf_controller
        print(f"CBF Controller adminMode: {str(cbf_controller.admin_mode)}")
        print(f"CBF Controller State: {cbf_controller.State()}")
        cbf_subarray = self.cbf_subarray
        print(f"CBF Subarray adminMode: {str(cbf_subarray.admin_mode)}")
        print(f"CBF Subarray State: {cbf_subarray.State()}")
        print(f"CBF Subarray obsState: {str(cbf_subarray.obs_state)}")

    def print_csp_diagnostics(self) -> None:
        """Print CSP diagnostics."""
        csp_controller = self.csp_controller
        print(f"CSP-LMC Controller adminMode: {str(csp_controller.admin_mode)}")
        print(f"CSP-LMC Controller State: {csp_controller.State()}")
        print(f"CSP-LMC Controller dishVccConfig: {csp_controller.dishVccConfig}")
        print(f"CSP-LMC Controller CBFSimulationMode: {csp_controller.cbfSimulationMode}")
        subarray = self.csp_subarray
        print(f"CSP-LMC Subarray adminMode: {str(subarray.admin_mode)}")
        print(f"CSP-LMC Subarray State: {subarray.State()}")
        print(f"CSP-LMC Subarray obsState: {str(subarray.obs_state)}")
        print(f"CSP-LMC Subarray dishVccConfig: {subarray.dishVccConfig}")

    def print_tmc_diagnostics(self) -> None:
        """Print TMC diagnostics."""
        tmc = self.tmc_central_node
        print(f"TMC Central Node state: {tmc.State()}")
        print(f"TMC Central Node adminMode: {str(tmc.admin_mode)}")
        print(f"TMC Central Node healthState: {str(tmc.health_state)}")
        print(f"TMC Central Node telescopeHealthState: {str(tmc.telescope_health_state)}")
        print(f"TMC Central Node isDishVccConfig: {str(tmc.isDishVccConfigSet)}")
        print(f"TMC Central Node dishvccvalidationstatus: {str(tmc.dishvccvalidationstatus)}")
        tmc_subarray = self.tmc_subarray
        print(f"TMC Subarray Node state: {tmc_subarray.State()}")
        print(f"TMC Subarray adminMode: {str(tmc_subarray.admin_mode)}")
        print(f"TMC Subarray Node obsState: {str(tmc_subarray.obs_state)}")
        tmc_dish_leafnode_001 = self.tmc_dish_leafnode_001
        print(f"TMC Dish Leaf Node 001 mode: {str(tmc_dish_leafnode_001.dishMode)}")
        print(f"TMC Dish Leaf Node 001 pointing state: {str(tmc_dish_leafnode_001.pointingState)}")
        tmc_dish_leafnode_036 = self.tmc_dish_leafnode_036
        print(f"TMC Dish Leaf Node 036 mode: {str(tmc_dish_leafnode_036.dishMode)}")
        print(f"TMC Dish Leaf Node 036 pointing state: {str(tmc_dish_leafnode_036.pointingState)}")

    def print_sdp_diagnostics(self) -> None:
        """Print SDP diagnostics."""
        sdp_controller = self.sdp_controller
        print(f"SDP Controller state: {sdp_controller.State()}")
        print(f"SDP Controller adminMode: {str(sdp_controller.admin_mode)}")
        sdp_subarray = self.sdp_subarray
        print(f"SDP Subarray state: {sdp_subarray.State()}")
        print(f"SDP Subarray adminMode: {str(sdp_subarray.admin_mode)}")
        print(f"SDP Subarray obsState: {str(sdp_subarray.obs_state)}")

    @property
    def signal_displays_endpoint(self) -> str:
        """
        Get endpoint of signal displays.

        :return: URL of display
        """
        return f"https://k8s.{self._cluster_domain}/{self.namespace}/signal/display/"


def get_sut_namespace(environment: Environment, branch_name: str) -> str:
    """
    Get K8S namespace.

    :param environment: environmental stuff
    :param branch_name: branch name
    :return: namespoce
    """
    if environment == Environment.CI:
        return f"ci-ska-mid-itf-{branch_name}"
    if environment == Environment.Staging:
        return "staging"
    if environment == Environment.Integration:
        return "integration"
    # TODO what should the default value be?
    return "whatever"


def disable_qa() -> None:
    """Disable quality assurance."""
    os.environ["DISABLE_QA"] = "True"


def wait_for_state(is_ready: Callable[[int], bool], max_sleep: int = 60) -> None:
    """
    Wait for the DeviceProxy to reach the expected state.

    :param is_ready: readiness thing
    :param max_sleep: the maximum time to sleep in seconds.
    :raises TimeoutError: if the DeviceProxy does not reach the expected state
    """
    sleep_interval = 1
    total_sleep = 0
    while not is_ready(total_sleep):
        time.sleep(sleep_interval)
        total_sleep += sleep_interval
        if total_sleep >= max_sleep:
            raise TimeoutError(f"Timed out waiting after {total_sleep} seconds")
        sleep_interval = min(2 * sleep_interval, max_sleep - total_sleep)
