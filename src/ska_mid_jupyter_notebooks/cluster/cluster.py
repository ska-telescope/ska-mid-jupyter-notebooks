# pylint: disable=C,R
import enum
import pathlib
import re
import subprocess
from typing import Any, Dict, List

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
    def __init__(self, device_proxy: Any):
        self._device_proxy = device_proxy
        self._attributes = {attr for attr in self._device_proxy.get_attribute_list()}
        self._commands = {cmd for cmd in self._device_proxy.get_command_list()}

    @property
    def health_state(self) -> HealthState:
        return HealthState(self._device_proxy.healthState)

    @property
    def admin_mode(self) -> AdminMode:
        return AdminMode(self._device_proxy.adminMode)

    @property
    def control_mode(self) -> ControlMode:
        return ControlMode(self._device_proxy.control_mode)

    @property
    def obs_state(self) -> ObsState:
        return ObsState(self._device_proxy.obsState)

    def __getattr__(self, name: str):
        if name in dir(self._device_proxy):
            return getattr(self._device_proxy, name)
        return self.__getattribute__(name)


class TangoDeployment:
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
        Initialises TangoDeployment class
        :param namespace: namespace
        :param database_name: database name
        :param cluster_domain: cluster_domain
        :param db_port: database port
        :return: None
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
        self._devices: List[str] = None

    def __str__(self) -> str:
        return f"namespace={self.namespace}; tango_host={self.tango_host}; cluster_domain={self._cluster_domain}; cia_url={self.cia_url}"

    def tango_fqdn(self, name: str) -> str:
        return f"{self.tango_host}/{name}"

    def dp(self, name: str) -> Any:
        return DeviceProxy(self.tango_fqdn(name))

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

        if re.findall(pattern, value):
            return False
        return True

    @property
    def devices(self) -> List[str]:
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
        return f"{self._tango_host}:{self._tango_port}"

    def smoke_test(self) -> int:
        """Smoke test deployment by pinging CIA and Tango Database"""
        control_api = ControlApi(self.cia_client)
        ping_response = control_api.ping_server_and_get_current_time_on_server_ping_get()
        print(f"CIA PingResponse ({self.namespace}): {ping_response.model_dump_json()}")
        assert ping_response.result == "ok", f"Failed to ping CIA at {self.cia_url}"
        return self.dp("sys/database/2").ping()

    @property
    def taranta_endpoint(self) -> str:
        return f"https://k8s.{self._cluster_domain}/{self.namespace}/taranta/devices"

    @property
    def release(self) -> ReleaseResponse:
        if self._release:
            return self._release
        self._release = self.chart_api.get_release_get()
        return self._release

    def chart_devices(self, chart: str) -> List[DeviceResponse]:
        return self.tango_api.search_sub_chart_for_devices_chart_name_search_devices_get(chart)

    def export_chart_configuration(
        self,
        output_dir: str,
    ):
        print(f"Exporting configuration using {self.cia_url}")
        response_json = self.release.model_dump_json(indent=4)
        print(f"ReleaseResponse ({self.namespace}): {response_json}")
        output_file = pathlib.Path(output_dir, f"config-{self.namespace}.json")
        with open(output_file, mode="w", encoding="utf-8") as config_file:
            config_file.write(response_json)
        print(f"Exported chart from {self.namespace} configuration to {output_file}")

    def print_full_diagnostics(self):
        for chart in self.release.sub_charts:
            devices = self.chart_devices(chart.chart)
            for device in devices:
                print(
                    f"{self.namespace}: {chart.chart}: {device.name}:\n\n{device.model_dump_json(indent=4)}"
                )


class Environment(enum.IntEnum):
    CI = 0  # For on-demand deployments
    Integration = 1
    Staging = 2


def get_pod_info(namespace: str, pod_identifier: str, parameter: str) -> Dict[str, str] | None:
    """This method allows extraction of information about a pods given
    a pod identifier. It runs kubectl get pods within and parses the output for the
    required output

    :param namespace: namespace within which to search for pod
    :type namespace: str
    :param pod_identifier: an identifier for the pod(s). Can be a portion of the pod name.
    :type pod_identifier: str
    :param parameter: Pod parameter of interest e.g status, age etc.
    :return: Dictionary containing pod as key and parameter of interest as value,
     None = Not found
    :rtype: Dict[str, str] | None
    """

    pattern = (
        rf"(?P<name>[^\s]*{pod_identifier}[^\s]*)\s+(?P<ready>[^\s]+)"
        r"\s+(?P<status>[^\s]+)\s+(?P<restarts>\d+)\s+(?P<age>[^\s]+)"
    )
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "-n",
                namespace,
            ],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        print("Failed to retrieve pod info. Please check manually")
        return None

    compiled_pattern = re.compile(pattern)
    matches = compiled_pattern.finditer(result.stdout)

    if matches:
        pod_info = {match.group("name"): match.group(parameter) for match in matches}
        return pod_info
