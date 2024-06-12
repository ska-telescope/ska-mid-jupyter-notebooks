"""Basic health test."""

import logging
import os
import pathlib
import time
from typing import List, Tuple

import pytest
import ska_ser_logging  # type: ignore[import-untyped]
from ska_oso_pdm.entities.common.sb_definition import SBDefinition  # type: ignore[import-untyped]
from ska_oso_pdm.entities.common.target import (  # type: ignore[import-untyped]
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_pdm.entities.sdp import BeamMapping  # type: ignore[import-untyped]
from ska_oso_scripting import oda_helper  # type: ignore[import-untyped]
from ska_oso_scripting.objects import SubArray, Telescope  # type: ignore[import-untyped]
from ska_tmc_cdm.messages.central_node.sdp import Channel  # type: ignore[import-untyped]
from ska_tmc_cdm.messages.subarray_node.configure.core import (  # type: ignore[import-untyped]
    ReceiverBand,
)

from ska_mid_jupyter_notebooks.cluster.cluster import Environment
from ska_mid_jupyter_notebooks.dish.dish import TangoDishDeployment
from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec, get_default_target_specs_sb
from ska_mid_jupyter_notebooks.sut.rendering import TelescopeMononitorPlot
from ska_mid_jupyter_notebooks.sut.state import (
    TelescopeDeviceModel,
    TelescopeModel,
    get_telescope_state,
)
from ska_mid_jupyter_notebooks.sut.sut import TangoSUTDeployment


@pytest.fixture()
def sut() -> TangoSUTDeployment:
    """
    Get handle for system under test.
    :return: handle for system under test
    """
    return SYSTEM_UNDER_TEST


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
    # nod = pathlib.Path(
    #     project_root(),
    #     f"notebook-execution-data/configure_scan_for_commissioning/execution-{timestr}",
    # )
    nod = pathlib.Path(
        f"./tmp/notebook-execution-data/configure_scan_for_commissioning/execution-{timestr}"
    )
    os.makedirs(nod)
    caplog.info("Output directory is %s", nod)
    return nod


# 3.1.1 Configure Telescope Monitoring
@pytest.fixture()
def telescope_monitor_plot() -> TelescopeMononitorPlot:
    """
    Use monitor plot as a dashboard.
    :return: monitor plot handle
    """
    return TELESCOPE_MONITOR_PLOT


@pytest.fixture()
def dish_ids() -> list[str]:
    """
    Get dish identifiers.

    :return: list od dish IDs
    """
    return DISH_IDS


@pytest.fixture()
def subarray_count() -> int:
    """
    Get subarray count.

    :return: number of subarrays
    """
    return SUBARRAY_COUNT


@pytest.fixture()
def telescope_state() -> TelescopeModel:
    """
    Get telescope state

    :return: state of telescope
    """
    return TELESCOPE_STATE


@pytest.fixture()
def eb_id() -> Tuple[str | None, str]:
    """
    Get execution block identifier

    :return: identifier and status
    """
    return EB_ID, EB_ID_STATUS


@pytest.fixture()
def sub() -> SubArray:
    """
    Get subarray.

    :return: subarray instance
    """
    return SUB


@pytest.fixture()
def tel() -> Telescope:
    """
    Get telescope.

    :return: telescope instance
    """
    return TEL


@pytest.fixture()
def observation() -> ObservationSB:
    """
    Get observation.

    :return: observation instance
    """
    return OBSERVATION


@pytest.fixture()
def target_specs() -> dict:
    """
    Get target specifications.

    :return: dictionary with specifications
    """
    return TARGET_SPECS


@pytest.fixture()
def pdm_allocation() -> SBDefinition:
    """
    Get PDM allocation

    :return: PDM allocation
    """
    return PDM_ALLOCATION


def get_dish_deployments(dishlmc_enabled: bool) -> List[TangoDishDeployment]:
    """
    Get dish deployments.

    :param dishlmc_enabled: flag to enable dish LMC
    :return: list of Tango dish deployments
    """
    dish_deploys: List[TangoDishDeployment] = []
    if dishlmc_enabled:
        for did, ddish in enumerate(DISH_IDS):
            dish = TangoDishDeployment(
                f"ska{ddish}",
                branch_name=str(BRANCH_NAME),
                environment=EXECUTON_ENVIRONMENT,
                namespace_override=DISH_NAMESPACE_OVERRIDES[did],
            )
            print(f"Dish {dish} configured: {dish}")
            dish_deploys.append(dish)
    return dish_deploys


def setup_oda() -> Tuple[str | None, str]:
    """
    Set up the ODA thing.

    :return: tuple with EB ID and status/error
    """
    os.environ["ODA_URI"] = "https://k8s.miditf.internal.skao.int/ska-db-oda/oda/api/v3"
    ebid: str | None
    ebid_status: str
    try:
        ebid = oda_helper.create_eb()
        ebid_status = "OK"
    # pylint: disable-next=broad-except
    except Exception as eb_err:
        caplog.error("Could not create EB: %s", eb_err)
        ebid = None
        ebid_status = str(eb_err)
    caplog.info(f"Execution Block ID: {ebid}")
    return ebid, ebid_status


def get_observation(get_deployments: list[TangoDishDeployment], get_specs: dict) -> ObservationSB:
    """
    Set up observation.

    :param get_deployments: target deployments
    :param get_specs: target specifications
    :return: observation instance
    """
    get_ids = [d.dish_id.upper() for d in get_deployments]
    default_target_specs: dict[str, TargetSpec] = get_default_target_specs_sb(get_ids)
    obs = ObservationSB(target_specs=default_target_specs)

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

    for _key, value in get_specs.items():
        obs.add_channel_configuration(value.channelisation, channel_configuration)

    obs.add_target_specs(get_specs)

    for target_id, _target in get_specs.items():
        obs.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )
    scan_def_id = "flux calibrator"
    obs.add_scan_sequence([scan_def_id])

    print("Observation created")
    return obs


