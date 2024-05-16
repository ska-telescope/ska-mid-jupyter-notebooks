"""This module contains test harness elements common to all unit tests."""

import logging
import os
import pathlib
import time
from typing import List

import pytest
import tango
from ska_oso_pdm.entities.common.sb_definition import SBDefinition
from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_scripting import oda_helper
from ska_oso_scripting.objects import SubArray, Telescope
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand

from ska_mid_jupyter_notebooks.cluster.cluster import Environment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.helpers.path import project_root
from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot
from ska_mid_jupyter_notebooks.sut.state import (
    TelescopeDeviceModel,
    TelescopeModel,
    get_telescope_state,
)
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment
from ska_mid_jupyter_notebooks.test_equipment.rendering import (
    TestEquipmentMonitorPlot,
    get_test_equipment_monitor_plot,
)
from ska_mid_jupyter_notebooks.test_equipment.state import TestEquipmentModel, get_equipment_model
from ska_mid_jupyter_notebooks.test_equipment.test_equipment import TangoTestEquipment

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)

DISHLMC_ENABLED: bool = True

# Dish IDs
# --------
DISH_IDS: list[str] = ["0001", "0036"]
caplog.info("Dish IDs %s", DISH_IDS)


@pytest.fixture()
def dish_ids() -> list[str]:
    """
    Get IDs for dishes.

    :return: list of dish IDs
    """
    return DISH_IDS


# Subarray details
SUBARRAY_ID: int = 1
SUBARRAY_COUNT: int = 1
caplog.info("Subarray ID %d (count %d)", SUBARRAY_ID, SUBARRAY_COUNT)


@pytest.fixture()
def subarray_count() -> int:
    """
    Get number of subarrays

    :return: number of subarrays
    """
    return SUBARRAY_COUNT


# Branch name and K8S namespaces
BRANCH_NAME: str = "at-1958-rf-chain-linearity-performance"
SUT_NAMESPACE_OVERRIDE: str = ""
DISH_NAMESPACE_OVERRIDES: list[str] = ["", ""]

# Execution environment
EXECUTON_ENVIRONMENT: Environment = Environment.CI
caplog.info("Created execution environment")


# System under test
# -----------------
SYSTEM_UNDER_TEST: TangoSUTDeployment = TangoSUTDeployment(
    BRANCH_NAME,
    EXECUTON_ENVIRONMENT,
    namespace_override=SUT_NAMESPACE_OVERRIDE,
    subarray_index=SUBARRAY_ID,
)
caplog.info("SUT configured: %s", str(SYSTEM_UNDER_TEST))


@pytest.fixture()
def sut() -> TangoSUTDeployment:
    """
    Get handle for system under test.

    :return: handle for system under test
    """
    return SYSTEM_UNDER_TEST


# Device model
# ------------
DEVICE_MODEL: TelescopeDeviceModel = TelescopeDeviceModel(DISH_IDS, SUBARRAY_COUNT)


@pytest.fixture()
def telescope_state() -> TelescopeModel | None:
    """
    Get handle for telescope state.

    :return: handle for telescope state
    """
    tel_state: TelescopeModel | None
    try:
        caplog.debug("Get telescope state for device model: %s", repr(DEVICE_MODEL))
        tel_state = get_telescope_state(DEVICE_MODEL, SYSTEM_UNDER_TEST)
    except tango.DevFailed as terr:
        caplog.error(f"Tango error in telescope state: {terr.args[0].desc.strip()}")
        tel_state = None
    # pylint: disable-next=broad-except
    except Exception as oerr:
        caplog.error("Error in telescope state: %s", oerr)
        tel_state = None
    return tel_state


# Dish deployments
# ----------------
DISH_DEPLOYMENTS = []
if DISHLMC_ENABLED:
    for i_i, d_d in enumerate(DISH_IDS):
        dish = TangoDishDeployment(
            f"ska{d_d[1:]}",
            branch_name=BRANCH_NAME,
            environment=EXECUTON_ENVIRONMENT,
            namespace_override=DISH_NAMESPACE_OVERRIDES[i_i],
        )
        caplog.debug("Dish %s configured: %s", d_d, dish)
        DISH_DEPLOYMENTS.append(dish)
caplog.info("Configured %d dishes", len(DISH_DEPLOYMENTS))


