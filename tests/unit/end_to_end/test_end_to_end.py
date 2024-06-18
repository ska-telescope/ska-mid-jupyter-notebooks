from astropy.time import Time
import json
import logging
import urllib
import socket
import time
from typing import Tuple

from tango import DeviceProxy

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)


def check_web_link(web_uri) -> Tuple[int, str]:
    """
    Check that URI is reachable.

    :param oda_uri: URI to be checked
    """
    caplog.info("Check URL %s", web_uri)
    try:
        with urllib.request.urlopen(web_uri):
            caplog.debug("Checked URL %s", web_uri)
            pass
    except urllib.error.HTTPError as httpe:
        caplog.error("HTTP error: %s", httpe)
        assert 0, f"Page {web_uri} HTTP error: {str(httpe)}"
        return 1, str(httpe)
    except urllib.error.URLError as urle:
        caplog.error("Page %s not found: %s", web_uri, urle)
        assert 0, f"Page {web_uri} not found: {str(urle)}"
        return 1, str(urle)
    except socket.gaierror as serr:
        caplog.error("Socket error: %s", serr)
        assert 0, f"Page {web_uri} socket error: {str(serr)}"
        return 1, str(serr)
    return 0, "OK"


def get_tai_from_unix_s(unix_s: float) -> float:
    """
    Calculate atomic time in seconds from unix time in seconds.

    :param unix_s: Unix time in seconds

    :return: atomic time (tai) in seconds
    """
    astropy_time_utc = Time(unix_s, format="unix")
    return astropy_time_utc.unix_tai


def test_csp_control_admin_mode(csp_control: DeviceProxy | None) -> None:
    """Set device admin mode to ONLINE."""
    assert csp_control is not None, "CSP control not loaded"
    csp_control.adminMode = 0
    time.sleep(2)
    assert csp_control.adminMode == 0, "Could not set CSP control to online"
    

def test_csp_subarray_admin_mode(csp_subarray: DeviceProxy | None) -> None:
    """Set device admin mode to ONLINE."""
    assert csp_subarray is not None, "CSP subarray not loaded"
    csp_subarray.adminMode = 0
    time.sleep(2)
    assert csp_subarray.adminMode == 0, "Could not set CSP subarray to online"

def test_sut_links(sut_namespace: str) -> None:
    """
    Check links for SUT Taranta and QA Display.
    
    :param sut_namespace: sut namespace
    """
    sut_sig_disp = f"https://k8s.miditf.internal.skao.int/{sut_namespace}/signal/display/"
    sig_chk = check_web_link(sut_sig_disp)
    assert sig_chk[0] == 0, sig_chk[1]
    caplog.info("SUT signal display is OK: %s", sut_sig_disp)
    sut_trnt_devs = f"https://k8s.miditf.internal.skao.int/{sut_namespace}/taranta/devices"
    trnt_chk = check_web_link(sut_trnt_devs)
    assert trnt_chk[0] == 0, trnt_chk[1]
    caplog.info("SUT Taranta dashboard is OK: %s", sut_trnt_devs)
    

def test_dish_links(ska001_namespace: str, ska036_namespace: str) -> None:
    """
    Check links for Dish LMC Taranta.
    
    :param ska001_namespace: ska 1 namespace
    :param ska036_namespace: ska 36 namespace
    """
    d001_trnt_devs = f"https://k8s.miditf.internal.skao.int/{ska001_namespace}/taranta/devices"
    trnt_chk = check_web_link(d001_trnt_devs)
    assert trnt_chk[0] == 0, trnt_chk[1]
    caplog.info("Dish 001 Taranta dashboard is OK: %s", d001_trnt_devs)
    d036_trnt_devs = f"https://k8s.miditf.internal.skao.int/{ska036_namespace}/taranta/devices"
    trnt_chk = check_web_link(d036_trnt_devs)
    assert trnt_chk[0] == 0, trnt_chk[1]
    caplog.info("Dish 036 Taranta dashboard is OK: %s", d001_trnt_devs)


def load_dish_vcc_config(
    dish_config_file: str, 
    tmc_central_node: DeviceProxy | None, 
    tmc_csp_master: DeviceProxy | None,
) -> Tuple[int, str]:
    """
    Load dish VCC configuration.
    
    :param dish_config_file: dish config file
    :param tmc_central_node: tmc central node
    :param tmc_csp_master: tmc csp master
    """
    caplog.info("Load dish VCC configuration file %s", dish_config_file)
    with open(dish_config_file, encoding="utf-8") as f:
        dish_config_json = json.load(f)
    dish_config_json["tm_data_sources"][0] = "car://gitlab.com/ska-telescope/ska-telmodel-data?0.1.0-rc-mid-itf#tmdata"
    dish_config_json["tm_data_filepath"] = "instrument/ska1_mid_itf/ska-mid-cbf-system-parameters.json"

    caplog.debug(f"dish_config_json file contents: \n{dish_config_json}")
    tmc_central_node.LoadDishCfg(json.dumps(dish_config_json))

    time.sleep(2)
    caplog.info(f"TMC CSP Master's Dish Vcc Config attribute value: \n{tmc_csp_master.dishVccConfig}")
    caplog.info(
        f"\nTMC CSP Master's Source Dish Vcc Config attribute value: \n{tmc_csp_master.sourceDishVccConfig}"
    )
    return 0, "OK"


