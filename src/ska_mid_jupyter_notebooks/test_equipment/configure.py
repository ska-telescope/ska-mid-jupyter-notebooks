from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment


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