def get_pdm_allocation(obs: ObservationSB, get_specs: dict) -> SBDefinition:
    """
    Get PDM allocation.

    :param obs: observation instance
    :param get_specs: target specifications
    :return: PDM allocation
    """
    pdm_alloc: SBDefinition = obs.generate_pdm_object_for_sbd_save(get_specs)
    return pdm_alloc


# Declare variables
DEBUG_MODE: bool
ENABLE_LOGGING: bool

DEBUG_MODE = True  # This setting enables printing of diagnostics
ENABLE_LOGGING = True  # This enables logging and sets the global log_level to debug
DISHLMC_ENABLED = True  # Set this to true if you have a dish LMC deployment

# Choose option CI / Integration / Staging
EXECUTON_ENVIRONMENT: Environment = Environment.Staging


# Branch name
# -----------
# Set this if you are using an on-demand deployment (i.e. Environment.CI)
# branch_name = None
BRANCH_NAME: str | None = None
branch: str | None = os.getenv("BRANCH_NAME", None)
if branch is not None:
    BRANCH_NAME = branch
else:
    BRANCH_NAME = "at-1958-rf-chain-linearity-performance"

# K8S namespaces
# --------------
# namespace_override parameter can be used to override auto-configured SUT namespace
# sut_namespace_override = ""
SUT_NAMESPACE_OVERRIDE: str
DISH_NAMESPACE_OVERRIDES: list[str]
k8s_ns: str | None = os.getenv("KUBE_NAMESPACE", None)
if k8s_ns is not None:
    SUT_NAMESPACE_OVERRIDE = k8s_ns
    DISH_NAMESPACE_OVERRIDES = []
    DISH_NAMESPACE_OVERRIDES.append(k8s_ns.replace("ci-ska-mid-itf", "ci-dish-lmc-ska001"))
    DISH_NAMESPACE_OVERRIDES.append(k8s_ns.replace("ci-ska-mid-itf", "ci-dish-lmc-ska036"))
else:
    SUT_NAMESPACE_OVERRIDE = ""
    DISH_NAMESPACE_OVERRIDES = ["", ""]

# Subarray details
# ----------------
SUBARRAY_ID: int = 1
SUBARRAY_COUNT: int = 1

if ENABLE_LOGGING:
    ska_ser_logging.configure_logging(logging.DEBUG)
caplog = logging.getLogger(__name__)

# System under test
# -----------------
SYSTEM_UNDER_TEST: TangoSUTDeployment = TangoSUTDeployment(
    BRANCH_NAME,
    EXECUTON_ENVIRONMENT,
    namespace_override=SUT_NAMESPACE_OVERRIDE,
    subarray_index=SUBARRAY_ID,
)
print(f"SUT configured: {str(SYSTEM_UNDER_TEST)}")

DISH_IDS = ["001", "036"]
# namespace_override parameter can be used to override automatically configured dish namespace
DISH_DEPLOYMENTS: List[TangoDishDeployment] = get_dish_deployments(DISHLMC_ENABLED)

# use monitor plot as a dashboard
TELESCOPE_MONITOR_PLOT = TelescopeMononitorPlot(plot_width=900, plot_height=200)

DEVICE_MODEL: TelescopeDeviceModel = TelescopeDeviceModel(DISH_IDS, SUBARRAY_COUNT)
TELESCOPE_STATE: TelescopeModel = get_telescope_state(DEVICE_MODEL, SYSTEM_UNDER_TEST)

# 3.3 Setup ODA
EB_ID: str | None
EB_ID_STATUS: str
EB_ID, EB_ID_STATUS = setup_oda()
caplog.info(f"Execution Block ID: {EB_ID}")

# 3.4 Initialise Telescope and Subarray
# Create Subarray and Telescope instances.
SUB: SubArray = SubArray(SUBARRAY_ID)
TEL: Telescope = Telescope()

TARGET_SPECS: dict = {
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

OBSERVATION: ObservationSB = get_observation(DISH_DEPLOYMENTS, TARGET_SPECS)

PDM_ALLOCATION: SBDefinition = get_pdm_allocation(OBSERVATION, TARGET_SPECS)