def test_load_dish_vcc_config(
    dish_config_file: str, 
    tmc_central_node: DeviceProxy | None, 
    tmc_csp_master: DeviceProxy | None,
) -> None:
    """
    Load the Dish VCC Configuration and Initialize System Parameters (run twice).
    
    :param dish_config_file: dish config file
    :param tmc_central_node: tmc central node
    :param tmc_csp_master: tmc csp master
    """
    caplog.info("Load dish VCC part 1")
    assert tmc_central_node is not None, "TMC central node not loaded"
    assert tmc_csp_master is not None, "TMC CSP master not loaded"
    rc, msg = load_dish_vcc_config(dish_config_file, tmc_central_node, tmc_csp_master)
    assert rc == 0, msg
    caplog.info("Load dish VCC part 2")
    rc, msg = load_dish_vcc_config(dish_config_file, tmc_central_node, tmc_csp_master)
    assert rc == 0, msg


def test_turn_telescope_on(tmc_central_node: DeviceProxy | None) -> None:
    """
    Turn on the telescope.
    
    :param tmc_central_node: tmc central node
    """
    caplog.info("Run the Telescope On command")
    assert tmc_central_node is not None, "TMC central node not loaded"
    tmc_central_node.TelescopeOn()

    retry: int = 10
    while int(tmc_central_node.telescopeState) != 0 and retry > 0:
        retry -= 1
        caplog.info("Waiting for Telescope to come ON (%d retries left)", retry)
        time.sleep(5)
    assert tmc_central_node.telescopeState == 0, "Telescope not on"
    caplog.info("Telecope is ON")
    
    
def test_assign_resources(
    sdp_subarray: DeviceProxy | None,
    assign_resources_file: str,
    receptors: list[str],
    tmc_subarray: DeviceProxy | None,
    cbf_subarray: DeviceProxy | None,
) -> None:
    """
    Assign resources.
    
    :param sdp_subarray: SDP subarray
    :param assign_resources_file: assign resources file
    :param receptors: dish receptors
    :param tmc_subarray: TMC subarray
    :param cbf_subarray: CBF subarray
    """
    caplog.info("Assign resources")
    assert sdp_subarray is not None, "SDP subarray not loaded"
    assert tmc_subarray is not None, "TMS subarray not loaded"
    assert cbf_subarray is not None, "CBF subarray not loaded"
    caplog.info("SDP subarray state: %s", sdp_subarray.state())

    time.sleep(3)

    caplog.info(
        "Running the AssignResources command: subarray obsstate should go to Idle and receptor IDs should be assigned"
    )

    with open(assign_resources_file, encoding="utf-8") as f:
        assign_resources_json = json.load(f)
        assign_resources_json["dish"]["receptor_ids"] = receptors
        assign_resources_json["sdp"]["resources"]["receptors"] = receptors


    caplog.info(f"\nassign_resources_json file contents: \n{assign_resources_json}")

    tmc_subarray.AssignResources(json.dumps(assign_resources_json))

    time.sleep(2)
    caplog.info(f"CBF Subarray Observation State: {tmc_subarray.obsState}")
    caplog.info(f"CBF Subarray Receptors : {cbf_subarray.receptors}")


def test_dish_deployments(dish_deployments: list[str]) -> None:
    """
    Test dish deployments.
    
    :param dish_deployments: list of dish deployments
    """
    caplog.info("Test dish deployments")
    for dish in dish_deployments:
        dish_manager_proxy = DeviceProxy(dish)
        current_pointing = dish_manager_proxy.achievedPointing
        current_az = current_pointing[1]
        current_el = current_pointing[2]

        current_time_tai_s = get_tai_from_unix_s(time.time() + 120)

        # Directions to move values
        az_dir = 1 if current_az < 350 else -1
        el_dir = 1 if current_el < 80 else -1

        track_table = [
            current_time_tai_s + 3,
            current_az + 1 * az_dir,
            current_el + 1 * el_dir,
            current_time_tai_s + 5,
            current_az + 2 * az_dir,
            current_el + 2 * el_dir,
            current_time_tai_s + 7,
            current_az + 3 * az_dir,
            current_el + 3 * el_dir,
            current_time_tai_s + 9,
            current_az + 4 * az_dir,
            current_el + 4 * el_dir,
            current_time_tai_s + 11,
            current_az + 5 * az_dir,
            current_el + 5 * el_dir,
        ]

        dish_manager_proxy.programTrackTable = track_table
        
        
