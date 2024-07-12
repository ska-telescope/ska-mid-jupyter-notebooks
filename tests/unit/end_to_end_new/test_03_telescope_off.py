"""End-to-end testing in the MID ITF."""

import logging
import time

from tango import CommunicationFailed, DevFailed, DeviceProxy

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)


def test_states_off(
    tmc_central_node: DeviceProxy | None,
    csp_control: DeviceProxy | None,
    cbf_controller: DeviceProxy | None,
    sdp_subarray_leaf_node: DeviceProxy | None,
    csp_subarray_leaf_node: DeviceProxy | None,
) -> None:
    """
    Read states of Tango devices.

    :param tmc_central_node: TMC central node
    :param csp_control: CSP control
    :param cbf_controller: CBF controller
    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
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


def test_end_scan_hack(
    sdp_subarray_leaf_node: DeviceProxy | None, csp_subarray_leaf_node: DeviceProxy | None
) -> None:
    """
    TMC leaf node hack to get around TMC subarray stuck in configuring.

    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
    caplog.info("Run end scan command: subarray obsstate should go to Ready state")
    assert sdp_subarray_leaf_node is not None, "SDP subarray leaf node not loaded"
    assert csp_subarray_leaf_node is not None, "CSP subarray leaf node not loaded"
    caplog.info("CSP Subarray Observation State: %s", csp_subarray_leaf_node.cspSubarrayObsState)

    err_msg: str
    try:
        caplog.info(
            "SDP Subarray Observation State: %s", sdp_subarray_leaf_node.cspSubarrayObsState
        )
    except AttributeError as a_err:
        caplog.warning("Could not read SDP Subarray Observation State: %s", str(a_err))

    try:
        sdp_subarray_leaf_node.EndScan()
    except DevFailed as t_err:
        err_msg = t_err.args[0].desc.strip()
        caplog.error("Could not end scan: %s", err_msg)
        assert 0, err_msg

    try:
        caplog.info(
            "CSP subarray observation state: %s", csp_subarray_leaf_node.cspSubarrayObsState
        )
    except AttributeError as t_err:
        err_msg = str(t_err)
        caplog.error("Could not read CSP observation state: %s", err_msg)
        assert 0, err_msg
    try:
        caplog.info(
            "SDP subarray observation state: %s", sdp_subarray_leaf_node.cspSubarrayObsState
        )
    except AttributeError as t_err:
        err_msg = str(t_err)
        caplog.error("Could not read SDP observation state: %s", err_msg)
        assert 0, err_msg

    time.sleep(2)
    try:
        caplog.info("Rerun end scan command")
        csp_subarray_leaf_node.EndScan()
    except DevFailed:
        caplog.warning("Could not end scan again")

    caplog.info("CSP Subarray Observation State: %s", csp_subarray_leaf_node.cspSubarrayObsState)
    caplog.info("SDP Subarray Observation State: %s", sdp_subarray_leaf_node.cspSubarrayObsState)


def test_release_resources_hack(
    sdp_subarray_leaf_node: DeviceProxy | None, csp_subarray_leaf_node: DeviceProxy | None
) -> None:
    """
    TMC leaf node hack to get around TMC subarray stuck in configuring.

    :param sdp_subarray_leaf_node: SDP subarray leaf node
    :param csp_subarray_leaf_node: CSP subarray leaf node
    """
    caplog.info(
        "Run Release All Resources: subarray obsstate should go to Empty state and receptor IDs"
        " should be empty"
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
    assert csp_control.info().dev_type == "MidCspController"
    assert cbf_controller is not None, "CBF controller not loaded"
    assert cbf_controller.info().dev_type == "CbfController"

    try:
        caplog.info(
            "Telescope (%s) state is %s",
            tmc_central_node.name(),
            str(tmc_central_node.telescopeState),
        )
        tmc_central_node.TelescopeOff()
    except CommunicationFailed as t_err:
        err_msg: str = t_err.args[0].desc.strip()
        caplog.error("Could not turn telescope off: %s", err_msg)
        assert 0, err_msg

    time.sleep(5)
    caplog.info(f"TMC Central Node State: {tmc_central_node.State()}")
    caplog.info(f"CSP Control State: {csp_control.State()}")
    caplog.info(f"CBF Controller State: {cbf_controller.State()}")

    caplog.info("Telescope state is now %s", str(tmc_central_node.telescopeState))
    assert tmc_central_node.telescopeState != 0, "Telescope not off"
