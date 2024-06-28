"""End-to-end testing in the MID ITF."""

import json
import logging
import time
from astropy.time import Time  # type: ignore[import-untyped]
from tango import CommunicationFailed, DevFailed, DeviceProxy

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)


def get_tai_from_unix_s(unix_s: float) -> float:
    """
    Calculate atomic time in seconds from unix time in seconds.

    :param unix_s: Unix time in seconds
    :return: atomic time (tai) in seconds
    """
    astropy_time_utc = Time(unix_s, format="unix")
    return astropy_time_utc.unix_tai


def test_states_configure(
    sdp_subarray: DeviceProxy | None,
    tmc_subarray: DeviceProxy | None,
    cbf_subarray: DeviceProxy | None,
    sdp_subarray_leaf_node: DeviceProxy | None,
    csp_subarray_leaf_node: DeviceProxy | None,
) -> None:
    """
    Read states of Tango devices.

    :param sdp_subarray: SDP subarray
    :param tmc_subarray: TMC subarray
    :param cbf_subarray: CBF subarray
    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
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
    # TODO SDP subarray does not exist!
    # assert sdp_subarray is not None, "SDP subarray not loaded"
    assert tmc_subarray is not None, "TMC subarray not loaded"
    assert tmc_subarray.info().dev_type == "SubarrayNodeMid"
    assert cbf_subarray is not None, "CBF subarray not loaded"
    assert cbf_subarray.info().dev_type == "CbfSubarray"
    if sdp_subarray is not None:
        caplog.info("SDP subarray state: %s", sdp_subarray.state())
    else:
        caplog.warning("SDP subarray not loaded")

    time.sleep(3)
    caplog.info("Subarray should go to idle and receptor IDs should be assigned")

    with open(assign_resources_file, encoding="utf-8") as f:
        assign_resources_json = json.load(f)
        assign_resources_json["dish"]["receptor_ids"] = receptors
        assign_resources_json["sdp"]["resources"]["receptors"] = receptors

    caplog.info(
        "Assign resources JSON file contents:\n%s", json.dumps(assign_resources_json, indent=4)
    )

    tmc_sub_state = str(tmc_subarray.obsState)
    caplog.info(f"TMC subarray observation state: {tmc_sub_state}")
    err_msg: str = ""
    try:
        tmc_subarray.AssignResources(json.dumps(assign_resources_json))
    except DevFailed as t_err:
        err_msg = t_err.args[0].desc.strip()
        caplog.error("Assign resources failed: %s", err_msg)

    time.sleep(2)
    caplog.info(f"TMC subarray observation state: {tmc_subarray.obsState}")
    caplog.info(f"CBF subarray receptors: {cbf_subarray.receptors}")
    assert not err_msg, err_msg


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
    tmc_scan_config_file: str,
    sdp_subarray_leaf_node: DeviceProxy | None,
    csp_subarray_leaf_node: DeviceProxy | None,
) -> None:
    """
    TMC leaf node hack to get around TMC subarray stuck in configuring.

    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
    caplog.info("Configure scan from file %s", tmc_scan_config_file)
    assert sdp_subarray_leaf_node is not None, "SDP subarray leaf node not loaded"
    assert csp_subarray_leaf_node is not None, "CSP subarray leaf node not loaded"

    scan_cfg: Any
    with open(tmc_scan_config_file, "r", encoding="utf-8") as json_data:
        scan_cfg = json.load(json_data)

    caplog.info("TMC scan config:\n%s", json.dumps(scan_cfg, indent=4))

    assert "sdp" in scan_cfg, "SDP data not found"
    sdp_scan = scan_cfg["sdp"]

    caplog.info("SDP scan: %s", sdp_scan)
    sdp_subarray_leaf_node.scan(json.dumps(sdp_scan))

    time.sleep(10)
    caplog.info("sdp Subarray Obs State: %s", sdp_subarray_leaf_node.sdpSubarrayObsState)

    assert "csp" in scan_cfg, "CSP data not found"
    csp_scan = scan_cfg["csp"]
    caplog.info(csp_scan)
    csp_subarray_leaf_node.scan(json.dumps(csp_scan))

    time.sleep(2)
    caplog.info("CSP Subarray Observation State: %s", csp_subarray_leaf_node.cspSubarrayObsState)
    caplog.info("SDP Subarray Observation State: %s", sdp_subarray_leaf_node.cspSubarrayObsState)


def test_configure_obs_state(
    tmc_subarray: DeviceProxy | None,
    csp_subarray_leaf_node: DeviceProxy | None,
    sdp_subarray_leaf_node: DeviceProxy | None
) -> None:
    """
    Read observation states of Tango devices.

    :param tmc_subarray: TMC subarray
    :param csp_subarray_leaf_node: CSP Subarray leaf node
    :param sdp_subarray_leaf_node: SDP Subarray leaf node
    """
    err_count: int = 0
    # TMC subarray
    try:
        caplog.info(f"TMC subarray observation state: %s", str(tmc_subarray.obsState))
    except AttributeError as a_err:
        err_count += 1
        caplog.error("Could not read observation state of TMC Subarray (%s)", tmc_subarray.name())
    # CSP Subarray leaf node
    try:
        caplog.info(
            "CSP Subarray Observation State: %s", str(csp_subarray_leaf_node.cspSubarrayObsState)
        )
    except AttributeError as a_err:
        err_count += 1
        caplog.error(
            "Could not read observation state of SDP Subarray (%s)", csp_subarray_leaf_node.name()
        )
    # SDP Subarray leaf node
    try:
        caplog.info(
            "SDP Subarray Observation State: %s", str(sdp_subarray_leaf_node.cspSubarrayObsState)
        )
    except AttributeError as a_err:
        err_count += 1
        caplog.error(
            "Could not read observation state of SDP Subarray (%s)", sdp_subarray_leaf_node.name()
        )
    assert err_count == 0, f"Could not read {err_count} observation state(s)"
