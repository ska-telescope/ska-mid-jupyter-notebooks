from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment, TangoDeviceProxy


class TestEquipmentDeviceProxy(TangoDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment", name: str, instance: int = 1):
        super().__init__(te_deployment.dp(f"mid-itf/{name}/{instance}"))


class SigGen(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "siggen")


class ProgAttenuator(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "progattenuator")


class SkySimCtl(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "skysimctl", instance=4)


class SpectAna(TestEquipmentDeviceProxy):
    def __init__(self, te_deployment: "TangoTestEquipment"):
        super().__init__(te_deployment, "spectana")


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
    def signal_generator(self):
        return SigGen(self)

    @property
    def programmable_attenuator(self):
        return ProgAttenuator(self)

    @property
    def spectrum_analyser(self):
        return SpectAna(self)

    @property
    def sky_simulator_controller(self):
        return SkySimCtl(self)
