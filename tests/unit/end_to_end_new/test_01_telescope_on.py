"""End-to-end testing in the MID ITF."""

import json
import logging
import socket
import ssl
import time
import urllib.error
import urllib.request
from typing import Tuple

import tango
from tango import DevFailed, DeviceProxy

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)

# pylint: disable=duplicate-code

# Use unverified SSL
# pylint: disable-next=protected-access
ssl._create_default_https_context = ssl._create_unverified_context


def check_web_link(web_uri: str) -> Tuple[int, str]:
    """
    Check that URI is reachable.

    :param web_uri: URI to be checked
    :return: status code and error message
    """
    caplog.info("Check URL %s", web_uri)
    try:
        with urllib.request.urlopen(web_uri):
            caplog.debug("Checked URL %s", web_uri)
    except urllib.error.HTTPError as httpe:
        caplog.error("HTTP error: %s", httpe)
        return 1, str(httpe)
    except urllib.error.URLError as urle:
        caplog.error("Page %s not found: %s", web_uri, urle)
        return 1, str(urle)
    except socket.gaierror as serr:
        caplog.error("Socket error: %s", serr)
        return 1, str(serr)
    return 0, "OK"


# pylint: disable-next=c-extension-no-member
def get_tango_dev_state(dev_state: tango._tango.DevState) -> str:
    """
    Get state of Tango device.

    :param dev_state: numeric value
    :return: string with state
    """
    dst = int(dev_state)
    # pylint: disable-next=c-extension-no-member,protected-access
    return tango._tango.DevState.values[dst]


def test_csp_control_admin_mode(csp_control: DeviceProxy | None) -> None:
    """
    Set device admin mode to ONLINE.

    :param csp_control: CSP control
    """
    caplog.info("Set CSP control to online")
    assert csp_control is not None, "CSP control not loaded"
    csp_control.adminMode = 0
    time.sleep(2)
    assert csp_control.adminMode == 0, "Could not set CSP control to online"


def test_csp_subarray_admin_mode(csp_subarray: DeviceProxy | None) -> None:
    """
    Set device admin mode to ONLINE.

    :param csp_subarray: CSP subarray
    """
    caplog.info("Set CSP subarray to online")
    assert csp_subarray is not None, "CSP subarray not loaded"
    assert csp_subarray.info().dev_type == "MidCspSubarray"
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


