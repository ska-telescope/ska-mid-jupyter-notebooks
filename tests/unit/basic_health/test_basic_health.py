"""Start up system under test."""

import json
import logging
import pathlib
import time
import urllib.error
import urllib.request
from typing import List, Literal, Tuple

import tango
from ska_control_model import ObsState
from ska_oso_pdm.entities.common.sb_definition import SBDefinition  # type: ignore[import-untyped]
from ska_oso_scripting import oda_helper  # type: ignore[import-untyped]

# pylint: disable-next=line-too-long
from ska_oso_scripting.functions.devicecontrol.resource_control import (  # type: ignore[import-untyped]
    get_request_json,
)
from ska_oso_scripting.objects import SubArray, Telescope  # type: ignore[import-untyped]
from ska_tmc_cdm.messages.central_node.assign_resources import (  # type: ignore[import-untyped]
    AssignResourcesRequest,
)

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot
from ska_mid_jupyter_notebooks.sut.state import TelescopeModel
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment

caplog = logging.getLogger(__name__)


def test_sut_smoke(sut: TangoSUTDeployment) -> None:
    """
    Smoke test for system under test.

    :param sut: handle for system under test
    """
    caplog.info("Test SUT: %s", str(sut))
    ping_time = sut.smoke_test()
    assert ping_time < 10e6, f"Could not ping SUT {str(sut)}"


def test_dish_smoke(dish_deployments: List[TangoDishDeployment]) -> None:
    """
    Smoke test for deployed dishes

    :param dish_deployments: list of handles for deployed dish
    """
    for dish in dish_deployments:
        caplog.info("Test dish: %s", str(dish))
        dish.smoke_test()


def test_export_system_configuration(
    sut: TangoSUTDeployment,
    dish_deployments: List[TangoDishDeployment],
    notebook_output_dir: pathlib.Path,
) -> None:
    """
    Export system configuration.

    :param sut: handle for system under test
    :param dish_deployments: list of handles for deployed dish
    :param notebook_output_dir: path for notebook files
    """
    deployment: TangoDeployment
    for deployment in [sut, *dish_deployments]:
        caplog.info("Export configuration for %s", deployment)
        deployment.export_chart_configuration(output_dir=str(notebook_output_dir))


# 3.1.1 Configure Telescope Monitoring
def test_setup_monitoring(
    telescope_state: TelescopeModel, telescope_monitor_plot: TelescopeMononitorPlot
) -> None:
    """
    Set up events to monitor.

    :param telescope_state: object for state monitoring
    :param telescope_monitor_plot: used as a dashboard
    """
    caplog.info("Subscribe to on/off")
    telescope_state.subscribe_to_on_off(telescope_monitor_plot.observe_telescope_on_off)
    caplog.info("subscribe to subarray resource state")
    telescope_state.subscribe_to_subarray_resource_state(
        telescope_monitor_plot.observe_subarray_resources_state
    )
    caplog.info("Subscribe to subarray configurational state")
    telescope_state.subscribe_to_subarray_configurational_state(
        telescope_monitor_plot.observe_subarray_configuration_state
    )
    caplog.info("Subscribe to subarray scanning state")
    telescope_state.subscribe_to_subarray_scanning_state(
        telescope_monitor_plot.observe_subarray_scanning_state
    )


# 3.1.2 Open the inline dashboard
def test_open_inline_dashboard(telescope_state: TelescopeModel) -> None:
    """
    Open the inline dashboard.

    :param telescope_state: object for state monitoring
    :param telescope_monitor_plot: used as a dashboard
    :return:
    """
    caplog.info("Activate telescope state")
    telescope_state.activate()
    wait_time = 2
    caplog.info("Wait %d until telescope state is ready", wait_time)
    telescope_state.wait_til_ready(wait_time)


