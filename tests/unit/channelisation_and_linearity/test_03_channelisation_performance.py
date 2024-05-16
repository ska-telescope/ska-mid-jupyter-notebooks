"""Channelisation Performance Verification Tests."""

# pylint: disable=broad-except,protected-access

import logging
import time

import tango
from ska_oso_pdm.entities.common.sb_definition import SBDefinition
from ska_oso_pdm.entities.sdp import BeamMapping
from ska_oso_scripting import oda_helper
from ska_oso_scripting.functions.devicecontrol.exception import EventTimeoutError
from ska_oso_scripting.objects import SubArray
from ska_tmc_cdm.messages.central_node.sdp import Channel

from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot


LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)


# 3.7.1 Define Resources to be used during Observation
# ----------------------------------------------------
def test_observation_resources(observation: ObservationSB) -> None:
    """
    Generate Processing Block and Execution Block IDs using SKUID.

    :param observation: the SB of the observation
    :return:
    """
    # External IDs (this would typically come from a database like ODA)
    # this is simulated by means of instantiate a new Observation object comping
    # from the helper modules
    assert observation is not None, "Unknown observation"
    caplog.info("Observation is OK")


# 3.7.2 Create the high level observation specifications in terms of target specs
# -------------------------------------------------------------------------------
def test_create_observation_specification(
    observation: ObservationSB,
    default_target_specs: dict,
) -> None:
    """
    Create the high level observation specifications in terms of target specs.

    :param observation: the SB of the observation
    :param dish_deployments: list of handles for deployed dishes
    :return:
    """
    # Note :- Users may currently modify the values by replacing the example values as
    # given for each field within Target specification section.
    channel_configuration = [
        Channel(
            spectral_window_id="fsp_1_channels",
            count=14880,
            start=0,
            stride=2,
            freq_min=0.35e9,
            freq_max=0.368e9,
            link_map=[[0, 0], [200, 1], [744, 2], [944, 3]],
        )
    ]

    for key, value in default_target_specs.items():
        caplog.info(f"Add configuration for {key}")
        try:
            observation.add_channel_configuration(value.channelisation, channel_configuration)
        except AssertionError as aerr:
            caplog.info(f"ERROR: {aerr}")

    observation.add_target_specs(default_target_specs)

    for target_id, _target in default_target_specs.items():
        caplog.info(f"Add scan configuration {target_id}")
        try:
            observation.add_scan_type_configuration(
                config_name=target_id,
                beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
                derive_from=".default",
            )
        except AssertionError as aerr:
            caplog.info(f"ERROR: {aerr}")
    scan_def_id = "flux calibrator"
    observation.add_scan_sequence([scan_def_id])


# 3.7.3 Mid-configuration schema input used by observing commands
# ---------------------------------------------------------------
def test_mid_configuration_schema(telescope_monitor_plot: TelescopeMononitorPlot) -> None:
    """
    Use this configuration schema as input for observing commands.

    :param telescope_monitor_plot: the monitor thing
    """
    for box_name in telescope_monitor_plot._labeled_blocks:
        try:
            value = telescope_monitor_plot._labeled_block[box_name]
            caplog.info("Monitor %s: %s", box_name, value)
        except AttributeError:
            caplog.warning("Could not read %s", box_name)


# 3.7.4 Create Scheduling Block Definition (SBD) Instance and save it into the ODA
# --------------------------------------------------------------------------------
def test_scheduling_block_definition(
    observation: ObservationSB,
    eb_id: str | None,
    pdm_allocation: SBDefinition | None,
) -> None:
    """
    Create scheduling block definition (SBD) instance and save it into the ODA.

    :param observation: the SB of the observation
    :param eb_id: the ID of the EB
    :param default_target_specs: default target specification
    :param pdm_allocation: allocation for PDM
    """
    assert pdm_allocation is not None, "Unknown PDM allocation"
    observation.eb_id = eb_id
    sbd = oda_helper.save(pdm_allocation)
    sbd_id = sbd.sbd_id
    pdm_allocation.sbd_id = sbd_id
    caplog.info(f"Saved Scheduling Block Definition Instance in ODA: SBD_ID={sbd_id}")


