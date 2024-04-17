import time
from typing import Any

from tango import DeviceProxy

from ska_mid_jupyter_notebooks.cluster.cluster import TangoCluster


class TangoDishCluster(TangoCluster):
    def __init__(
        self,
        dish_id: str,
        branch_name: str,
        dev_mode: bool,
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ):
        self.dish_id = dish_id
        namespace = get_dish_namespace(dish_id, branch_name, dev_mode)
        super().__init__(namespace, database_name, cluster_domain, db_port)

    def reset_dish(self):
        dish_proxy = self.device_manager_dp
        self.logger.debug(f"{self.dish_id}: aborting dish operation")
        dish_proxy.AbortCommands()
        while (str(dish_proxy.dishMode) != "dishMode.ABORTING") and (
            (str(dish_proxy.dishMode) != "dishMode.OPERATE")
        ):
            time.sleep(1)
        self.logger.debug(f"{self.dish_id}: stowing dish")
        dish_proxy.SetStowMode()
        while str(dish_proxy.dishMode) != "dishMode.STOW":
            time.sleep(1)
        self.logger.debug(f"{self.dish_id}: setting standbyLP mode")
        dish_proxy.SetStandbyLPMode()
        self.logger.debug(f"{self.dish_id}: {dish_proxy.Status()}")

    @property
    def device_manager_dp(self) -> Any:
        return self.dp(f"mid-dish/dish-manager/{self.dish_id}")

    @property
    def spfc_simulator_dp(self) -> Any:
        # TODO: Update this to grab the real SPFC if it is connected.
        return self.dp(f"mid-dish/simulator-spfc/{self.dish_id}")

    @property
    def spfrx_simulator_dp(self) -> Any:
        # TODO: Update this to grab the real SPFRx if it is connected.
        return self.dp(f"mid-dish/simulator-spfrx/{self.dish_id}")

    @property
    def ds_manager_dp(self) -> Any:
        return self.dp(f"mid-dish/ds-manager/{self.dish_id}")

    def print_diagnostics(self):
        dm = self.device_manager_dp
        self.logger.debug(f"{self.dish_id}: ComponentStates: {dm.GetComponentStates()}")
        self.logger.debug(f"{self.dish_id}: DishMode: {dm.dishMode}")
        self.logger.debug(f"{self.dish_id}: PowerState: {dm.powerState}")
        self.logger.debug(f"{self.dish_id}: HealthState: {dm.healthState}")
        self.logger.debug(f"{self.dish_id}: PointingState: {dm.pointingState}")
        self.logger.debug(f"{self.dish_id}: K-Value: {dm.kValue}")
        self.logger.debug(f"{self.dish_id}: Capturing: {dm.capturing}")
        self.logger.debug(f"{self.dish_id}: SimulationMode: {dm.simulationMode}")
        spfc = self.spfc_simulator_dp
        self.logger.debug(f"{self.dish_id}: SPFC OperatingMode: {spfc.OperatingMode}")
        spfrx = self.spfrx_simulator_dp
        self.logger.debug(f"{self.dish_id}: SPFRx OperatingMode: {spfrx.OperatingMode}")
        ds_manager = self.ds_manager_dp
        self.logger.debug(f"{self.dish_id}: DS Manager OperatingMode: {ds_manager.OperatingMode}")
        self.logger.debug(
            "{self.dish_id}: DS Manager IndexerPosition: {ds_manager.indexerPosition}"
        )


def get_dish_namespace(dish_id: str, branch_name: str, dev_mode: bool) -> str:
    if dev_mode:
        return f"ci-dish-lmc-{dish_id}-{branch_name}"
    return f"dish-lmc-{dish_id}"