@pytest.fixture()
def dish_deployments() -> List[TangoDishDeployment]:
    """
    Get handles for dish deployment.

    :return: handles for dish deployment
    """
    return DISH_DEPLOYMENTS


# Notebook output directory
# -------------------------
@pytest.fixture()
def notebook_output_dir() -> pathlib.Path:
    """
    Get output directory for notebook.

    :return: output directory
    """
    timestr = time.strftime("%Y%m%d-%H%M")
    nod = pathlib.Path(
        project_root(),
        f"notebook-execution-data/configure_scan_for_commissioning/execution-{timestr}",
    )
    caplog.debug("Output directory is %s", nod)
    return nod


# Test equipment
# --------------
TESTEQ_IN_THE_LOOP: bool = False
if os.getenv("TESTEQ_IN_THE_LOOP", "False").lower() == "true":
    TESTEQ_IN_THE_LOOP = True
if TESTEQ_IN_THE_LOOP:
    TESTEQ = TangoTestEquipment()
    caplog.info("Test equipment enabled")
else:
    caplog.warning("Test equipment disabled")
    TESTEQ = None


@pytest.fixture()
def test_equipment() -> TangoTestEquipment | None:
    """
    Get handles for test equipment.

    :return: handles for test equipment
    """
    return TESTEQ


@pytest.fixture()
def test_equipment_state() -> TestEquipmentModel | None:
    """
    Configure test equipment state.

    :return: test equipment state
    """
    if not TESTEQ_IN_THE_LOOP:
        return None
    return get_equipment_model(TESTEQ)


@pytest.fixture()
def monitor_plot() -> TestEquipmentMonitorPlot:
    """
    Get test equipment monitor plot

    :return: test equipment monitor plot
    """
    return get_test_equipment_monitor_plot()


@pytest.fixture()
def telescope_monitor_plot() -> TelescopeMononitorPlot:
    """
    Get handle for telescope monitoring.

    :return: handle for telescope monitoring.
    """
    return TelescopeMononitorPlot(plot_width=900, plot_height=200)


# the EB of the ODA thing
os.environ["ODA_URI"] = (
    # pylint: disable-next=line-too-long
    "http://ingress-nginx-controller-lb-default.ingress-nginx.svc.miditf.internal.skao.int/ska-db-oda/api/v1/"
)
EBID: str | None
try:
    EBID = oda_helper.create_eb()
    caplog.info(f"Execution block ID: {EBID}")
except ConnectionError as cerr:
    caplog.error("Could not create execution block ID: %s", cerr)
    EBID = None


@pytest.fixture()
def eb_id() -> str | None:
    """
    Setup ODA.

    :return: the EB of the ODA thing
    """
    return EBID


# Subarray
# --------
SUB: SubArray = SubArray(SUBARRAY_ID)
caplog.info(f"Subarray with ID {SUBARRAY_ID}")


@pytest.fixture()
def sub() -> SubArray | None:
    """
    Get handle for subarray.

    :return: handle for subarray
    """
    return SUB


# Telescope
# ---------
TEL = Telescope()
caplog.info("Created telescope instance")


@pytest.fixture()
def tel() -> Telescope | None:
    """
    Get handle for telescope.

    :return: handle for telescope
    """
    return TEL


# Observation
# -----------
OBSERVATION = ObservationSB()
caplog.info("Created observation instance")


@pytest.fixture()
def observation() -> ObservationSB | None:
    """
    Make an observation.

    :return: handle for observation
    """
    return OBSERVATION


# Default target specs
# --------------------
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
caplog.info("Created default target specification")


@pytest.fixture()
def default_target_specs() -> dict:
    """
    Get default target specification.

    :return: dictionary with specification
    """
    return DEFAULT_TARGET_SPECS


# PDM allocation
# --------------
try:
    PDM_ALLOCATION = OBSERVATION.generate_pdm_object_for_sbd_save(DEFAULT_TARGET_SPECS)
    caplog.info("Created PDM allocation")
except KeyError as kerr:
    caplog.error("Could not allocate PDM key: %s", kerr)
    PDM_ALLOCATION = None
except Exception as eerr:
    caplog.error("Could not allocate PDM: %s", eerr)
    PDM_ALLOCATION = None


@pytest.fixture()
def pdm_allocation() -> SBDefinition | None:
    """
    Get the SB definition.

    :return: SB definition
    """
    return PDM_ALLOCATION