# 3.8 Assign Resources
# ====================
def test_assign_subarray_resources(
    observation: ObservationSB,
    pdm_allocation: SBDefinition | None,
    sub: SubArray | None,
    telescope_monitor_plot: TelescopeMononitorPlot,
) -> None:
    """
    Assign the requested resources to a subarray.

    :param observation: the SB of the observation
    :param pdm_allocation: allocation for PDM
    :param sub: subarray handle
    :param telescope_monitor_plot: the monitor thing
    """
    assert pdm_allocation is not None, "Unknown PDM allocation"
    caplog.info("Assign request")
    assign_request = observation.generate_allocate_config_sb(pdm_allocation).as_object
    caplog.info(f"Got assign request {assign_request}")

    # if debug_mode:
    #     print("Debug request JSON")
    #     request_json = get_request_json(assign_request, AssignResourcesRequest, True)
    #     print("AssignResourcesRequest:", json.dumps(json.loads(request_json), indent=2))
    assert sub is not None, "Unknown subarray"
    caplog.info("Assign from Control Data Model (CDM) from subarray {sub.id}")
    try:
        sub.assign_from_cdm(assign_request, timeout=120)
    except tango.DevFailed as terr:
        caplog.error(f"ERROR: {terr.args[0].desc.strip()}")
    except EventTimeoutError:
        caplog.error("Could not assign resources")
    except Exception as oerr:
        caplog.error("Running on empty: %s", oerr)

    for box_name in telescope_monitor_plot._labeled_blocks:
        try:
            value = telescope_monitor_plot._labeled_block[box_name]
            caplog.info("Monitor %s: %s", box_name, value)
        except AttributeError:
            caplog.warning("Could not read %s", box_name)


# 3.9 Configure Scan
# ==================
def test_configure_scan(
    observation: ObservationSB,
    pdm_allocation: SBDefinition | None,
    sub: SubArray | None,
) -> None:
    """
    Configure the telescope on first target in sequence.

    This may be modified to configure and run multiple targets at a later time.

    :param observation: the SB of the observation
    :param pdm_allocation:  allocation for PDM
    :param sub: subarray handle
    """
    assert pdm_allocation is not None, "Unknown PDM allocation"
    assert sub is not None, "Unknown subarray"

    scan_def_id = "flux calibrator"

    configure_object = observation.generate_scan_config_sb(
        pdm_observation_request=pdm_allocation,
        scan_definition_id=scan_def_id,
        scan_duration=10.0,
    ).as_object

    # if debug_mode:
    #     cfg_json = get_request_json(configure_object, ConfigureRequest)
    #     print(f"ConfigureRequest={cfg_json}")

    try:
        sub.configure_from_cdm(configure_object, timeout=120)
        time.sleep(2)
        caplog.info("Subarray configured OK")
    except tango.DevFailed as terr:
        caplog.info(f"ERROR: {terr.args[0].desc.strip()}")


# 3.10 Run the Scan
# =================
def test_run_scan(
    sub: SubArray | None,
    telescope_monitor_plot: TelescopeMononitorPlot,
) -> None:
    """
    Run the scan.

    :param sub: subarray handle
    :param telescope_monitor_plot: the monitor thing
    """
    try:
        sub.scan(timeout=120)
    except tango.DevFailed as terr:
        caplog.error(f"ERROR: {terr.args[0].desc.strip()}")
    for box_name in telescope_monitor_plot._labeled_blocks:
        try:
            value = telescope_monitor_plot._labeled_block[box_name]
            caplog.info("Monitor %s: %s", box_name, value)
        except AttributeError:
            caplog.warning("Could not read %s", box_name)