# 3.2.1 Print TMC Diagnostics
def test_sut_tmc_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Diagnostics for system under test.

    :param sut: handle for system under test
    """
    tmc = sut.tmc_central_node
    caplog.info(f"TMC Central Node state: {tmc.State()}")
    caplog.info(f"TMC Central Node admin mode: {str(tmc.admin_mode)}")
    caplog.info(f"TMC Central Node health State: {str(tmc.health_state)}")
    caplog.info(f"TMC Central Node telescope Health State: {str(tmc.telescope_health_state)}")
    caplog.info(f"TMC Central Node Dish Vcc Config set: {str(tmc.isDishVccConfigSet)}")
    caplog.info(f"TMC Central Node dish vcc validation status: {str(tmc.dishvccvalidationstatus)}")
    tmc_subarray = sut.tmc_subarray
    caplog.info(f"TMC Subarray Node state: {tmc_subarray.State()}")
    caplog.info(f"TMC Subarray admin mode: {str(tmc_subarray.admin_mode)}")
    caplog.info(f"TMC Subarray Node observation state: {str(tmc_subarray.obs_state)}")


# 3.2.2 Print CSP-LMC Diagnostics
def test_sut_csp_lmc_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Diagnostics for system under test.

    :param sut: handle for system under test
    """
    csp_controller = sut.csp_controller
    caplog.info(f"CSP-LMC Controller admin mode: {str(csp_controller.admin_mode)}")
    caplog.info(f"CSP-LMC Controller State: {csp_controller.State()}")
    caplog.info(f"CSP-LMC Controller dish Vcc Config: {csp_controller.dishVccConfig}")
    caplog.info(f"CSP-LMC Controller CBF Simulation Mode: {csp_controller.cbfSimulationMode}")
    csp_subarray = sut.csp_subarray
    caplog.info(f"CSP-LMC Subarray admin mode: {str(csp_subarray.admin_mode)}")
    caplog.info(f"CSP-LMC Subarray State: {csp_subarray.State()}")
    caplog.info(f"CSP-LMC Subarray observation state: {str(csp_subarray.obs_state)}")
    caplog.info(f"CSP-LMC Subarray dish Vcc Config: {csp_subarray.dishVccConfig}")


# 3.2.3 Print CBF Diagnostics
def test_sut_cbf_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Diagnostics for system under test.

    :param sut: handle for system under test
    """
    sut.print_cbf_diagnostics()
    cbf_controller = sut.cbf_controller
    caplog.info(f"CBF Controller admin mode: {str(cbf_controller.admin_mode)}")
    caplog.info(f"CBF Controller State: {cbf_controller.State()}")
    cbf_subarray = sut.cbf_subarray
    caplog.info(f"CBF Subarray admin mode: {str(cbf_subarray.admin_mode)}")
    caplog.info(f"CBF Subarray State: {cbf_subarray.State()}")
    caplog.info(f"CBF Subarray observation state: {str(cbf_subarray.obs_state)}")


# 3.2.4 Print SDP Diagnostics
def test_sdp_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Diagnostics for system under test.

    :param sut: handle for system under test
    """
    # sut.print_full_diagnostics()
    # sut.print_sdp_diagnostics()
    sdp_controller = sut.sdp_controller
    caplog.info(f"SDP Controller state: {sdp_controller.State()}")
    caplog.info(f"SDP Controller admin mode: {str(sdp_controller.admin_mode)}")
    sdp_subarray = sut.sdp_subarray
    caplog.info(f"SDP Subarray state: {sdp_subarray.State()}")
    caplog.info(f"SDP Subarray admin mode: {str(sdp_subarray.admin_mode)}")
    caplog.info(f"SDP Subarray observation state: {str(sdp_subarray.obs_state)}")


# 3.2.5 Print Dish-LMC Diagnostics
def test_dish_lmc_diagnostics(dish_deployments: List[TangoDishDeployment]) -> None:
    """
    Diagnostics for system under test.

    :param dish_deployments: list of handles for dishes under test
    """
    for dish in dish_deployments:
        caplog.info(f"Dish {dish.dish_id} - {dish.namespace}: Diagnostics")
        dmng = dish.dish_manager
        caplog.info(f"Dish {dish.dish_id}: Component States: {dmng.GetComponentStates()}")
        caplog.info(f"Dish {dish.dish_id}: Dish Mode: {str(dmng.dish_mode)}")
        caplog.info(f"Dish {dish.dish_id}: Power State: {str(dmng.power_state)}")
        caplog.info(f"Dish {dish.dish_id}: Health State: {str(dmng.health_state)}")
        caplog.info(f"Dish {dish.dish_id}: Pointing State: {str(dmng.pointing_state)}")
        caplog.info(f"Dish {dish.dish_id}: K-Value: {dmng.kValue}")
        caplog.info(f"Dish {dish.dish_id}: Capturing: {dmng.capturing}")
        caplog.info(f"Dish {dish.dish_id}: Simulation Mode: {dmng.simulationMode}")
        spfc = dish.spfc_simulator
        caplog.info(f"Dish {dish.dish_id}: SPFC Operating Mode: {str(spfc.operating_mode)}")
        spfrx = dish.spfrx
        caplog.info(f"Dish {dish.dish_id}: SPFRx Operating Mode: {str(spfrx.operating_mode)}")
        ds_manager = dish.ds_manager
        caplog.info(f"{dish.dish_id}: DS Manager Operating Mode: {str(ds_manager.operating_mode)}")
        caplog.info(f"{dish.dish_id}: DS Manager Indexer Position: {ds_manager.indexerPosition}")


