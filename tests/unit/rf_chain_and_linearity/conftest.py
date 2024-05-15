"""This module contains test harness elements common to all unit tests."""

import logging
import pathlib
import pytest
import time
from typing import List

from ska_mid_jupyter_notebooks.cluster.cluster import Environment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.helpers.path import project_root
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment
from ska_mid_jupyter_notebooks.test_equipment.rendering import (
    get_test_equipment_monitor_plot,
    TestEquipmentMonitorPlot,
)
from ska_mid_jupyter_notebooks.test_equipment.state import get_equipment_model, TestEquipmentModel
from ska_mid_jupyter_notebooks.test_equipment.test_equipment import TangoTestEquipment

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)

dishlmc_enabled = True
dish_ids = ["0001", "0036"]
branch_name = "at-1958-rf-chain-linearity-performance"
sut_namespace_override = ""
dish_namespace_overrides = ["", ""]
subarray_id = 1

executon_environment = Environment.CI
teq = TangoTestEquipment()


@pytest.fixture()
def sut() -> TangoSUTDeployment:
    system_under_test = TangoSUTDeployment(
        branch_name,
        executon_environment,
        namespace_override=sut_namespace_override,
        subarray_index=subarray_id,
    )
    caplog.info("SUT configured: %s", str(system_under_test))
    return system_under_test


@pytest.fixture()
def dish_deployments() -> List[TangoDishDeployment]:
    dishes = []
    if dishlmc_enabled:
        for i, d in enumerate(dish_ids):
            dish = TangoDishDeployment(
                f"ska{d[1:]}",
                branch_name=branch_name,
                environment=executon_environment,
                namespace_override=dish_namespace_overrides[i],
            )
            caplog.info("Dish %s configured: %s", d, dish)
            dishes.append(dish)
    caplog.info("Configured %d dishes", len(dishes))
    return dishes


@pytest.fixture()
def notebook_output_dir() -> pathlib.Path:
    """Get output directory for notebook."""
    timestr = time.strftime("%Y%m%d-%H%M")
    nod = pathlib.Path(
        project_root(),
        f"notebook-execution-data/configure_scan_for_commissioning/execution-{timestr}"
    )
    caplog.info("Output directory is %s", nod)
    return nod


@pytest.fixture()
def test_equipment() -> TangoTestEquipment:
    caplog.info("Get test equipment")
    return teq


@pytest.fixture()
def test_equipment_state(test_equipment: TangoTestEquipment) -> TestEquipmentModel:
    """
    Configure test equipment state.

    :param test_equipment: Tango devices for test equipment
    """
    return get_equipment_model(teq)


@pytest.fixture()
def monitor_plot() -> TestEquipmentMonitorPlot:
    """
    Get test equipment monitor plot
    :return: test equipment monitor plot
    """
    return get_test_equipment_monitor_plot()