def test_configure_scan_hack(
    sdp_subarray_leaf_node: DeviceProxy | None, csp_subarray_leaf_node: DeviceProxy | None
) -> None:
    """
    TMC leaf node hack to get around TMC subarray stuck in configuring.
    
    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
    caplog.info("configure scan")
    assert sdp_subarray_leaf_node is not None, "SDP subarray leaf node not loaded"
    assert csp_subarray_leaf_node is not None, "CSP subarray leaf node not loaded"
    
    with open("../../data/mid_telescope/tmc/scan.json", "r", encoding="utf-8") as json_data:
        d = json.load(json_data)
        sdp_scan = d["sdp"]
        caplog.info("SDP scan: %s", sdp_scan)
        sdp_subarray_leaf_node.scan(json.dumps(sdp_scan))

    time.sleep(10)
    caplog.info("sdp Subarray Obs State: %s", sdp_subarray_leaf_node.sdpSubarrayObsState)

    with open("../../data/mid_telescope/tmc/scan.json", "r", encoding="utf-8") as json_data:
        d = json.load(json_data)
        csp_scan = d["csp"]
        caplog.info(csp_scan)
        csp_subarray_leaf_node.scan(json.dumps(csp_scan))

    time.sleep(2)
    caplog.info("csp Subarray Obs State: %s", csp_subarray_leaf_node.cspSubarrayObsState)


def test_end_scan_hack(
    sdp_subarray_leaf_node: DeviceProxy | None, csp_subarray_leaf_node: DeviceProxy | None
) -> None:
    """
    TMC leaf node hack to get around TMC subarray stuck in configuring.
    
    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
    caplog.info("Running the End Scan command: subarray obsstate should go to Ready state")
    assert sdp_subarray_leaf_node is not None, "SDP subarray leaf node not loaded"
    assert csp_subarray_leaf_node is not None, "CSP subarray leaf node not loaded"
    
    sdp_subarray_leaf_node.EndScan()
    time.sleep(2)
    csp_subarray_leaf_node.EndScan()
    caplog.info(f"SDP Subarray Observation State: {sdp_subarray_leaf_node.sdpSubarrayObsState}")
    caplog.info(f"CSP Subarray Observation State: {csp_subarray_leaf_node.cspSubarrayObsState}")


def test_release_resources_hack(
    sdp_subarray_leaf_node: DeviceProxy | None, csp_subarray_leaf_node: DeviceProxy | None
) -> None:
    """
    TMC leaf node hack to get around TMC subarray stuck in configuring.
    
    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
    caplog.info(
        "Running the Release All Resources command: subarray obsstate should go to Empty state and receptor IDs should be empty"
    )
    assert sdp_subarray_leaf_node is not None, "SDP subarray leaf node not loaded"
    assert csp_subarray_leaf_node is not None, "CSP subarray leaf node not loaded"

    sdp_subarray_leaf_node.ReleaseAllResources()
    time.sleep(2)
    csp_subarray_leaf_node.ReleaseAllResources()

    time.sleep(2)
    caplog.info(f"SDP Subarray Observation State: {sdp_subarray_leaf_node.sdpSubarrayObsState}")
    caplog.info(f"CSP Subarray Observation State: {csp_subarray_leaf_node.cspSubarrayObsState}")
    

def test_turn_telescope_off(
    tmc_central_node: DeviceProxy | None, 
    csp_control: DeviceProxy | None, 
    cbf_controller: DeviceProxy | None,
) -> None:
    """
    Turn off the telescope.
    
    :param tmc_central_node: tmc central node
    :param csp_control: csp control
    :param cbf_controller: cbf controller
    """
    caplog.info("Run the Telescope Off command")

    assert tmc_central_node is not None, "TMC central node not loaded"
    assert csp_control is not None, "CSP control not loaded"
    assert cbf_controller is not None, "CBF controller not loaded"

    tmc_central_node.TelescopeOff()

    time.sleep(5)
    caplog.info(f"TMC Central Node State: {tmc_central_node.State()}")
    caplog.info(f"CSP Control State: {csp_control.State()}")
    caplog.info(f"CBF Controller State: {cbf_controller.State()}")
    
    assert tmc_central_node.telescopeState != 0, "Telescope not off"

