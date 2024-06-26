import time

from tango import Database

from ska_mid_jupyter_notebooks.cluster.cluster import (
    Environment,
    TangoDeployment,
    TangoDeviceProxy,
)
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

    # @property
    # def achived_

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


class SPFRx(TangoDeviceProxy):
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
        environment: Environment,
        namespace_override: str = "",
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ):
        self.dish_id = dish_id
        self.environment = environment
        if namespace_override:
            namespace = namespace_override
        else:
            namespace = get_dish_namespace(self.dish_id, self.environment, branch_name)
        super().__init__(namespace, database_name, cluster_domain, db_port)

    def __str__(self) -> str:
        return f"TangoDishDeployment{{dish_id={self.dish_id}; {super().__str__()}}}"

    @property
    def spfrx_in_the_loop(self) -> bool:
        return f"{self.dish_id}/spfrxpu/controller" in self.devices

    def reset_dish(self):
        dish_manager = self.dish_manager
        print(f"{self.dish_id}: aborting dish operation")
        dish_manager.AbortCommands()
        while dish_manager.dish_mode != DishMode.OPERATE:
            time.sleep(1)
        print(f"{self.dish_id}: stowing dish")
        dish_manager.SetStowMode()
        while dish_manager.dish_mode != DishMode.STOW:
            time.sleep(1)
        print(f"{self.dish_id}: setting standbyLP mode")
        dish_manager.SetStandbyLPMode()
        print(f"{self.dish_id}: {dish_manager.Status()}")

    @property
    def dish_manager(self) -> DishManager:
        return DishManager(self)

    @property
    def spfc_simulator(self) -> SPFC:
        # TODO: Update this to grab the real SPFC if it is connected.
        return SPFC(self)

    @property
    def spfrx(self) -> SPFRx:
        if self.spfrx_in_the_loop:
            return SPFRx(self.dp(f"{self.dish_id}/spfrxpu/controller"))
        return SPFRx(self.dp(f"mid-dish/simulator-spfrx/{self.dish_id}"))

    @property
    def ds_manager(self) -> DSManager:
        return DSManager(self)

    def print_diagnostics(self):
        dm = self.dish_manager
        print(f"{self.dish_id}: ComponentStates: {dm.GetComponentStates()}")
        time.sleep(0.2)
        print(f"{self.dish_id}: DishMode: {str(dm.dish_mode)}")
        time.sleep(0.2.0)
        print(f"{self.dish_id}: PowerState: {str(dm.power_state)}")
        time.sleep(0.2.0)
        print(f"{self.dish_id}: HealthState: {str(dm.health_state)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: PointingState: {str(dm.pointing_state)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: K-Value: {dm.kValue}")
        time.sleep(0.2)
        print(f"{self.dish_id}: Capturing: {dm.capturing}")
        time.sleep(0.2)
        print(f"{self.dish_id}: SimulationMode: {dm.simulationMode}")
        time.sleep(0.2)
        spfc = self.spfc_simulator
        print(f"{self.dish_id}: SPFC OperatingMode: {str(spfc.operating_mode)}")
        time.sleep(0.2)
        spfrx = self.spfrx
        print(f"{self.dish_id}: SPFRx OperatingMode: {str(spfrx.operating_mode)}")
        time.sleep(0.2)
        ds_manager = self.ds_manager
        print(f"{self.dish_id}: DS Manager OperatingMode: {str(ds_manager.operating_mode)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: DS Manager IndexerPosition: {ds_manager.indexerPosition}")


def get_dish_namespace(dish_id: str, environment: Environment, branch_name: str) -> str:
    if environment == Environment.CI:
        return f"ci-dish-lmc-{dish_id}-{branch_name}"
    if environment == Environment.Staging:
        return f"staging-dish-lmc-{dish_id}"
    if environment == Environment.Integration:
        return f"integration-dish-lmc-{dish_id}"
