"""Do the tests."""
import logging
import pytest
from typing import List

import sys

import json
import os
import pathlib
import time
import tango

import ska_ser_logging
from bokeh.io import output_notebook
from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_pdm.entities.sdp import BeamMapping
from ska_oso_scripting import oda_helper
from ska_oso_scripting.functions.devicecontrol.resource_control import get_request_json
from ska_oso_scripting.objects import SubArray, Telescope
from ska_tmc_cdm.messages.central_node.assign_resources import AssignResourcesRequest
from ska_tmc_cdm.messages.central_node.sdp import Channel
from ska_tmc_cdm.messages.subarray_node.configure import ConfigureRequest
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand

from ska_mid_jupyter_notebooks.cluster.cluster import Environment, TangoDeployment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.helpers.path import project_root
from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot
from ska_mid_jupyter_notebooks.sut.state import TelescopeDeviceModel, get_telescope_state
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment, disable_qa
from ska_mid_jupyter_notebooks.test_equipment.rendering import TestEquipmentMonitorPlot
from ska_mid_jupyter_notebooks.test_equipment.state import TestEquipmentModel
from ska_mid_jupyter_notebooks.test_equipment.test_equipment import TangoTestEquipment


LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)


# 1.2 Set up Global Variables and Configuration
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
    assert (len(dish_deployments) == 2)


# 1.3 Test Connections to Namespaces
def test_connections_to_namespaces(
    sut: TangoSUTDeployment,
    test_equipment: TangoTestEquipment,
    dish_deployments: List[TangoDishDeployment],
) -> None:
    """
    Test connections to K8S namespaces.

    :param sut: system under test
    :param test_equipment: Tango devices for test equipment
    :param dish_deployments: list of handles for deployed dishes
    """
    try:
        st = sut.smoke_test()
        caplog.info("SUT smoke test: %s", str(st))
    except Exception as smerr:
        caplog.error("SUT error: %s", str(smerr))
        assert True
    caplog.info("System under test OK")
    try:
        test_equipment.smoke_test()
    except Exception as smerr:
        caplog.error("Test equipment error: %s", str(smerr))
        assert True
    caplog.info("Test equipment OK")
    for dish_deployment in dish_deployments:
        try:
            dish_deployment.smoke_test()
        except Exception as smerr:
            caplog.error("Dish error: %s", str(smerr))
            assert True
    caplog.info("Dishes OK")


# 1.4 Export System Configuration
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
    for deployment in [sut, test_equipment, *dish_deployments]:
        deployment.export_chart_configuration(output_dir=notebook_output_dir)
    caplog.info("System configuration OK")


# 2.1 Configure Test Equipment State
def test_test_equipment_state(
    test_equipment: TangoTestEquipment,
    test_equipment_state: TestEquipmentModel,
) -> None:
    """
    Configure test equipment state.

    :param test_equipment: Tango devices for test equipment
    :param test_equipment_state: state of the above
    """
    caplog.info("Test equipment devices: %s", test_equipment.devices)
    assert(len(test_equipment.devices) > 0)


# 2.2 Print Test Equipment Diagnostics
def test_signal_generator(test_equipment: TangoTestEquipment) -> None:
    """
    Print test equipment diagnostics.

    :param test_equipment: Tango devices for test equipment
    """
    siggen = test_equipment.signal_generator

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

    assert (str(siggen.State()) == "ON")

# ### 2.3 Create Test Equipment Plot
def test_subscribe_to_test_equipment_state(
    test_equipment_state: TestEquipmentModel,
    monitor_plot: TestEquipmentMonitorPlot,
) -> None:
    """
    Create test equipment plot.

    :param test_equipment: Tango devices for test equipment
    :param monitor_plot: graphic for looging pretty
    """
    test_equipment_state.subscribe_to_test_equipment_state(monitor_plot.handle_device_state_change)
    test_equipment_state.activate()
