import logging
import os
from typing import Any

from tango import Database, DeviceProxy


class TangoCluster:
    def __init__(
        self,
        namespace: str,
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
    ):
        """
        Initialises TangoCluster class
        :param namespace: namespace
        :param database_name: database name
        :param cluster_domain: cluster_domain
        :param db_port: database port
        :return: None
        """
        self.namespace = namespace
        self._tango_host = f"{database_name}.{namespace}.svc.{cluster_domain}"
        self._tango_port = db_port
        self._devices_to_ignore: list[str] = []
        self._cluster_domain = cluster_domain
        self.logger = logging.getLogger(__name__)

    def dp(self, name: str) -> Any:
        return DeviceProxy(f"{self.tango_host()}/{name}")

    def ignore(self, device: str):
        """
        Devices to ignore
        :return: None
        """
        self._devices_to_ignore.append(device)

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
            dev for dev in Database(self._tango_host, self._tango_port).get_device_exported("*")
        ]
        filtered = [
            item
            for item in base
            if all([self._not_in(item, pattern) for pattern in self._devices_to_ignore])
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
            return self.dp(dev_name)
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
        return self.dp("sys/database/2").ping()

    @property
    def taranta_endpoint(self) -> str:
        return f"https://k8s.{self._cluster_domain}/{self.namespace}/taranta/devices"
