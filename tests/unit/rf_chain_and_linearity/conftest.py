"""This module contains test harness elements common to all unit tests."""

import logging
import os
import pathlib
import pytest
import time
from typing import List

import tango

from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_scripting import oda_helper
from ska_oso_scripting.objects import SubArray, Telescope
from ska_mid_jupyter_notebooks.cluster.cluster import Environment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.helpers.path import project_root
from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec
from ska_mid_jupyter_notebooks.sut.state import (
    get_telescope_state,
    TelescopeDeviceModel,
    TelescopeModel,
)
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot
from ska_mid_jupyter_notebooks.test_equipment.rendering import (
    get_test_equipment_monitor_plot,
    TestEquipmentMonitorPlot,
)
from ska_mid_jupyter_notebooks.test_equipment.state import get_equipment_model, TestEquipmentModel
from ska_mid_jupyter_notebooks.test_equipment.test_equipment import TangoTestEquipment
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand
from ska_oso_pdm.entities.common.sb_definition import SBDefinition

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)

dishlmc_enabled: bool = True
DISH_IDS: list[str] = ["0001", "0036"]
BRANCH_NAME: str = "at-1958-rf-chain-linearity-performance"
SUT_NAMESPACE_OVERRIDE: str = ""
DISH_NAMESPACE_OVERRIDES: list[str] = ["", ""]
SUBARRAY_ID: int = 1
SUBARRAY_COUNT: int = 1
DEVICE_MODEL: TelescopeDeviceModel = TelescopeDeviceModel(DISH_IDS, SUBARRAY_COUNT)

EXECUTON_ENVIRONMENT: Environment = Environment.CI
teq: TangoTestEquipment = TangoTestEquipment()

SYSTEM_UNDER_TEST: TangoSUTDeployment = TangoSUTDeployment(
    BRANCH_NAME,
    EXECUTON_ENVIRONMENT,
    namespace_override=SUT_NAMESPACE_OVERRIDE,
    subarray_index=SUBARRAY_ID,
)
SUB: SubArray = SubArray(SUBARRAY_ID)
TEL = Telescope()
OBSERVATION = ObservationSB()

@pytest.fixture()
def sut() -> TangoSUTDeployment:
    caplog.info("SUT configured: %s", str(SYSTEM_UNDER_TEST))
    return SYSTEM_UNDER_TEST


@pytest.fixture()
def telescope_state() -> TelescopeModel | None:
    tel_state: TelescopeModel | None
    try:
        caplog.info("Get telescope state for device model: %s", repr(DEVICE_MODEL))
        tel_state = get_telescope_state(DEVICE_MODEL, SYSTEM_UNDER_TEST)
    except tango.DevFailed as terr:
        caplog.error(f"Tango error in telescope state: {terr.args[0].desc.strip()}")
        tel_state = None
    except Exception as oerr:
        caplog.error(f"Error in telescope state: %s", oerr)
        tel_state = None
    return tel_state


