import re
from enum import Enum

# Regex patterns - compiled for reuse efficiency
INCOMING_COMMAND_CALL_REGEX_PATTERN = re.compile(r"-> (\w+\.\w+)\(\)")
RETURN_COMMAND_CALL_REGEX_PATTERN = re.compile(r"^(.*) <- (\w+\.\w+)\(\)")

LRC_RETURN_VAL_REGEX_PATTERN = re.compile(r"\(\[(.*)\], \['(.*)'\]\)")
LRC_TUPLE_REGEX_PATTERN = re.compile(r"'([0-9a-zA-Z._]*)', '([^']*)'")

LOG_REGEX_PATTERN = re.compile(
    r"([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|(.*)"
)
EVENT_REGEX_PATTERN = re.compile(r"([^\t]*)\t([^\t]*)\t([^\t]*)\t(.*)")
DEBUG_PATCH_FORWARD_REGEX_PATTERN = re.compile(r"->\s*(\w+)\.(\w+)\(\)")
ISO_DATE_STRING_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z")

LOG_LRC_RESULT_REGEX_PATTERN = re.compile(
    r"Received longRunningCommandResult event for\s*device:?\s*(.*?),?\s*with value:\s*\('(.*?)',\s*'\[\d,\s*\"(.*?)\"\]'\)"
)
INVOKE_EXECUTE_COMMAND_REGEX_PATTERN = re.compile(
    r"(?:Invoked|About to execute command) \[?(.*?)\]? on device (\[.*?\]|[^\[]+)"
)
CSP_SDP_RELEASE_RESOURCES_COMMAND_REGEX_PATTERN = re.compile(
    r"(.*) command invoked on (?:CSP|SDP) Subarray Leaf Node  (.*)"
)
K_VALUES_TO_DISH_REGEX_PATTERN = re.compile(r"Invoking (.*) on dish adapter (.*)")
CSP_SDP_ON_OFF_COMMAND_REGEX_PATTERN = re.compile(r"Invoking (.*) command for (.*) devices\s*")
INVOKING_COMMAND_REGEX_PATTERN = re.compile(r"Invoking (.*) command on(?:\:)\s*(.*)")
COMMAND_INVOKED_REGEX_PATTERN = re.compile(r"(.*) command (?:is\s)invoked (?:on|from) (.*)")

# Limits for spammy calls
TRACK_LOAD_TABLE_LIMIT = 8

# Log time adjustment due to delays
GENERAL_LOG_TIME_ADJUSTMENT_SECONDS = 0.07
DEBUG_LOG_TIME_ADJUSTMENT_SECONDS = 0.23


class DeviceGroup(Enum):
    """Enum class for determining device colours on the diagram"""

    TMC = ("TMC Mid", "Lavender")
    CSP = ("CSP Mid", "DCE3C7")  # Sage green
    SDP = ("SDP Mid", "LightYellow")
    DISHES = ("Dishes", "LightBlue")
    UNKNOWN = ("Unknown", "LightGrey")


def define_tracked_device_trls(
    dish_indexes: list[str], sut_namespace: str, dish_namespaces: list[str]
) -> list[str]:
    """Create the list of tango devices to track events on based on dishes and namespaces"""
    # Define tango hosts
    sut_tango_host = f"tango-databaseds.{sut_namespace}.svc.miditf.internal.skao.int:10000"
    dish_tango_hosts = [
        f"tango-databaseds.{dish_namespace}.svc.miditf.internal.skao.int:10000"
        for dish_namespace in dish_namespaces
    ]

    # Define device TRLs (for events)
    tracked_device_trls = [
        f"{sut_tango_host}/ska_mid/tm_central/central_node",
        f"{sut_tango_host}/ska_mid/tm_subarray_node/1",
        f"{sut_tango_host}/ska_mid/tm_leaf_node/csp_master",
        f"{sut_tango_host}/ska_mid/tm_leaf_node/csp_subarray01",
        f"{sut_tango_host}/mid-csp/subarray/01",
        f"{sut_tango_host}/mid_csp_cbf/sub_elt/controller",
        f"{sut_tango_host}/mid_csp_cbf/sub_elt/subarray_01",
        # f'{sut_tango_host}/mid-sdp/subarray/01',
    ]

    tracked_device_trls.extend(
        f"{sut_tango_host}/ska_mid/tm_leaf_node/d0{index}" for index in dish_indexes
    )

    tracked_device_trls.extend(
        f"{dish_host}/mid-dish/dish-manager/ska{index}"
        for dish_host, index in zip(dish_tango_hosts, dish_indexes)
    )

    tracked_device_trls.extend(
        f"{dish_host}/mid-dish/ds-manager/ska{index}"
        for dish_host, index in zip(dish_tango_hosts, dish_indexes)
    )

    return tracked_device_trls


def define_pods_for_logs(
    dish_indexes: list[str], sut_namespace: str, dish_namespaces: list[str]
) -> dict[str, list[str]]:
    """Create a dictionary for the pods in each namespace that logs will be retrieved from"""
    # Define pods to get logs from
    csp_subarray_pod_name = (
        f"ds-cspsubarray-{sut_namespace}-subarray1-0"
        if sut_namespace in ["staging", "integration"]
        else "ds-cspsubarray-sut-subarray1-0"
    )

    sut_device_pods = [
        "ds-centralnode-01-0",
        "ds-subarraynode-01-0",
        "ds-cspmasterleafnode-01-0",
        csp_subarray_pod_name,
        "ds-cspsubarrayleafnode-01-0",
        "ds-cbfcontroller-controller-0",
        "ds-cbfsubarray-cbfsubarray-0",
    ]
    sut_device_pods.extend(f"ds-dishleafnode-{index}-0" for index in dish_indexes)

    dish_device_pods = [
        [
            f"ds-dishmanager-{index}-0",
            f"ds-dsmanager-{index}-0",
        ]
        for index in dish_indexes
    ]

    # Dictionary containing namespaces as keys and corresponding pods as values
    namespaces_pods = {
        sut_namespace: sut_device_pods,
    }
    namespaces_pods.update(
        {
            dish_namespace: dish_pods
            for dish_namespace, dish_pods in zip(dish_namespaces, dish_device_pods)
        }
    )

    return namespaces_pods


def setup_device_hierarchy(dish_indexes: list[str]) -> list[list[str]]:
    """Create the list of device lists used to order and group the sequence diagram"""
    # Declare likely callers for each device
    device_hierarchy = [
        ["notebook", "tm_central.central_node", "tm_leaf_node.csp_master", "mid-csp.control.0"],
        ["tm_central.central_node", "tm_leaf_node.sdp_master"],
        ["tm_central.central_node", "tm_subarray_node.2"],
        ["tm_central.central_node", "tm_subarray_node.1"],
        ["tm_subarray_node.1", "tm_leaf_node.sdp_subarray01"],  # 'mid-sdp.subarray.01'],
        ["tm_subarray_node.1", "tm_leaf_node.csp_subarray01", "mid-csp.subarray.01"],
    ]

    # Use a for loop because the dish devices should be grouped for the diagram
    for index in dish_indexes:
        device_hierarchy.append(
            [
                "tm_subarray_node.1",
                f"tm_leaf_node.d0{index}",
                f"dish-manager.ska{index}",
                f"ds-manager.ska{index}",
            ]
        )

        device_hierarchy.append([f"dish-manager.ska{index}", f"ska{index}.spfrxpu.controller"])

        device_hierarchy.append([f"dish-manager.ska{index}", f"simulator_spfc.ska{index}"])

    return device_hierarchy
