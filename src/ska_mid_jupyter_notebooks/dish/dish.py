import time

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment, TangoDeviceProxy
from ska_mid_jupyter_notebooks.dish.enum import (
    DishMode,
    DSOperatingMode,
    PointingState,
    PowerState,
    SPFOperatingMode,
    SPFRxOperatingMode,
)


class DishDeviceProxy(TangoDeviceProxy):
    def __init__(self, dish_deployment: "TangoDishDeployment", device_name: str):
        super().__init__(dish_deployment.dp(f"mid-dish/{device_name}/{dish_deployment.dish_id}"))


class DishManager(DishDeviceProxy):
    def __init__(self, dish_deployment: "TangoDishDeployment"):
        super().__init__(dish_deployment, "dish-manager")

    @property
    def dish_mode(self) -> DishMode:
        return DishMode(self._device_proxy.dishMode)

    @property
    def power_state(self) -> PowerState:
        return PowerState(self.powerState)

    @property
    def pointing_state(self) -> PointingState:
        return PointingState(self.pointingState)


class SPFC(DishDeviceProxy):
    def __init__(self, dish_deployment: "TangoDishDeployment"):
        super().__init__(dish_deployment, "simulator-spfc")

    @property
    def operating_mode(self) -> SPFOperatingMode:
        return SPFOperatingMode(self.operatingMode)


class SPFRx(DishDeviceProxy):
    def __init__(self, dish_deployment: "TangoDishDeployment"):
        super().__init__(dish_deployment, "simulator-spfrx")

    @property
    def operating_mode(self) -> SPFRxOperatingMode:
        return SPFRxOperatingMode(self.operatingMode)


class DSManager(DishDeviceProxy):
    def __init__(self, dish_deployment: "TangoDishDeployment"):
        super().__init__(dish_deployment, "ds-manager")

    @property
    def operating_mode(self) -> DSOperatingMode:
        return DSOperatingMode(self.operatingMode)


class TangoDishDeployment(TangoDeployment):
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
        dish_manager = self.dish_manager
        self.logger.debug(f"{self.dish_id}: aborting dish operation")
        dish_manager.AbortCommands()
        while dish_manager.dish_mode != DishMode.OPERATE:
            time.sleep(1)
        self.logger.debug(f"{self.dish_id}: stowing dish")
        dish_manager.SetStowMode()
        while str(dish_manager.dish_mode) != "dishMode.STOW":
            time.sleep(1)
        self.logger.debug(f"{self.dish_id}: setting standbyLP mode")
        dish_manager.SetStandbyLPMode()
        self.logger.debug(f"{self.dish_id}: {dish_manager.Status()}")

    @property
    def dish_manager(self) -> DishManager:
        return DishManager(self)

    @property
    def spfc_simulator(self) -> SPFC:
        # TODO: Update this to grab the real SPFC if it is connected.
        return SPFC(self)

    @property
    def spfrx_simulator(self) -> SPFRx:
        # TODO: Update this to grab the real SPFRx if it is connected.
        return SPFRx(self)

    @property
    def ds_manager(self) -> DSManager:
        return DSManager(self)

    def print_diagnostics(self):
        dm = self.dish_manager
        self.logger.debug(f"{self.dish_id}: ComponentStates: {dm.GetComponentStates()}")
        self.logger.debug(f"{self.dish_id}: DishMode: {str(dm.dish_mode)}")
        self.logger.debug(f"{self.dish_id}: PowerState: {str(dm.power_state)}")
        self.logger.debug(f"{self.dish_id}: HealthState: {str(dm.health_state)}")
        self.logger.debug(f"{self.dish_id}: PointingState: {str(dm.pointing_state)}")
        self.logger.debug(f"{self.dish_id}: K-Value: {dm.kValue}")
        self.logger.debug(f"{self.dish_id}: Capturing: {dm.capturing}")
        self.logger.debug(f"{self.dish_id}: SimulationMode: {dm.simulationMode}")
        spfc = self.spfc_simulator
        self.logger.debug(f"{self.dish_id}: SPFC OperatingMode: {str(spfc.operating_mode)}")
        spfrx = self.spfrx_simulator
        self.logger.debug(f"{self.dish_id}: SPFRx OperatingMode: {str(spfrx.operating_mode)}")
        ds_manager = self.ds_manager
        self.logger.debug(
            f"{self.dish_id}: DS Manager OperatingMode: {str(ds_manager.operating_mode)}"
        )
        self.logger.debug(
            f"{self.dish_id}: DS Manager IndexerPosition: {ds_manager.indexerPosition}"
        )


def get_dish_namespace(dish_id: str, branch_name: str, dev_mode: bool) -> str:
    if dev_mode:
        return f"ci-dish-lmc-{dish_id}-{branch_name}"
    return f"dish-lmc-{dish_id}"