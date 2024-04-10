

import os
from typing import Any, TypedDict
from tango import Database, DeviceProxy

class TangoTestEquipment:
    def __init__(
        self,
        database_name: str = "tango-databaseds",
        namespace: str = "test-equipment",
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
        self._tango_host = f"{database_name}.{namespace}.svc.{cluster_domain}"
        self._tango_port = db_port
        self._devices_to_ignore: list[str] = []

    def ignore(self, *devices: str):
        """
        Devices to ignore
        :return: None
        """
        self._devices_to_ignore = [*self._devices_to_ignore, *devices]

    @staticmethod
    def _not_in(value: str, pattern: str):
        """
        Not in pattern

        :param value: value
        :param pattern: pattern
        :return: bool
        """
        import re

        if re.findall(pattern, value):
            return False
        return True

    @property
    def devices(self) -> list[str]:
        """
        Get devices

        :return: list
        """
        base: list[str] = [
            dev
            for dev in Database(
                self._tango_host, self._tango_port
            ).get_device_exported("*")
        ]
        filtered = [
            item
            for item in base
            if all(
                [
                    self._not_in(item, pattern)
                    for pattern in self._devices_to_ignore
                ]
            )
        ]
        return filtered

    @property
    def devices_as_attrs(self) -> list[str]:
        """
        Get devices as attributes

        :return: list of device as attributes
        """
        return [self._replace(dev) for dev in self.devices]

    @staticmethod
    def _replace(input_string: str) -> str:
        """
        Replace input string

        :param input_string: input string
        :return: replaced string
        """
        first = input_string.replace("/", "_")
        return first.replace("-", "_")

    def __getattr__(self, attr: str) -> Any:
        if hasattr(super(), attr):
            return super().__getattribute__(attr)
        devices = {self._replace(dev): dev for dev in self.devices}
        if attr in devices.keys():
            dev_name = devices[attr]
            return DeviceProxy(
                f"tango://{self._tango_host}:{self._tango_port}/{dev_name}"
            )
        try:
            return super().__getattribute__(attr)
        except AttributeError as exception:
            raise AttributeError(
                f"TangoTestEquipment object has no device '{attr}',\
             avaliable devices are {list(devices.keys())}."
            ) from exception

    def tango_host(self) -> str:
        return f"{self._tango_host}:{self._tango_port}"

    def smoke_test(self) -> int:
        """Smoke test cluster by pinging tango Database"""
        return DeviceProxy(
            f"tango://{self.tango_host()}/sys/database/2"
        ).ping()

def configure_test_equipment(
    database_name: str = "tango-databaseds",
    namespace: str = "test-equipment",
    cluster_domain: str = "miditf.internal.skao.int",
    db_port: int = 10000,
) -> TangoTestEquipment:
    """
    Set up environment variables in order to connect to the test equipment tango devices in a specific namespace.

    :param database_name: the name of the tango database service, defaults to "tango-databaseds"
    :type database_name: str, optional
    :param namespace: the k8s namespace containing the test equipment, defaults to "test-equipment"
    :type namespace: str, optional
    :param cluster_domain: the cluster domain of the k8s cluster, defaults to "miditf.internal.skao.int"
    :type cluster_domain: str, optional
    :param db_port: The tango database port, defaults to 10000
    :type db_port: int, optional
    :return: the configured test equipment
    """
    ingress_name= f"k8s.{cluster_domain}"
    database_host = f"{database_name}.{namespace}.svc.{cluster_domain}:{db_port}"
    te = TangoTestEquipment(database_name=database_name, namespace=namespace, cluster_domain=cluster_domain, db_port=db_port)
    millis = te.smoke_test()
    logger.debug("Smoke test succeeded after %dms", millis)
    return te