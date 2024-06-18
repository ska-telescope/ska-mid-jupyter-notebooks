"""End to End testing in the MID ITF."""

import logging
import os
from time import sleep
import json
import pytest

from tango import DeviceProxy, ConnectionFailed

LOG_LEVEL = logging.DEBUG
logging.basicConfig(level=LOG_LEVEL)
caplog = logging.getLogger(__name__)

# Branch name
# -----------
# Set this if you are using an on-demand deployment (i.e. Environment.CI)
BRANCH_NAME: str | None = None
branch: str | None = os.getenv("BRANCH_NAME", None)
if branch is not None:
    BRANCH_NAME = branch
else:
    BRANCH_NAME = "at-1958-rf-chain-linearity-performance"

# Set up parameters
# SKA001_NAMESPACE: str = "ci-dish-lmc-ska001-at-1958-rf-chain-linearity-performance"
# SKA036_NAMESPACE: str = "ci-dish-lmc-ska036-at-1958-rf-chain-linearity-performance"
# SUT_NAMESPACE: str = "ci-ska-mid-itf-at-1958-rf-chain-linearity-performance"

SKA001_NAMESPACE: str = f"ci-dish-lmc-ska001-{BRANCH_NAME}"
SKA036_NAMESPACE: str = f"ci-dish-lmc-ska036-{BRANCH_NAME}"
SUT_NAMESPACE: str = f"ci-ska-mid-itf-{BRANCH_NAME}"
    
# SUT_NAMESPACE: str = "ci-ska-mid-itf-at-2111-update-tmc"
# SUT_NAMESPACE: str = os.getenv("KUBE_NAMESPACE", "ci-ska-mid-itf-at-1958-rf-chain-linearity-performance")

TANGO_HOST: str = f"tango-databaseds.{SUT_NAMESPACE}.svc.miditf.internal.skao.int:10000"
os.environ["TANGO_HOST"] = TANGO_HOST

RECEPTORS: list[str] = ["SKA001", "SKA036"]


@pytest.fixture()
def sut_namespace() -> str:
    return SUT_NAMESPACE


@pytest.fixture()
def ska001_namespace() -> str:
    return SKA001_NAMESPACE


@pytest.fixture()
def ska036_namespace() -> str:
    return SKA036_NAMESPACE


@pytest.fixture()
def receptors() -> list[str]:
    return RECEPTORS


# Config files set up
HOME = os.getenv("HOME")
# DATA_DIR = "../../../data"
DATA_DIR = f"{HOME}/.local/ska-mid-itf-data/"
TMC_CONFIGS: str = f"{DATA_DIR}/mid_telescope/tmc"
SCAN_FILE: str = f"{TMC_CONFIGS}/scan.json"
RELEASE_RESOURCES_FILE: str = f"{DATA_DIR}/release_resources.json"

ASSIGN_RESOURCES_FILE: str = f"{TMC_CONFIGS}/assign_resources.json"
CONFIGURE_SCAN_FILE: str = f"{TMC_CONFIGS}/configure_scan.json"

CBF_CONFIGS: str = f"{DATA_DIR}/mid_telescope/cbf"
DISH_CONFIG_FILE: str = f"{CBF_CONFIGS}/sys_params/load_dish_config.json"


def get_tango(device_name: str) -> DeviceProxy | None:
    """Get proxy for Tango device."""
    tango_device: DeviceProxy | None
    try:
        tango_device = DeviceProxy(device_name)
    except ConnectionFailed as t_err:
        caplog.error("Could not connect proxy %s: %s", device_name, t_err.args[0].desc.strip())
        tango_device = None
    except Exception as eb_err:
        caplog.error("Could not create proxy %s: %s", device_name, eb_err)
        tango_device = None
    return tango_device


@pytest.fixture()
def dish_config_file() -> str:
    """Get name of dish conffiguration file."""
    return DISH_CONFIG_FILE

# Telescope Monitor and Control (TMC) proxies
TMC_CENTRAL_NODE: DeviceProxy | None = get_tango("ska_mid/tm_central/central_node")
TMC_CSP_MASTER: DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/csp_master")
TMC_CSP_SUBARRAY: DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/csp_subarray01")
TMC_SUBARRAY: DeviceProxy | None = get_tango("ska_mid/tm_subarray_node/1")


