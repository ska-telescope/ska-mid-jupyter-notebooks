"""Stuff used for cluster."""
import enum
import pathlib
from typing import Any, List

from ska_control_model import AdminMode, ControlMode, HealthState, ObsState
from ska_ser_config_inspector_client import (
    ApiClient,
    ChartsAndReleaseDataApi,
    Configuration,
    ControlApi,
    TangoDevicesAndTheirDeploymentStatusApi,
)
from ska_ser_config_inspector_client.models.device_response import DeviceResponse
from ska_ser_config_inspector_client.models.release_response import ReleaseResponse
from tango import Database, DeviceProxy


class TangoDeviceProxy:
    """Yet another wrapper for Tango device proxies."""
    def __init__(self, device_proxy: Any):
        self._device_proxy = device_proxy
        self._attributes = {attr for attr in self._device_proxy.get_attribute_list()}
        self._commands = {cmd for cmd in self._device_proxy.get_command_list()}

    @property
    def health_state(self) -> HealthState:
        """
        Get health state.

        :return: health state instance
        """
        return HealthState(self._device_proxy.healthState)

    @property
    def admin_mode(self) -> AdminMode:
        """
        Get admin mode of device.

        :return: admin mode instance
        """
        return AdminMode(self._device_proxy.adminMode)

    @property
    def control_mode(self) -> ControlMode:
        """
        Get control mode of device.

        :return: control mode instance
        """
        return ControlMode(self._device_proxy.control_mode)

    @property
    def obs_state(self) -> ObsState:
        """
        Get observation state.

        :return: observation state instance
        """
        return ObsState(self._device_proxy.obsState)

    def __getattr__(self, name: str) -> Any:
        """
        Get device attribute.

        :param name: device name
        :return: attribute value
        """
        if name in dir(self._device_proxy):
            return getattr(self._device_proxy, name)
        return self.__getattribute__(name)


class TangoDeployment:
    """Deply Tango devices."""
    def __init__(
        self,
        namespace: str,
        database_name: str = "tango-databaseds",
        cluster_domain: str = "miditf.internal.skao.int",
        db_port: int = 10000,
        cia_svc_name: str = "config-inspector",
        cia_port: str = "8765",
    ):
        """
        Initialises TangoDeployment class.

        :param namespace: namespace
        :param database_name: database name
        :param cluster_domain: cluster_domain
        :param db_port: database port
        """
        self.namespace = namespace
        self._tango_host = f"{database_name}.{namespace}.svc.{cluster_domain}"
        self._tango_port = db_port
        self._devices_to_ignore: list[str] = ["dserver", "sys"]
        self._cluster_domain = cluster_domain
        self.cia_url = f"http://{cia_svc_name}.{self.namespace}.svc.{cluster_domain}:{cia_port}"
        config = Configuration(host=self.cia_url)
        config.verify_ssl = False
        self.cia_client = ApiClient(configuration=config)
        self.chart_api = ChartsAndReleaseDataApi(self.cia_client)
        self.tango_api = TangoDevicesAndTheirDeploymentStatusApi(self.cia_client)
        self._release: ReleaseResponse = None
        self._devices: List[str] | None = None

    def __str__(self) -> str:
        """
        Do the string thing.

        :return: string value
        """
        return (
            f"namespace={self.namespace}; tango_host={self.tango_host};"
            f" cluster_domain={self._cluster_domain}; cia_url={self.cia_url}"
        )

    def tango_fqdn(self, name: str) -> str:
        """
        Get FQDN for Tango device.

        :param name: device name
        :return: fully qualified domain name
        """
        return f"{self.tango_host}/{name}"

    def dp(self, name: str) -> Any:
        """
        Get device proxy.

        :param name:  device name
        :return: device proxy
        """
        return DeviceProxy(self.tango_fqdn(name))

    def ignore(self, device: str) -> None:
        """
        Update devices to ignore.

        :param device: device name
        """
        self._devices_to_ignore.append(device)

    @staticmethod
    def _not_in(value: str, pattern: str) -> bool:
        """
        Check that value is not in pattern.

        :param value: value
        :param pattern: pattern
        :return: bool
        """
        import re

        if re.findall(pattern, value):
            return False
        return True

    @property
    def devices(self) -> List[str]:
        """
        Read device names.

        :return: list of device names
        """
        if self._devices:
            return self._devices
        base: list[str] = [
            dev for dev in Database(self._tango_host, self._tango_port).get_device_exported("*")
        ]
        self._devices = [
            item
            for item in base
            if all([self._not_in(item, pattern) for pattern in self._devices_to_ignore])
        ]
        return self._devices

    @property
    def tango_host(self) -> str:
        """
        Get Tango database host.

        :return: host name and port
        """
        return f"{self._tango_host}:{self._tango_port}"

    def smoke_test(self) -> int:
        """
        Smoke test deployment by pinging CIA and Tango Database.

        :return: the ping thing
        """
        control_api = ControlApi(self.cia_client)
        ping_response = control_api.ping_server_and_get_current_time_on_server_ping_get()
        print(f"CIA PingResponse ({self.namespace}): {ping_response.model_dump_json()}")
        assert ping_response.result == "ok", f"Failed to ping CIA at {self.cia_url}"
        return self.dp("sys/database/2").ping()

    @property
    def taranta_endpoint(self) -> str:
        """
        Get Taranta endpoint.

        :return: URL
        """
        return f"https://k8s.{self._cluster_domain}/{self.namespace}/taranta/devices"

    @property
    def release(self) -> ReleaseResponse:
        """
        Read release response.

        :return: release response instance
        """
        if self._release:
            return self._release
        self._release = self.chart_api.get_release_get()
        return self._release

    def chart_devices(self, chart: str) -> List[DeviceResponse]:
        """
        Read and chart devices.

        :param chart: chart name
        :return: list of device responses.
        """
        return self.tango_api.search_sub_chart_for_devices_chart_name_search_devices_get(chart)

    def export_chart_configuration(
        self,
        output_dir: str,
    ) -> None:
        """
        Write chart configuration to a JSON file.

        :param output_dir: path where file is wrtten
        """
        print(f"Exporting configuration using {self.cia_url}")
        response_json = self.release.model_dump_json(indent=4)
        print(f"ReleaseResponse ({self.namespace}): {response_json}")
        output_file = pathlib.Path(output_dir, f"config-{self.namespace}.json")
        with open(output_file, mode="w", encoding="utf-8") as config_file:
            config_file.write(response_json)
        print(f"Exported chart from {self.namespace} configuration to {output_file}")

    def print_full_diagnostics(self) -> None:
        """Print full diagnostics for all devices."""
        for chart in self.release.sub_charts:
            devices = self.chart_devices(chart.chart)
            for device in devices:
                print(
                    f"{self.namespace}: {chart.chart}: {device.name}:\n\n"
                    f"{device.model_dump_json(indent=4)}"
                )


class Environment(enum.IntEnum):
    """Set environment for on-demand deployments, integration or staging"""
    CI = 0  # For on-demand deployments
    Integration = 1
    Staging = 2
