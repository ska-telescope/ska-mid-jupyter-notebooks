#!/usr/bin/env python3
import argparse
import concurrent.futures
import getpass
import json
import logging
import os

from bite_device_client.bite_client import BiteClient

LOG_FORMAT = "[midcbf_bite.py: line %(lineno)s]%(levelname)s: %(message)s"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    OK = "\x1b[6;30;42m"
    FAIL = "\x1b[0;30;41m"
    ENDC = "\x1b[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_PARAMS_DIR = os.path.join(os.getcwd(), "test_parameters")
CBF_INPUT_DATA_DIR = os.path.join(TEST_PARAMS_DIR, "cbf_input_data")
BITE_CONFIGS_DIR = os.path.join(CBF_INPUT_DATA_DIR, "bite_config_parameters")
JSON_DIR = os.path.join(os.getcwd(), "bite_device_client/json")
BASIC_TEST_PARAMS_FILE = os.path.join(JSON_DIR, "basic_test_parameters.json")

DOWNLOAD_CHUNK_BYTES = 1024
GITLAB_PROJECTS_URL = "https://gitlab.drao.nrc.ca/api/v4/projects/"
GITLAB_API_HEADER = {
    "PRIVATE-TOKEN": f'{os.environ.get("GIT_ARTIFACTS_TOKEN")}'
}


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    logger_ = logging.getLogger("midcbf_bite.py")
    logger_.info(f"User: {getpass.getuser()}")
    parser = argparse.ArgumentParser(description="Talon DX BITE Utility")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "--talon-bite-config",
        help="Configure the BITE devices on the Talon DX board",
        action="store_true",
    )
    parser.add_argument(
        "--talon-bite-lstv-replay",
        help="Start LSTV Replay on the Talon DX board",
        action="store_true",
    )
    parser.add_argument(
        "--talon-bite-stop-lstv-replay",
        help="Stop LSTV Replay on the Talon DX board",
        action="store_true",
    )
    parser.add_argument(
        "--bite_mac_address", type=str, default="00:11:22:33:44:55"
    )
    parser.add_argument("--talon_under_test", type=str)
    parser.add_argument(
        "--input_data",
        help="Select the set of CBF Input Data to be used in BITE configuration.",
        type=str,
    )
    parser.add_argument(
        "--test",
        help="Select the Test ID to configure BITE according to the parameters defined in that test.",
        type=str,
    )
    # Manual input data parameters (these are otherwise specified in sets of CBF Input Data)
    parser.add_argument(
        "--boards",
        help="Select the talon boards to be used in BITE configuration by their board numbers, separated by commas. The board number must match one of the VCC ID in ext_config/initial_system_param.json",
        type=str,
        default="3",
    )
    parser.add_argument(
        "--packet_rate_scale_factor",
        type=float,
        default=1.0,
        help="Specify the packet rate scale factor (default = 1.0)",
    )

    args = parser.parse_args()
    bite_receptors = []

    test_data_path = os.path.join(TEST_PARAMS_DIR, "tests.json")
    cbf_input_data_path = os.path.join(
        CBF_INPUT_DATA_DIR, "cbf_input_data.json"
    )
    bite_configs_path = os.path.join(BITE_CONFIGS_DIR, "bite_configs.json")
    filters_path = os.path.join(BITE_CONFIGS_DIR, "filters.json")

    if not os.path.exists(test_data_path):
        logger_.info(
            f"Test parameter file is not found at {test_data_path}. Using the default in {BASIC_TEST_PARAMS_FILE}"
        )
        test_data_path = BASIC_TEST_PARAMS_FILE
    if not os.path.exists(cbf_input_data_path):
        logger_.info(
            f"CBF Input Data file is not found at {cbf_input_data_path}. Using the default in {BASIC_TEST_PARAMS_FILE}"
        )
        cbf_input_data_path = BASIC_TEST_PARAMS_FILE
    if not os.path.exists(bite_configs_path):
        logger_.info(
            f"BITE config file is not found at {bite_configs_path}. Using the default in {BASIC_TEST_PARAMS_FILE}"
        )
        bite_configs_path = BASIC_TEST_PARAMS_FILE
    if not os.path.exists(filters_path):
        logger_.info(
            f"Filters definition file is not found at {filters_path}. Using the default in {BASIC_TEST_PARAMS_FILE}"
        )
        filters_path = BASIC_TEST_PARAMS_FILE

    with open(test_data_path) as f:
        test_data = json.load(f)["tests"]
    with open(cbf_input_data_path) as f:
        cbf_input_data = json.load(f)["cbf_input_data"]

    # If --test has been specified, use the CBF Input Data ID in that test to get the parameters for each receptor.
    if args.test and args.input_data is None:
        try:
            bite_receptors = cbf_input_data.get(
                test_data[args.test]["cbf_input_data"]
            ).get("receptors")
        except KeyError:
            parser.error(
                f"Could not locate the given test ID in the tests parameter file: {args.test}"
            )

    # Or, if --input_data has been specified, get the BITE parameters defined for that CBF Input Data ID.
    elif args.input_data and args.test is None:
        try:
            bite_receptors = cbf_input_data.get(args.input_data).get(
                "receptors"
            )
        except KeyError:
            parser.error(
                f"Could not locate this CBF Input Data ID in the cbf_input_data parameter file: {args.input_data}"
            )

    # If both --test and --input data have been provided, there is either a conflict in the specified input parameters,
    # or they match and there was no reason to enter both. Intended usage is either one or the other.
    elif args.test and args.input_data:
        parser.error(
            "Cannot provide both --test and --input_data. Only one is required, and there may be conflicting input parameters if both the Test and the CBF Input Data IDs are specified."
        )

    # If no parameter arguments other than --boards have been provided, as is the case in EC's 'talon-bite-config' Make target,
    # use only basic (default) test parameters.
    else:
        boards_list = (args.boards).split(",")
        logger_.info(
            f"No test parameter arguments provided. Defaulting to basic test parameters on boards: {boards_list}"
        )
        for b in boards_list:
            bite_receptors.append(
                cbf_input_data.get(
                    test_data["basic_test"]["cbf_input_data"]
                ).get("receptors")[int(b) - 1]
            )

    logger_.info(f"BITE receptors: {bite_receptors}")

    if args.talon_bite_config:

        def talon_bite_config_thread(receptor, args):
            bite = BiteClient(f"talon{receptor['talon']}_test", False)
            bite.init(
                bite_config_id=receptor.get("bite_config_id"),
                bite_configs_path=bite_configs_path,
                filters_path=filters_path,
                freq_offset_k=receptor.get("sample_rate_k"),
            )
            bite.configure_bite(
                dish_id=receptor.get("dish_id"),
                bite_initial_timestamp_time_offset=receptor.get(
                    "bite_initial_timestamp_time_offset"
                ),
                talon_inst=args.talon_under_test,
                bite_mac_address=args.bite_mac_address,
            )

        logger_.info("Talon BITE Configure")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(talon_bite_config_thread, receptor, args)
                for receptor in bite_receptors
            ]
            [f.result() for f in futures]  # wait for completion

    elif args.talon_bite_lstv_replay:
        logger_.info("Talon BITE LSTV Replay")
        for i, receptor in enumerate(bite_receptors):
            bite = BiteClient(f"talon{bite_receptors[i]['talon']}_test", False)
            bite.init(
                bite_config_id=receptor.get("bite_config_id"),
                bite_configs_path=bite_configs_path,
                filters_path=filters_path,
                freq_offset_k=receptor.get("sample_rate_k"),
            )
            bite.start_lstv_replay(args.packet_rate_scale_factor)
    elif args.talon_bite_stop_lstv_replay:
        logger_.info("Stop Talon BITE LSTV Replay")
        for i, receptor in enumerate(bite_receptors):
            bite = BiteClient(f"talon{bite_receptors[i]['talon']}_test", False)
            bite.init(
                bite_config_id=receptor.get("bite_config_id"),
                bite_configs_path=bite_configs_path,
                filters_path=filters_path,
                freq_offset_k=receptor.get("sample_rate_k"),
            )
            bite.stop_lstv_replay()