@pytest.fixture()
def tmc_central_node() -> DeviceProxy | None:
    """Test fixture for Telescope Monitor and Control central node."""
    return TMC_CENTRAL_NODE


@pytest.fixture()
def tmc_csp_master() -> DeviceProxy | None:
    """Test fixture for Telescope Monitor and Control master node."""
    return TMC_CSP_MASTER


@pytest.fixture()
def tmc_csp_subarray() -> DeviceProxy | None:
    """Test fixture for Telescope Monitor and Control Central Signal Processor subarray."""
    return TMC_CSP_SUBARRAY
    

@pytest.fixture()
def tmc_subarray() -> DeviceProxy | None:
    """Test fixture for Telescope Monitor and Control subarray."""
    return TMC_SUBARRAY

# Central Signal Processor (CSP) Local Monitor and Control (LMC) proxies
CSP_CONTROL: DeviceProxy | None = get_tango("mid-csp/control/0")
CSP_SUBARRAY: DeviceProxy | None = get_tango("mid-csp/subarray/01")


@pytest.fixture()
def csp_control() -> DeviceProxy | None:
    """Test fixture for Central Signal Processor control."""
    return CSP_CONTROL


@pytest.fixture()
def csp_subarray() -> DeviceProxy | None:
    """Test fixture for Central Signal Processor subarray."""
    return CSP_SUBARRAY


# Correlator Beam Former (CBF) proxies
CBF_CONTROLLER: DeviceProxy | None = get_tango("mid_csp_cbf/sub_elt/controller")
CBF_SUBARRAY: DeviceProxy | None = get_tango("mid_csp_cbf/sub_elt/subarray_01")


@pytest.fixture()
def cbf_controller() -> DeviceProxy | None:
    """Test fixture for Correlator Beam Former controller."""
    return CBF_CONTROLLER


@pytest.fixture()
def cbf_subarray() -> DeviceProxy | None:
    """Test fixture for Correlator Beam Former subarray."""
    return CBF_SUBARRAY

# Dish Leaf Proxies
DISH_LEAF_NODE_SKA001: DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/d0001")
DISH_LEAF_NODE_SKA036: DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/d0036")


@pytest.fixture()
def dish_leaf_node_ska001() -> DeviceProxy | None:
    """Test fixture for dish leaf node 1."""
    return DISH_LEAF_NODE_SKA001


@pytest.fixture()
def dish_leaf_node_ska036() -> DeviceProxy | None:
    """Test fixture for dish leaf node 36."""
    return DISH_LEAF_NODE_SKA036


# Science Data Processor (SDP) Proxies
SDP_SUBARRAY: DeviceProxy | None = get_tango("mid-sdp/subarray/01")


@pytest.fixture()
def sdp_subarray() -> DeviceProxy | None:
    """Test fixture for Science Data Processor subarray."""
    return SDP_SUBARRAY

# Leaf Nodes
CSP_SUBARRAY_LEAF_NODE : DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/csp_subarray01")
SDP_SUBARRAY_LEAF_NODE: DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/sdp_subarray01")
CSP_MASTER_LEAF_NODE: DeviceProxy | None = get_tango("ska_mid/tm_leaf_node/csp_master")


@pytest.fixture()
def sdp_subarray_leaf_node() -> DeviceProxy | None:
    """Test fixture for  leaf node"""
    return SDP_SUBARRAY_LEAF_NODE


@pytest.fixture()
def csp_master_leaf_node() -> DeviceProxy | None:
    """Test fixture for  leaf node"""
    return CSP_MASTER_LEAF_NODE

                   
mid_tld = "svc.miditf.internal.skao.int"
DISH_DEPLOYMENTS: list[str] = [
    f"tango://tango-databaseds.{SKA001_NAMESPACE}.{mid_tld}:10000/mid-dish/dish-manager/SKA001", 
    f"tango://tango-databaseds.{SKA036_NAMESPACE}.{mid_tld}:10000/mid-dish/dish-manager/SKA036",
]


@pytest.fixture()
def dish_deployments() -> list[str]:
    return DISH_DEPLOYMENTS

