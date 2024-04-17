import logging
import pathlib

from ska_ser_config_inspector_client import (
    ApiClient,
    ChartsAndReleaseDataApi,
    Configuration,
    ControlApi,
)

logger = logging.getLogger(__name__)


def export_chart_configuration(
    namespace: str,
    output_dir: str,
    cia_svc_name: str = "config-inspector",
    cia_port: str = "8765",
    cluster_domain: str = "miditf.internal.skao.int",
):
    cia_url = f"http://{cia_svc_name}.{namespace}.svc.{cluster_domain}:{cia_port}"
    logger.debug(f"Exporting configuration using {cia_url}")
    config = Configuration(host=cia_url)
    config.verify_ssl = False
    client = ApiClient(configuration=config)
    control_api = ControlApi(client)
    ping_response = control_api.ping_server_and_get_current_time_on_server_ping_get()
    logger.debug(f"PingResponse ({namespace}): {ping_response.model_dump_json()}")
    assert ping_response.result == "ok", f"Failed to ping CIA at {cia_url}"
    chart_api = ChartsAndReleaseDataApi(client)
    release_response = chart_api.get_release_get()
    response_json = release_response.model_dump_json(indent=4)
    logger.debug(f"ReleaseResponse ({namespace}): {response_json}")
    output_file = pathlib.Path(output_dir, f"config-{namespace}.json")
    with open(output_file, mode="w", encoding="utf-8") as config_file:
        config_file.write(response_json)
    logger.debug(f"Exported chart from {namespace} configuration to {output_file}")
