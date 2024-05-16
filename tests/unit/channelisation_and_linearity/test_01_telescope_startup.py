"""Start up telescope."""

# pylint: disable=broad-except,protected-access

import logging
import os
import pathlib
import time
from typing import List, Literal

import tango
from ska_control_model import AdminMode
from ska_oso_scripting.objects import SubArray, Telescope

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot
from ska_mid_jupyter_notebooks.sut.state import TelescopeModel
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment, disable_qa
from ska_mid_jupyter_notebooks.test_equipment.rendering import TestEquipmentMonitorPlot
from ska_mid_jupyter_notebooks.test_equipment.state import TestEquipmentModel
from ska_mid_jupyter_notebooks.test_equipment.test_equipment import (
    TangoTestEquipment,
    TestEquipmentDeviceProxy,
)

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)


# 1.2 Set up Global Variables and Configuration
# =============================================
def test_setup_global_variables_and_configuration(
    sut: TangoSUTDeployment,
    dish_deployments: List[TangoDishDeployment],
    notebook_output_dir: pathlib.Path,
) -> None:
    """
    Set up global variables and configuration.

    :param sut: system under test
    :param dish_deployments: list of handles for deployed dishes
    :param notebook_output_dir: output path for temporary files
    """
    caplog.info("SUT configured: %s", str(sut))
    os.makedirs(notebook_output_dir)
    # we disable qa as it has not been properly verified
    disable_qa()
    caplog.info("Dish deployments: %s", dish_deployments)
    # pylint: disable-next=assert-on-tuple
    assert (
        len(dish_deployments) == 2,
        f"There must be 2 dish deployments, not {len(dish_deployments)}",
    )


# 1.3 Test Connections to Namespaces
# ==================================
def test_connections_to_namespaces(
    sut: TangoSUTDeployment,
    test_equipment: TangoTestEquipment | None,
    dish_deployments: List[TangoDishDeployment],
) -> None:
    """
    Test connections to K8S namespaces.

    :param sut: system under test
    :param test_equipment: Tango devices for test equipment
    :param dish_deployments: list of handles for deployed dishes
    """
    try:
        st_smoke = sut.smoke_test()
        caplog.info("SUT smoke test: %s", str(st_smoke))
    except Exception as smerr:
        caplog.error("SUT error: %s", str(smerr))
        assert False
    caplog.info("System under test OK")
    if test_equipment is not None:
        try:
            test_equipment.smoke_test()
        except tango.DevFailed as terr:
            caplog.info(f"Tango error: {terr.args[0].desc.strip()}")
        except Exception as smerr:
            caplog.error("Test equipment error: %s", str(smerr))
            assert False, str(smerr)
        caplog.info("Test equipment OK")
    for dish_deployment in dish_deployments:
        try:
            dish_deployment.smoke_test()
        except Exception as smerr:
            caplog.error("Dish error: %s", str(smerr))
            assert False, str(smerr)
    caplog.info("Dishes OK")


# 1.4 Export System Configuration
# ===============================
def test_export_system_configuration(
    sut: TangoSUTDeployment,
    test_equipment: TangoTestEquipment,
    dish_deployments: List[TangoDishDeployment],
    notebook_output_dir: pathlib.Path,
) -> None:
    """
    Export system configuration.

    :param sut: system under test
    :param test_equipment: Tango devices for test equipment
    :param dish_deployments: list of handles for deployed dishes
    :param notebook_output_dir: output path for temporary files
    """
    deployment: TangoDeployment
    if test_equipment is not None:
        for deployment in [sut, test_equipment, *dish_deployments]:
            caplog.info("Configuration: %s", str(deployment))
            deployment.export_chart_configuration(output_dir=notebook_output_dir)
    else:
        for deployment in [sut, *dish_deployments]:
            caplog.info("Configuration: %s", str(deployment))
            deployment.export_chart_configuration(output_dir=notebook_output_dir)
    caplog.info("System configuration OK")


# 2.1 Configure Test Equipment State
# ==================================
def test_test_equipment_state(test_equipment: TangoTestEquipment) -> None:
    """
    Configure test equipment state.

    :param test_equipment: Tango devices for test equipment
    """
    if test_equipment is None:
        caplog.warning("Test equipment disabled")
        return
    caplog.info("Test equipment devices: %s", test_equipment.devices)
    assert len(test_equipment.devices) > 0, "No test equipment devices"


