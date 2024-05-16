"""Shut down telescope."""

# pylint: disable=broad-except,protected-access

import logging
import os
import pathlib
import time
from typing import List, Literal

import tango
from ska_control_model import AdminMode
from ska_oso_pdm.entities.common.sb_definition import SBDefinition
from ska_oso_pdm.entities.sdp import BeamMapping
from ska_oso_scripting import oda_helper
from ska_oso_scripting.functions.devicecontrol.exception import EventTimeoutError
from ska_oso_scripting.objects import SubArray, Telescope
from ska_tmc_cdm.messages.central_node.sdp import Channel

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
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


# 3.12 Reset the Telescope/Subarray (On Failure)
def test_reset(
    sub: SubArray | None,
    dish_deployments: List[TangoDishDeployment],
) -> None:
    """
    Reset the telescope and subarray on failure.

    :param sub: subarray handle
    :param dish_deployments: list of handles for deployed dishes
    """
    # Set booleans to True to reset the system after a failed execution.
    do_reset_subarray = False
    do_reset_dish = False

    if do_reset_subarray:
        sub.abort()
        time.sleep(3)
        sub.restart()

    if do_reset_dish:
        dish_deployment: TangoDishDeployment
        for dish_deployment in dish_deployments:
            dish_deployment.reset_dish()

# 3.11 Post Observation teardown
# If the observation executed successfully, you can use the following commands to reset
# the telescope.


# 3.11.1 Clear scan configuration
def test_clear_scan_configuration(
    sub: SubArray | None,
    telescope_monitor_plot: TelescopeMononitorPlot,
) -> None:
    """
    Clear scan configuration .

    :param sub: subarray handle
    :param telescope_monitor_plot: the monitor thing
    """
    try:
        sub.end()
        telescope_monitor_plot.show()
    except tango.DevFailed as terr:
        caplog.error(f"ERROR: {terr.args[0].desc.strip()}")
    # for box_name in telescope_monitor_plot._labeled_blocks:
    #     try:
    #         value = telescope_monitor_plot._labeled_block[box_name]
    #         caplog.info("Monitor %s: %s", box_name, value)
    #     except AttributeError:
    #         caplog.warning("No value for %s", box_name)


# 3.11.2 Release Subarray resources
def test_release_subarray_resources(
    sub: SubArray | None,
    telescope_monitor_plot: TelescopeMononitorPlot,
) -> None:
    """
    Release the subarray resources.

    :param sub: subarray handle
    :param telescope_monitor_plot: the monitor thing
    :return:
    """
    try:
        sub.release()
        caplog.info("Subarray released")
    except tango.DevFailed as terr:
        caplog.error(f"ERROR: {terr.args[0].desc.strip()}")
        assert False, terr.args[0].desc.strip()
    except AttributeError as aerr:
        caplog.error("ERROR: %s", str(aerr))
        assert False, str(aerr)
    for box_name in telescope_monitor_plot._labeled_blocks:
        try:
            value = telescope_monitor_plot._labeled_block[box_name]
            caplog.info("Monitor %s: %s", box_name, value)
        except AttributeError:
            caplog.warning("Could not read %s", box_name)