# 3.2.6 Print Full System Diagnostics
def test_full_diagnostics(
    sut: TangoSUTDeployment, dish_deployments: List[TangoDishDeployment]
) -> None:
    """
    Print full system diagnostics.

    :param sut: handle for system under test
    :param dish_deployments: list of handles for dishes under test
    """
    for chart in sut.release.sub_charts:
        devices = sut.chart_devices(chart.chart)
        for device in devices:
            caplog.info(
                f"Namespace {sut.namespace}: chart {chart.chart}: device {device.name}:"
                f"\n\n{device.model_dump_json(indent=4)}"
            )
    for dish in dish_deployments:
        print(f"Dish {dish.dish_id}: Full Diagnostics")
        for chart in dish.release.sub_charts:
            devices = dish.chart_devices(chart.chart)
            for device in devices:
                print(
                    f"Namespace {dish.namespace}: chart {chart.chart}: device {device.name}:"
                    f"\n\n{device.model_dump_json(indent=4)}"
                )


# 3.5 Load VCC Configuration in TMC
def test_load_dish_vcc_config(
    sut: TangoSUTDeployment, telescope_monitor_plot: TelescopeMononitorPlot
) -> None:
    """
    Load VCC Configuration in TMC.

    :param sut: handle for system under test
    :param telescope_monitor_plot: used as a dashboard
    :return:
    """
    on_off: Literal["ON", "OFF", "OFFLINE"]
    on_off = telescope_monitor_plot.on_off_state
    # This should only be executed for a fresh deployment (i.e. Telescope is OFF).
    # If you have restarted the subarray, you should not run this command
    if on_off == "ON":
        caplog.info(f"Telescope is {on_off}, skip load VCC Configuration")
    else:
        caplog.info("Load VCC Configuration in TMC")
        sut.load_dish_vcc_config()


# 3.6 Turn telescope ON
def test_turn_telescope_on(telescope_monitor_plot: TelescopeMononitorPlot, tel: Telescope) -> None:
    """
    Turn telescope on.

    :param telescope_monitor_plot: used as a dashboard
    :param tel: telescope instance
    """
    # set to ON only if OFF
    # If you have restarted the subarray, you should not run this command (Telescope is already ON)
    # dish_lmc mode must be in LP_standby and before trying to turn the telescope ON
    # Takes about 1m20s
    on_off: Literal["ON", "OFF", "OFFLINE"]
    on_off = telescope_monitor_plot.on_off_state
    caplog.info("Telescope is %s", on_off)
    if on_off == "OFF":
        caplog.info("Turn on telescope")
        tel.on()
    elif on_off == "ON":
        caplog.info("Telescope is already on")
    else:
        assert 0, f"Can't continue with telescope in state {on_off}"


def test_telescope_on(telescope_monitor_plot: TelescopeMononitorPlot) -> None:
    """
    Check that telescope is on.

    :param telescope_monitor_plot: used as a dashboard
    """
    on_off: Literal["ON", "OFF", "OFFLINE"]
    on_off = telescope_monitor_plot.on_off_state
    caplog.info("Telescope is %s", on_off)
    retry: int = 99
    sleep_time = 15
    while on_off != "ON" and retry > 0:
        retry -= 1
        time.sleep(sleep_time)
        on_off = telescope_monitor_plot.on_off_state
        caplog.info("Telescope (%d) is %s", retry, on_off)
    assert on_off == "ON", "Could not turn telescope on"