# pylint: disable-next=too-many-arguments
def test_states_on(
    tmc_central_node: DeviceProxy | None,
    csp_control: DeviceProxy | None,
    cbf_controller: DeviceProxy | None,
    sdp_subarray: DeviceProxy | None,
    tmc_subarray: DeviceProxy | None,
    cbf_subarray: DeviceProxy | None,
    sdp_subarray_leaf_node: DeviceProxy | None,
    csp_subarray_leaf_node: DeviceProxy | None,
) -> None:
    """
    Read states of Tango devices.

    :param tmc_central_node: TMC central node
    :param csp_control: CSP control
    :param cbf_controller: CBF controller
    :param sdp_subarray: SDP subarray
    :param tmc_subarray: TMC subarray
    :param cbf_subarray: CBF subarray
    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    :return:
    """
    # TMC central node
    assert tmc_central_node is not None, "TMC central node not loaded"
    caplog.info(
        "TMC central node (%s) state: %s", tmc_central_node.name(), tmc_central_node.State()
    )
    # CSP control
    assert csp_control is not None, "CSP control not loaded"
    caplog.info("CSP control (%s) state: %s", csp_control.name(), csp_control.State())
    # CBF controller
    assert cbf_controller is not None, "CBF controller not loaded"
    caplog.info("CBF controller (%s) state: %s", cbf_controller.name(), cbf_controller.State())
    # SDP subarray
    assert sdp_subarray is not None, "SDP subarray not loaded"
    caplog.info("SDP subarray (%s) state: %s", sdp_subarray.name(), sdp_subarray.State())
    # TMC subarray
    assert tmc_subarray is not None, "TMC subarray not loaded"
    assert tmc_subarray.info().dev_type == "SubarrayNodeMid"
    caplog.info("TMC subarray (%s) state: %s", tmc_subarray.name(), tmc_subarray.State())
    # CBF subarray
    assert cbf_subarray is not None, "CBF subarray not loaded"
    assert cbf_subarray.info().dev_type == "CbfSubarray"
    caplog.info("CBF subarray (%s) state: %s", cbf_subarray.name(), cbf_subarray.State())
    # SDP subarray leaf node
    assert sdp_subarray_leaf_node is not None, "SDP subarray leaf node not loaded"
    caplog.info(
        "SDP subarray leaf node (%s) state: %s",
        sdp_subarray_leaf_node.name(),
        sdp_subarray_leaf_node.State(),
    )
    # CSP subarray leaf node
    assert csp_subarray_leaf_node is not None, "CSP subarray leaf node not loaded"
    caplog.info(
        "CSP subarray leaf node (%s) state: %s",
        csp_subarray_leaf_node.name(),
        csp_subarray_leaf_node.State(),
    )


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
    assert tmc_central_node is not None, "TMC central node not loaded"
    assert tmc_csp_master is not None, "TMC CSP master not loaded"
    assert tmc_csp_master.info().dev_type == "CspMasterLeafNodeMid"
    with open(dish_config_file, encoding="utf-8") as cfg_f:
        dish_config_json = json.load(cfg_f)
    dish_config_json["tm_data_sources"][
        0
    ] = "car://gitlab.com/ska-telescope/ska-telmodel-data?0.1.0-rc-mid-itf#tmdata"

    dish_config_json["tm_data_filepath"] = (
        "instrument/ska1_mid_itf/ska-mid-cbf-system-parameters.json"
    )

    caplog.debug("Dish config JSON file contents:\n%s", dish_config_json)
    try:
        tmc_central_node.LoadDishCfg(json.dumps(dish_config_json))
    except DevFailed as t_err:
        err_msg: str = t_err.args[0].desc.strip()
        caplog.error("Could not load VCC configuration file: %s", err_msg)
        return 1, err_msg

    time.sleep(2)
    caplog.info(
        "TMC CSP Master's Dish Vcc Config attribute value:\n%s", tmc_csp_master.dishVccConfig
    )
    caplog.info(
        "TMC CSP Master's Source Dish Vcc Config attribute value:\n%s",
        tmc_csp_master.sourceDishVccConfig,
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
    tmc_central_node_t: str = tmc_central_node.info().dev_type
    caplog.info("Type of tmc_central_node is %s", tmc_central_node_t)
    assert tmc_central_node_t == "CentralNodeMid", f"TMC central node ype is {tmc_central_node_t}"
    tmc_csp_master_t: str = tmc_csp_master.info().dev_type
    caplog.info("Type of tmc_csp_master is %s", tmc_csp_master_t)
    assert tmc_csp_master_t == "CspMasterLeafNodeMid", f"TMC CSP master type is {tmc_csp_master_t}"
    rval, msg = load_dish_vcc_config(dish_config_file, tmc_central_node, tmc_csp_master)
    assert rval == 0, msg
    caplog.info("Load dish VCC part 2")
    rval, msg = load_dish_vcc_config(dish_config_file, tmc_central_node, tmc_csp_master)
    assert rval == 0, msg


def test_turn_telescope_on(tmc_central_node: DeviceProxy | None) -> None:
    """
    Turn on the telescope.

    :param tmc_central_node: tmc central node
    """
    caplog.info("Run the Telescope On command")
    assert tmc_central_node is not None, "TMC central node not loaded"
    try:
        tel_state: str = get_tango_dev_state(tmc_central_node.telescopeState)
    except tango.DevFailedDevFailed as t_err:
        err_msg: str = t_err.args[0].desc.strip()
        caplog.error("Could not get telescope state: %s", err_msg)
        assert 0, err_msg
    caplog.info("Telescope state is '%s'", tel_state)
    if tel_state == "ON":
        caplog.warning("Telescope is already on")
        return
    # assert tmc_central_node.telescopeState == tango._tango.DevState(1)
    try:
        tmc_central_node.TelescopeOn()
    except DevFailed as t_err:
        err_msg: str = t_err.args[0].desc.strip()
        caplog.error("Could not turn on telescope: %s", err_msg)
        assert 0, err_msg

    retry: int = 10
    while int(tmc_central_node.telescopeState) != 0 and retry > 0:
        retry -= 1
        caplog.info("Waiting for Telescope to come ON (%d retries left)", retry)
        time.sleep(5)
    caplog.info("Telescope state is now %s", get_tango_dev_state(tmc_central_node.telescopeState))
    assert tmc_central_node.telescopeState == 0, "Telescope not on"
