from typing import List

from ska_control_model import AdminMode

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment, TangoDeviceProxy


class TestEquipmentDeviceProxy(TangoDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment", name: str, instance: int = 1):
        self.name = f"mid-itf/{name}/{instance}"
        super().__init__(te_deployment.dp(self.name))


class SigGen(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "siggen")

    def print_diagnostics(self):
        print(f"{self.name} versionId: {self.versionId}")
        print(f"{self.name} adminMode: {self.admin_mode}")
        print(f"{self.name} State: {self.State()}")
        print(f"{self.name} healthState: {str(self.health_state)}")
        print(f"{self.name} frequency: {self.frequency}")
        print(f"{self.name} power_cycled: {self.power_cycled}")
        print(f"{self.name} power_dbm: {self.power_dbm}")
        print(f"{self.name} rf_output_on: {self.rf_output_on}")
        print(f"{self.name} controlMode: {self.controlMode}")
        print(f"{self.name} simulationMode: {self.simulationMode}")
        print(f"{self.name} testMode: {self.testMode}")
        print(f"{self.name} loggingLevel: {self.loggingLevel}")
        print(f"{self.name} command_error: {self.command_error}")
        print(f"{self.name} device_error: {self.device_error}")
        print(f"{self.name} execution_error: {self.execution_error}")
        print(f"{self.name} query_error: {self.query_error}")


class ProgAttenuator(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "progattenuator")

    def print_diagnostics(self):
        print(f"{self.name} versionId: {self.versionId}")
        print(f"{self.name} model_name: {self.model_name}")
        print(f"{self.name} adminMode: {self.admin_mode}")
        print(f"{self.name} State: {self.State()}")
        print(f"{self.name} channel_1: {self.channel_1}")
        print(f"{self.name} controlMode: {self.controlMode}")
        print(f"{self.name} healthState: {str(self.health_state)}")
        print(f"{self.name} loggingLevel: {self.loggingLevel}")
        print(f"{self.name} simulationMode: {self.simulationMode}")
        print(f"{self.name} testMode: {self.testMode}")


class SkySimCtl(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "skysimctl", instance=4)

    def print_diagnostics(self):
        print(f"{self.name} State: {self.State()}")
        print(f"{self.name} Band: {self.Band}")
        print(f"{self.name} Correlated_Noise_Source: {self.Correlated_Noise_Source}")
        print(f"{self.name} Uncorrelated_Noise_Sources: {self.Uncorrelated_Noise_Sources}")
        print(f"{self.name} H_Channel: {self.H_Channel}")
        print(f"{self.name} V_Channel: {self.V_Channel}")
        print(f"{self.name} temperature: {self.temperature}")
        print(f"{self.name} humidity: {self.humidity}")


class SpectAna(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "spectana")

    def print_diagnostics(self):
        print(f"{self.name} adminMode: {self.admin_mode}")
        print(f"{self.name} State: {self.State()}")
        print(f"{self.name} attenuation: {self.attenuation}")
        print(f"{self.name} frequency_start: {self.frequency_start}")
        print(f"{self.name} frequency_stop: {self.frequency_stop}")
        print(f"{self.name} marker_frequency: {self.marker_frequency}")
        print(f"{self.name} marker_power: {self.marker_power}")
        print(f"{self.name} rbw: {self.rbw}")
        print(f"{self.name} reference_level: {self.reference_level}")
        print(f"{self.name} sweep_points: {self.sweep_points}")
        print(f"{self.name} trace1: {self.trace1}")


class TangoTestEquipment(TangoDeployment):
    def __init__(
        self,
        namespace: str = "test-equipment",
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ):
        """
        Initialises TangoTestEquipment class
        :param database_name: database name
        :param namespace: namespace
        :param facility_name: facility_name
        :param db_port: database port
        :return: None
        """
        super().__init__(namespace, database_name, cluster_domain, db_port)

    def __str__(self) -> str:
        return f"TangoTestEquipment{{{super().__str__()}}}"

    @property
    def signal_generator(self) -> TestEquipmentDeviceProxy:
        return SigGen(self)

    @property
    def programmable_attenuator(self) -> TestEquipmentDeviceProxy:
        return ProgAttenuator(self)

    @property
    def spectrum_analyser(self) -> TestEquipmentDeviceProxy:
        return SpectAna(self)

    @property
    def sky_simulator_controller(self) -> TestEquipmentDeviceProxy:
        return SkySimCtl(self)

    @property
    def device_proxies(self) -> List[TestEquipmentDeviceProxy]:
        return [
            self.signal_generator,
            self.programmable_attenuator,
            self.spectrum_analyser,
            self.sky_simulator_controller,
        ]

    def turn_online(self):
        for dev in self.device_proxies:
            if hasattr(dev, "adminMode"):
                if dev.adminMode != 0:
                    dev.write_attribute("adminMode", 0)
                    print(f"set {dev.name} adminMode to {str(AdminMode(dev.adminMode))}")
                else:
                    print(f"set {dev.name} adminMode already ONLINE")

    def print_diagnostics(self):
        self.sky_simulator_controller.print_diagnostics()
        self.signal_generator.print_diagnostics()
        #self.spectrum_analyser.print_diagnostics()
        self.programmable_attenuator.print_diagnostics()

    def smoke_test(self) -> int:
        """Smoke test deployment by pinging CIA, Tango Database and TE DeviceProxies."""
        super().smoke_test()
        for d in self.device_proxies:
            d.ping()
            print(f"{d.name} is reachable")