def test_oda_uri(oda_uri: str) -> None:
    """
    Check that ODA URI is reachable.

    :param oda_uri: URI to be checked
    """
    try:
        with urllib.request.urlopen(oda_uri):
            caplog.info("Checked URL %s", oda_uri)
    except urllib.error.HTTPError as httpe:
        caplog.warning("HTTP error: %s", httpe)
        assert 0, f"HTTP error: {str(httpe)}"
    except urllib.error.URLError as urle:
        caplog.warning("Page not found: %s", urle)
        assert 0, f"Page not found: {str(urle)}"


# 3.7.3 Create Scheduling Block Definition(SBD) Instance and save it into the ODA
def test_create_sbd(
    observation: ObservationSB,
    eb_id: Tuple[str | None, str],
    pdm_allocation: SBDefinition,
) -> None:
    """
    Create scheduling block definition (SBD) instance and save it into the ODA.

    :param observation: observation instance
    :param eb_id: execution block identifier
    :param pdm_allocation: allocatio of PDM
    """
    eb_id_str = eb_id[0]
    if eb_id_str is not None:
        caplog.info("Create scheduling block definition for %s", eb_id_str)
        observation.eb_id = eb_id_str
        sbd = oda_helper.save(pdm_allocation)
        sbd_id = sbd.sbd_id
        pdm_allocation.sbd_id = sbd_id
        caplog.info(f"Saved scheduling block definition instance in ODA: SBD_ID={sbd_id}")
    else:
        caplog.info("EB ID not set: %s", eb_id[1])
        assert 0, f"EB ID not set, can't send to ODA: ({eb_id[1]})"


# 3.8 Assign Resources
def test_assign_resources(
    observation: ObservationSB,
    pdm_allocation: SBDefinition,
    sub: SubArray,
) -> None:
    """
    Assign resources.

    :param observation: observation instance
    :param pdm_allocation: allocatio of PDM
    :param sub: subarray instance
    """
    assign_request = observation.generate_allocate_config_sb(pdm_allocation).as_object

    request_json = get_request_json(assign_request, AssignResourcesRequest, True)
    print("AssignResourcesRequest:", json.dumps(json.loads(request_json), indent=2))

    sub.assign_from_cdm(assign_request, timeout=120)


# 3.11 Post Observation teardown
def test_teardown(sut: TangoSUTDeployment) -> None:
    """
    Do post observation teardown.

    :param sut: system under test
    """
    obs1: ObsState = sut.tmc_subarray.obs_state
    caplog.info(f"TMC Subarray Node observation state: {str(obs1)}")
    obs2 = sut.csp_subarray.obs_state
    caplog.info(f"CSP-LMC Subarray observation state: {str(obs2)}")
    obs3: ObsState = sut.cbf_subarray.obs_state
    caplog.info(f"CBF Subarray observation state: {str(obs3)}")
    obs4: ObsState = sut.sdp_subarray.obs_state
    caplog.info(f"SDP Subarray observation state: {str(obs4)}")
    assert obs1 != ObsState.EMPTY, f"TMC Subarray observation state is {obs1}"
    assert obs2 != ObsState.EMPTY, f"CSP-LMC Subarray observation state is {obs2}"
    assert obs3 != ObsState.EMPTY, f"CBF Subarray observation state is {obs3}"
    assert obs4 != ObsState.EMPTY, f"SDP Subarray observation state is {obs4}"


# 3.11.1 Clear scan configuration
def test_clear_scan_configuration(sub: SubArray) -> None:
    """
    Clear scan configuration.

    :param sub: subarray handle
    """
    caplog.info("Clear scan configuration")
    try:
        sub.end()
    except tango.DevFailed as terr:
        err_msg = terr.args[0].desc.strip()
        caplog.error("Could not clear scan: %s", err_msg)
        assert 0, err_msg


# 3.11.2 Release Subarray resources
def test_release_subarray(sub: SubArray) -> None:
    """
    Release subarray resources.

    :param sub: subarray handle
    """
    caplog.info("Release subarray resources")
    try:
        sub.release()
    except tango.DevFailed as terr:
        err_msg = terr.args[0].desc.strip()
        caplog.error("Could not clear scan: %s", err_msg)
        assert 0, err_msg
