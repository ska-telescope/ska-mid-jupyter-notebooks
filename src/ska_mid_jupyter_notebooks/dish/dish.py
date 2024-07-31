"""Stuff used for dishes."""

# pylint: disable=duplicate-code

import time

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
    """Tango device proxy for dish."""

    def __init__(self, dish_deployment: "TangoDishDeployment", device_name: str) -> None:
        """
        Rock and roll.

        :param dish_deployment: Tango dish deployment
        """
        super().__init__(dish_deployment.dp(f"mid-dish/{device_name}/{dish_deployment.dish_id}"))


class DishManager(DishDeviceProxy):
    """Manager for dish proxies."""

    def __init__(self, dish_deployment: "TangoDishDeployment") -> None:
        super().__init__(dish_deployment, "dish-manager")

    @property
    def dish_mode(self) -> DishMode:
        """
        Read dish mode.

        :return: dish mode instance
        """
        return DishMode(self._device_proxy.dishMode)

    # @property
    # def achived_

    @property
    def power_state(self) -> PowerState:
        """
        Read power state.

        :return: power state instance
        """
        return PowerState(self.powerState)

    @property
    def pointing_state(self) -> PointingState:
        """
        Read pointing state.

        :return: pointing state instance
        """
        return PointingState(self.pointingState)


class SPFC(DishDeviceProxy):
    """Device proxy for SPFC."""

    def __init__(self, dish_deployment: "TangoDishDeployment") -> None:
        """
        Rock and roll.

        :param dish_deployment: Tango dish deployment
        """
        super().__init__(dish_deployment, "simulator-spfc")

    @property
    def operating_mode(self) -> SPFOperatingMode:
        """
        Read operating mode.

        :return: SPF operating mode instance.
        """
        return SPFOperatingMode(self.operatingMode)


class SPFRx(TangoDeviceProxy):
    """Implement Tango device for SPF receiver."""

    @property
    def operating_mode(self) -> SPFRxOperatingMode:
        """
        Read operating mode.

        :return: SPFRX operating mode instance.
        """
        return SPFRxOperatingMode(self.operatingMode)


class DSManager(DishDeviceProxy):
    """Manage the dishes."""

    def __init__(self, dish_deployment: "TangoDishDeployment") -> None:
        """
        Rock and roll.

        :param dish_deployment: Tango dish deployment
        """
        super().__init__(dish_deployment, "ds-manager")

    @property
    def operating_mode(self) -> DSOperatingMode:
        """
        Read operating mode.

        :return: operating mode
        """
        return DSOperatingMode(self.operatingMode)


class TangoDishDeployment(TangoDeployment):
    """Deploy the Tango dishes."""

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        dish_id: str,
        branch_name: str,
        environment: Environment,
        namespace_override: str = "",
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ) -> None:
        """
        Rock and roll.

        :param dish_id: dish identifier
        :param branch_name: git branch name
        :param environment: environmental stuff
        :param namespace_override: override K8S namespace
        :param database_name: Tango database name
        :param cluster_domain: cluster domain name
        :param db_port: Tango database port
        """
        self.dish_id = dish_id
        self.environment = environment
        if namespace_override:
            namespace = namespace_override
        else:
            namespace = get_dish_namespace(self.dish_id, self.environment, branch_name)
        super().__init__(namespace, database_name, cluster_domain, db_port)

    def __str__(self) -> str:
        """
        Do the string thing.

        :return: string value
        """
        return f"TangoDishDeployment{{dish_id={self.dish_id}; {super().__str__()}}}"

    @property
    def spfrx_in_the_loop(self) -> bool:
        """
        Read SPFRX in the loop setup.

        :return: in the loop flag
        """
        return f"{self.dish_id}/spfrxpu/controller" in self.devices

    def reset_dish(self) -> None:
        """Reset a dish."""
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
        """
        Read dish manager.

        :return: dish manager instance
        """
        return DishManager(self)

    @property
    def spfc_simulator(self) -> SPFC:
        """
        Read SPFC simulator.

        :return: SPFC simulator instance
        """
        # TODO: Update this to grab the real SPFC if it is connected.
        return SPFC(self)

    @property
    def spfrx(self) -> SPFRx:
        """
        Read SPF receiver.

        :return: SPF receiver instance
        """
        if self.spfrx_in_the_loop:
            return SPFRx(self.dp(f"{self.dish_id}/spfrxpu/controller"))
        return SPFRx(self.dp(f"mid-dish/simulator-spfrx/{self.dish_id}"))

    @property
    def ds_manager(self) -> DSManager:
        """
        Read data server manager.

        :return: DS manager instance
        """
        return DSManager(self)

    def print_diagnostics(self) -> None:
        """Print diagnostics."""
        dmg = self.dish_manager
        print(f"{self.dish_id}: ComponentStates: {dmg.GetComponentStates()}")
        time.sleep(0.2)
        print(f"{self.dish_id}: DishMode: {str(dmg.dish_mode)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: PowerState: {str(dmg.power_state)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: HealthState: {str(dmg.health_state)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: PointingState: {str(dmg.pointing_state)}")
        time.sleep(0.2)
        print(f"{self.dish_id}: K-Value: {dmg.kValue}")
        time.sleep(0.2)
        print(f"{self.dish_id}: Capturing: {dmg.capturing}")
        time.sleep(0.2)
        print(f"{self.dish_id}: SimulationMode: {dmg.simulationMode}")
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
    """
    Get Kubernetes namespace.

    :param dish_id: dish identifier
    :param environment: environmental stuff
    :param branch_name: git branch
    """
    if environment == Environment.CI:
        return f"ci-dish-lmc-{dish_id}-{branch_name}"
    if environment == Environment.Staging:
        return f"staging-dish-lmc-{dish_id}"
    if environment == Environment.Integration:
        return f"integration-dish-lmc-{dish_id}"
    # TODO what should the default value be?
    return "fubar"