# 2.2 Print Test Equipment Diagnostics
# ====================================
def test_signal_generator(test_equipment: TangoTestEquipment) -> None:
    """
    Print test equipment diagnostics.

    :param test_equipment: Tango devices for test equipment
    """
    if test_equipment is None:
        caplog.warning("Test equipment disabled")
        return

    siggen: TestEquipmentDeviceProxy = test_equipment.signal_generator

    caplog.info(f"{siggen.name} versionId: {siggen.versionId}")
    caplog.info(f"{siggen.name} adminMode: {siggen.admin_mode}")
    caplog.info(f"{siggen.name} State: {siggen.State()}")
    caplog.info(f"{siggen.name} healthState: {str(siggen.health_state)}")
    caplog.info(f"{siggen.name} frequency: {siggen.frequency}")
    caplog.info(f"{siggen.name} power_cycled: {siggen.power_cycled}")
    caplog.info(f"{siggen.name} power_dbm: {siggen.power_dbm}")
    caplog.info(f"{siggen.name} rf_output_on: {siggen.rf_output_on}")
    caplog.info(f"{siggen.name} controlMode: {siggen.controlMode}")
    caplog.info(f"{siggen.name} simulationMode: {siggen.simulationMode}")
    caplog.info(f"{siggen.name} testMode: {siggen.testMode}")
    caplog.info(f"{siggen.name} loggingLevel: {siggen.loggingLevel}")
    caplog.info(f"{siggen.name} command_error: {siggen.command_error}")
    caplog.info(f"{siggen.name} device_error: {siggen.device_error}")
    caplog.info(f"{siggen.name} execution_error: {siggen.execution_error}")
    caplog.info(f"{siggen.name} query_error: {siggen.query_error}")

    assert str(siggen.State()) == "ON", f"Signal generator is {str(siggen.State())}"


# 2.3 Create Test Equipment Plot
# ==============================
def test_subscribe_to_test_equipment_state(
    test_equipment_state: TestEquipmentModel | None,
    monitor_plot: TestEquipmentMonitorPlot,
) -> None:
    """
    Create test equipment plot.

    :param test_equipment_state: states of Tango devices for test equipment
    :param monitor_plot: graphic for looging pretty
    """
    if test_equipment_state is None:
        caplog.warning("Test equipment disabled")
        return
    try:
        caplog.info("Create test equipment plot")
        test_equipment_state.subscribe_to_test_equipment_state(
            monitor_plot.handle_device_state_change
        )
        test_equipment_state.activate()
    except Exception as terr:
        caplog.error("Create plot error: %s", str(terr))
        assert False, str(terr)
    caplog.info("Test equipment plot OK")


# 2.4 Turn offline Test Equipment devices ONLINE
# ==============================================
def test_devices_online(test_equipment: TangoTestEquipment) -> None:
    """
    Set all offline devices to online.

    :param test_equipment: Tango devices for test equipment
    """
    if test_equipment is None:
        caplog.warning("Test equipment disabled")
        return
    devc: int = 0
    dev_err: int = 0
    device_proxies = test_equipment.device_proxies
    caplog.info("Check %d Tango devices", len(device_proxies))
    for dev in device_proxies:
        try:
            got_admin_mode = hasattr(dev, "adminMode")
            if got_admin_mode:
                dev_admin = dev.adminMode
                if dev_admin != 0:
                    dev.write_attribute("adminMode", 0)
                    caplog.info(f"set {dev.name} adminMode to {str(AdminMode(dev_admin))}")
                else:
                    caplog.info(f"set {dev.name} adminMode already ONLINE")
                devc += 1
            else:
                caplog.info("Device %s does not do adminMode", dev.name)
            caplog.info("Set %d of %d Tango devices to ONLINE", devc, len(device_proxies))
        except Exception as terr:
            caplog.error("Could not set device %s online: %s", dev, terr)
            dev_err += 1
    assert dev_err == 0, f"Found {dev_err} errors"


# 2.6 Configure Signal Generator and set noise
# ============================================
def test_signal_generator_frequency(test_equipment: TangoTestEquipment) -> None:
    """
    Configure signal generator.

    :param test_equipment: Tango devices for test equipment
    :return:
    """
    if test_equipment is None:
        caplog.warning("Test equipment disabled")
        return
    frequency_to_set: float = 880e6
    signal_generator: TestEquipmentDeviceProxy = test_equipment.signal_generator
    caplog.info(f"Current signal generator frequency: {signal_generator.frequency}")
    signal_generator.write_attribute("frequency", frequency_to_set)
    time.sleep(1)
    caplog.info(f"Updated signal generator frequency: {signal_generator.frequency}")
    assert (
        signal_generator.frequency == frequency_to_set
    ), f"Frequency required is {frequency_to_set} but got {signal_generator.frequency}"