@pytest.fixture()
def dish_deployments() -> List[TangoDishDeployment]:
    dishes = []
    if dishlmc_enabled:
        for i, d in enumerate(DISH_IDS):
            dish = TangoDishDeployment(
                f"ska{d[1:]}",
                branch_name=BRANCH_NAME,
                environment=EXECUTON_ENVIRONMENT,
                namespace_override=DISH_NAMESPACE_OVERRIDES[i],
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


@pytest.fixture()
def dish_ids() -> list[str]:
    """
    Get IDs for dishes.

    :return: list of dish IDs
    """
    return DISH_IDS


@pytest.fixture()
def subarray_count() -> int:
    """
    Get number of subarrays

    :return: number of subarrays
    """
    return SUBARRAY_COUNT


@pytest.fixture()
def telescope_monitor_plot() -> TelescopeMononitorPlot:
    return TelescopeMononitorPlot(plot_width=900, plot_height=200)


@pytest.fixture()
def eb_id() -> str | None:
    """
    Setup ODA.

    :return: the EB of the ODA thing
    """
    os.environ["ODA_URI"] = (
        "http://ingress-nginx-controller-lb-default.ingress-nginx.svc.miditf.internal.skao.int/ska-db-oda/api/v1/"
    )
    try:
        ebid = oda_helper.create_eb()
        print(f"Execution Block ID: {ebid}")
    except ConnectionError as cerr:
        caplog.error("Could not create EB: %s", cerr)
        ebid = None
    return ebid

@pytest.fixture()
def sub() -> SubArray | None:
    return SUB


@pytest.fixture()
def tel() -> Telescope | None:
    return TEL


@pytest.fixture()
def observation() -> ObservationSB | None:
    """Make an observation."""
    return OBSERVATION


DEFAULT_TARGET_SPECS = {
    "flux calibrator": TargetSpec(
        target_sb_detail={
            "co_ordinate_type": "Equatorial",
            "ra": "19:24:51.05 degrees",
            "dec": "-29:14:30.12 degrees",
            "reference_frame": "ICRS",
            "unit": ("hourangle", "deg"),
            "pointing_pattern_type": {
                "single_pointing_parameters": SinglePointParameters(
                    offset_x_arcsec=0.0, offset_y_arcsec=0.0
                ),
                "raster_parameters": RasterParameters(
                    row_length_arcsec=0.0,
                    row_offset_arcsec=0.0,
                    n_rows=1,
                    pa=0.0,
                    unidirectional=False,
                ),
                "star_raster_parameters": StarRasterParameters(
                    row_length_arcsec=0.0,
                    n_rows=1,
                    row_offset_angle=0.0,
                    unidirectional=False,
                ),
                "five_point_parameters": FivePointParameters(offset_arcsec=0.0),
                "cross_scan_parameters": CrossScanParameters(offset_arcsec=0.0),
                "active_pointing_pattern_type": "single_pointing_parameters",
            },
        },
        scan_type="flux calibrator",
        band=ReceiverBand.BAND_2,
        channelisation="vis_channels9",
        polarisation="all",
        processing="test-receive-addresses",
        dish_ids=DISH_IDS,
        target=None,
    ),
    "M87": TargetSpec(
        target_sb_detail={
            "co_ordinate_type": "Equatorial",
            "ra": "19:24:51.05 degrees",
            "dec": "-29:14:30.12 degrees",
            "reference_frame": "ICRS",
            "unit": ("hourangle", "deg"),
            "pointing_pattern_type": {
                "single_pointing_parameters": SinglePointParameters(
                    offset_x_arcsec=0.0, offset_y_arcsec=0.0
                ),
                "raster_parameters": RasterParameters(
                    row_length_arcsec=0.0,
                    row_offset_arcsec=0.0,
                    n_rows=1,
                    pa=0.0,
                    unidirectional=False,
                ),
                "star_raster_parameters": StarRasterParameters(
                    row_length_arcsec=0.0,
                    n_rows=1,
                    row_offset_angle=0.0,
                    unidirectional=False,
                ),
                "five_point_parameters": FivePointParameters(offset_arcsec=0.0),
                "cross_scan_parameters": CrossScanParameters(offset_arcsec=0.0),
                "active_pointing_pattern_type": "single_pointing_parameters",
            },
        },
        scan_type="M87",
        band=ReceiverBand.BAND_2,
        channelisation="vis_channels10",
        polarisation="all",
        processing="test-receive-addresses",
        dish_ids=DISH_IDS,
        target=None,
    ),
}


@pytest.fixture()
def default_target_specs() -> dict:
    return DEFAULT_TARGET_SPECS

try:
    PDM_ALLOCATION = OBSERVATION.generate_pdm_object_for_sbd_save(DEFAULT_TARGET_SPECS)
except KeyError as kerr:
    caplog.error("Could not allocate PDM: %s", kerr)
    PDM_ALLOCATION = None


@pytest.fixture()
def pdm_allocation() -> SBDefinition | None:
    return PDM_ALLOCATION