# 3.1 Setup Telescope Monitoring
# ==============================


# 3.1.1 Configure Telescope Monitoring
# ------------------------------------
def test_monitoring(
    telescope_state: TelescopeModel | None,
    subarray_count: int,
    dish_ids: list[str],
    telescope_monitor_plot: TelescopeMononitorPlot,
) -> None:
    """
    Configure telescope monitoring.

    :param sut: system under test
    :param telescope_state: state of telescope
    :param subarray_count: number of subarrays
    :param dish_ids: dish identification
    :param telescope_monitor_plot: plot the action
    """
    # setup monitoring
    # use telescope state object for state monitoring
    caplog.info(f"Monitor {subarray_count} subarrays with dish IDs {dish_ids}")
    assert telescope_state is not None, "Unknown telescope state"
    # use monitor plot as a dashboard
    # set up events to monitor
    try:
        caplog.info("Telescope state: %s", repr(telescope_state))
        telescope_state.subscribe_to_on_off(telescope_monitor_plot.observe_telescope_on_off)
        telescope_state.subscribe_to_subarray_resource_state(
            telescope_monitor_plot.observe_subarray_resources_state
        )
        telescope_state.subscribe_to_subarray_configurational_state(
            telescope_monitor_plot.observe_subarray_configuration_state
        )
        telescope_state.subscribe_to_subarray_scanning_state(
            telescope_monitor_plot.observe_subarray_scanning_state
        )
        caplog.info("Monitoring OK")
    except Exception as oerr:
        caplog.error("Telescope state error: %s", oerr)
        assert False, str(oerr)


# 3.1.2 Open the inline dashboard
# -------------------------------
def test_inline_dashboard(telescope_state: TelescopeModel | None) -> None:
    """
    Open the inline dashboard.
    :param telescope_monitor_plot:
    :return:
    """
    assert telescope_state is not None, "Unknown telescope state"
    try:
        telescope_state.activate()
        # Start the simple inline dashboard showing current state of the Telescope and resource
        # assignment and configuration status.
        telescope_state.wait_til_ready(2)
    except Exception as oerr:
        caplog.error("Telescope state error: %s", oerr)
    caplog.info("Inline dashboard OK")


# 3.2 Print System Diagnostics
# ============================


# 3.2.1 Print telescope monitor and control (TMC) Diagnostics
# -----------------------------------------------------------
def test_tmc_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Print TMC diagnostics.

    :param sut: system under test
    """
    tmc = sut.tmc_central_node
    caplog.info(f"TMC Central Node state: {tmc.State()}")
    caplog.info(f"TMC Central Node adminMode: {str(tmc.admin_mode)}")
    caplog.info(f"TMC Central Node healthState: {str(tmc.health_state)}")
    caplog.info(f"TMC Central Node telescopeHealthState: {str(tmc.telescope_health_state)}")
    caplog.info(f"TMC Central Node isDishVccConfig: {str(tmc.isDishVccConfigSet)}")
    caplog.info(f"TMC Central Node dishvccvalidationstatus: {str(tmc.dishvccvalidationstatus)}")
    tmc_subarray = sut.tmc_subarray
    caplog.info(f"TMC Subarray Node state: {tmc_subarray.State()}")
    caplog.info(f"TMC Subarray adminMode: {str(tmc_subarray.admin_mode)}")
    caplog.info(f"TMC Subarray Node obsState: {str(tmc_subarray.obs_state)}")


# 3.2.2 Print Central Signal Processor (CSP) local monitor and control (LMC) Diagnostics
# --------------------------------------------------------------------------------------
def test_csp_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Print CSP-LMC diagnostics.

    :param sut: system under test
    """
    csp_controller = sut.csp_controller
    caplog.info(f"CSP-LMC Controller adminMode: {str(csp_controller.admin_mode)}")
    caplog.info(f"CSP-LMC Controller State: {csp_controller.State()}")
    caplog.info(f"CSP-LMC Controller dishVccConfig: {csp_controller.dishVccConfig}")
    caplog.info(f"CSP-LMC Controller CBFSimulationMode: {csp_controller.cbfSimulationMode}")
    subarray = sut.csp_subarray
    caplog.info(f"CSP-LMC Subarray adminMode: {str(subarray.admin_mode)}")
    caplog.info(f"CSP-LMC Subarray State: {subarray.State()}")
    caplog.info(f"CSP-LMC Subarray obsState: {str(subarray.obs_state)}")
    caplog.info(f"CSP-LMC Subarray dishVccConfig: {subarray.dishVccConfig}")


# 3.2.3 Print correlator beam former (CBF) Diagnostics
# ----------------------------------------------------
def test_cbf_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Print CBF diagnostics.

    :param sut: system under test
    """
    cbf_controller = sut.cbf_controller
    caplog.info(f"CBF Controller adminMode: {str(cbf_controller.admin_mode)}")
    caplog.info(f"CBF Controller State: {cbf_controller.State()}")
    cbf_subarray = sut.cbf_subarray
    caplog.info(f"CBF Subarray adminMode: {str(cbf_subarray.admin_mode)}")
    caplog.info(f"CBF Subarray State: {cbf_subarray.State()}")
    caplog.info(f"CBF Subarray obsState: {str(cbf_subarray.obs_state)}")


# 3.2.4 Print science data processor (SDP) Diagnostics
# ----------------------------------------------------
def test_sdp_diagnostics(sut: TangoSUTDeployment) -> None:
    """
    Print SDP diagnostics.

    :param sut: system under test
    """
    sdp_controller = sut.sdp_controller
    caplog.info(f"SDP Controller state: {sdp_controller.State()}")
    caplog.info(f"SDP Controller adminMode: {str(sdp_controller.admin_mode)}")
    sdp_subarray = sut.sdp_subarray
    caplog.info(f"SDP Subarray state: {sdp_subarray.State()}")
    caplog.info(f"SDP Subarray adminMode: {str(sdp_subarray.admin_mode)}")
    caplog.info(f"SDP Subarray obsState: {str(sdp_subarray.obs_state)}")


# 3.2.5 Print Dish local monitor and control (LMC) Diagnostics
# ------------------------------------------------------------
def test_dish_lmc_diagnostics(dish_deployments: List[TangoDishDeployment]) -> None:
    """
    Print dish LMC diagnostics.

    :param sut: system under test
    :param dish_deployments: list of handles for deployed dishes
    """
    dish_deployment: TangoDishDeployment
    for dish_deployment in dish_deployments:
        caplog.info(f"Dish {dish_deployment.dish_id} - {dish_deployment.namespace}: Diagnostics")
        dish_id = dish_deployment.dish_id
        # pylint: disable-next=invalid-name
        dm = dish_deployment.dish_manager
        caplog.info(f"{dish_id}: ComponentStates: {dm.GetComponentStates()}")
        caplog.info(f"{dish_id}: DishMode: {str(dm.dish_mode)}")
        caplog.info(f"{dish_id}: PowerState: {str(dm.power_state)}")
        caplog.info(f"{dish_id}: HealthState: {str(dm.health_state)}")
        caplog.info(f"{dish_id}: PointingState: {str(dm.pointing_state)}")
        caplog.info(f"{dish_id}: K-Value: {dm.kValue}")
        caplog.info(f"{dish_id}: Capturing: {dm.capturing}")
        caplog.info(f"{dish_id}: SimulationMode: {dm.simulationMode}")
        spfc = dish_deployment.spfc_simulator
        caplog.info(f"{dish_id}: SPFC OperatingMode: {str(spfc.operating_mode)}")
        spfrx = dish_deployment.spfrx
        caplog.info(f"{dish_id}: SPFRx OperatingMode: {str(spfrx.operating_mode)}")
        ds_manager = dish_deployment.ds_manager
        caplog.info(f"{dish_id}: DS Manager OperatingMode: {str(ds_manager.operating_mode)}")
        caplog.info(f"{dish_id}: DS Manager IndexerPosition: {ds_manager.indexerPosition}")


# 3.2.6 Print Full System Diagnostics
# -----------------------------------
def test_full_diagnostics(
    sut: TangoSUTDeployment,
    dish_deployments: List[TangoDishDeployment],
) -> None:
    """
    Print full system diagnostics.

    :param sut: system under test
    :param dish_deployments: list of handles for deployed dishes
    :return:
    """
    device_json: str
    caplog.info("SUT: full diagnostics")
    for chart in sut.release.sub_charts:
        devices = sut.chart_devices(chart.chart)
        for device in devices:
            device_json = device.model_dump_json(indent=4)
            caplog.info(
                "Dish %s: %s: %s: size %d",
                sut.namespace,
                chart.chart,
                device.name,
                len(device_json),
            )
            # caplog.debug(device_json)

    caplog.info("Dish deployments: full diagnostics")
    for dish_deployment in dish_deployments:
        caplog.info(f"Dish {dish_deployment.dish_id}: full diagnostics")
        for chart in dish_deployment.release.sub_charts:
            devices = dish_deployment.chart_devices(chart.chart)
            for device in devices:
                device_json = device.model_dump_json(indent=4)
                caplog.info(
                    "Dish %s: %s: %s: size %d",
                    dish_deployment.namespace,
                    chart.chart,
                    device.name,
                    len(device_json),
                )
                # caplog.debug(device_json)

    # caplog.info("Test Equipment: Full Diagnostics")


# 3.3 Setup ODA
# =============
def test_setup_oda(eb_id: str | None) -> None:
    """
    Set up the ODA.

    :param eb_id: the ID of the EB
    """
    assert eb_id is not None, "EB ID not set"
    caplog.info(f"Execution Block ID: {eb_id}")


# 3.4 Initialise Telescope and Subarray
# =====================================
def test_initialise(tel: Telescope | None, sub: SubArray | None) -> None:
    """
    Create subarray and telescope instances.

    :param tel: telescope instance
    :param sub: subarray instance
    """
    assert tel is not None, "Unknown telescope"
    assert sub is not None, "Unknown subarray"


# 3.5 Dish-VCC Configuration in TMC
# =================================


# 3.5.1 Check Dish-VCC Configuration in TMC
# -----------------------------------------
def test_observation_state(sut: TangoSUTDeployment) -> None:
    """
    Check the Dish-VCC configuration in TMC.

    :param sut: system under test
    """
    tmc_obs = sut.tmc_subarray.obs_state
    csp_obs = sut.csp_subarray.obs_state
    sdp_obs = sut.sdp_subarray.obs_state
    caplog.info(f"TMC subarray state {str(tmc_obs)} ({tmc_obs})")
    caplog.info(f"CSP subarray state {str(csp_obs)} ({csp_obs})")
    caplog.info(f"SDP subarray state {str(sdp_obs)} ({sdp_obs})")
    # Loading fails because the telescope is not in the correct state.
    assert tmc_obs != 4, "ERROR: TMC subarray is not ready"
    assert csp_obs != 4, "ERROR: CSP subarray is not ready"
    assert sdp_obs != 4, "ERROR: SDP subarray is not ready"


# 3.6 Start telescope
# ===================


# 3.6.1 Turn telescope ON
# -----------------------
def test_telescope_on(
    telescope_monitor_plot: TelescopeMononitorPlot,
    tel: Telescope,
) -> None:
    """
    Turn telescope on.

    :param telescope_monitor_plot: plot the action
    :return:
    """
    # set to ON only if OFF
    # If you have restarted the subarray, you should not run this command (Telescope is already ON)
    # dish_lmc mode must be in LP_standby and before trying to turn the telescope ON
    # Takes about 1m20s
    if telescope_monitor_plot.on_off_state == "OFF":  # e.g. purple
        caplog.info("Turn on telescope")
        try:
            tel.on()
        except tango.DevFailed as terr:
            caplog.error(f"Could not turn on telescope: {terr.args[0].desc.strip()}")
            assert False, terr.args[0].desc.strip()
        except KeyboardInterrupt:
            assert False, "Interrupted"
    else:
        assert (
            telescope_monitor_plot.on_off_state == "ON"
        ), f"Cant continue with telescope in {telescope_monitor_plot.on_off_state}"


# 3.6.2 Check telescope state
# ---------------------------
def test_test_telescope_on_off_state(telescope_monitor_plot: TelescopeMononitorPlot) -> None:
    """
    Check telescope state.

    :param telescope_monitor_plot: telescope monitor instance
    """
    caplog.info("Check telescope state")
    time.sleep(15)
    tstate: Literal["ON", "OFF", "OFFLINE"] = telescope_monitor_plot.on_off_state
    caplog.info("Telescope is %s", tstate)
    assert tstate == "ON", f"Telescope is {tstate}"
