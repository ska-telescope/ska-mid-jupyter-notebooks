import os
import csv
import pathlib
import shutil
import sys
import argparse

import numpy as np
from PyTango import DeviceProxy

import notebook_tools.histogram_client as HistogramClient
from notebook_tools.misc_helper import get_tango_host

timeout_ms = 3000
collect_pre_vcc = True
collect_post_vcc = True
collect_post_16k = True
collect_wideband = True

def collect_statecount_histograms(namespace:str, boards:list[int], lanes:list[int]):
    """ For a given namespace, board and lanes, collect the histogram and wideband data and save to a folder. Then compress the folder to a .zip file."""
    # Parse the boards/lanes from the args
    path = os.getcwd() + "/output-data/" + namespace  # The directory name to use for data storage

    # Set up the initial folder
    folder = pathlib.Path(path)
    folder.mkdir(parents=True, exist_ok=True)

    os.environ["TANGO_HOST"] = get_tango_host(namespace)
    # Mapping higher number boards to correct value
    if len(boards) > 1 and boards[1] == 17:
        boards[1] = 2
        print("Replacing talon17 with talon2 in the target_boards")

    if boards[0] >= 5:
        print("Mapping talons of higher numbers to 1-4")
        boards = list(map(lambda x: x - (((x - 1) // 4) * 4), boards))

    # Collect each of the histograms and statecounts needed
    if collect_pre_vcc:
        collect_histogram("pre_vcc",boards,path)
    if collect_post_vcc:
        collect_histogram_lanes("post_vcc", boards, lanes, path)
    if collect_post_16k:
        collect_histogram_lanes("post_ch16k", boards, lanes,path)
    if collect_wideband: 
        collect_statecount_data(boards)
    # Compress data to zip archive
    shutil.make_archive(namespace, "zip", path)

def collect_histogram(target:str,boards:list[int], path:str):
        """Collects the raw histogram data from the target, for each of the boards provided. If collection is successful, writes the data to a .csv file in the relevant folder."""
        for board in boards:
            print(f"----Board #{board}----")
            device = f"talondx-00{board}/histogram/{target}"
            # Create a histogram client to the VCC device
            client = HistogramClient.HistogramClient(device, timeout_ms)
            # Run the capture command on the device and read the data for the histogram
            success, data = client.capture()
            if success:
                # If we captured the data, store the x and y histograms as 2D lists
                print("Data capture successful, storing")
                histo_x = data[0]
                histo_y = data[1]
                print(f"Pol-x Histogram is of dimensions {len(histo_x)}X{len(histo_x[0])}")
                print(f"Pol-y Histogram is of dimensions {len(histo_y)}X{len(histo_y[0])}")

                histogram_folder = path + f"/talondx-00{board}/" + "/histograms/" + f"/{target}/"
                folder = pathlib.Path(histogram_folder)
                folder.mkdir(parents=True, exist_ok=True)
                with open(str(folder) + f"/{target}_x.csv", "w") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(histo_x)
                    print(f"Wrote histogram data to {histogram_folder}{target}_x.csv")
                with open(str(folder) + f"/{target}_y.csv", "w") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(histo_y)
                    print(f"Wrote histogram data to {histogram_folder}{target}_y.csv")
            else:
                print(f"Could not get {target} data!")

def collect_histogram_lanes(target:str, boards:list[int],lanes:list[int], path:str):
    """Collects the raw histogram data from a target that has lanes, for each of the boards and lanes provided.4
    If collection is successful, writes the data to a .csv file in the relevant folder.
    """
    for board in boards:
        print(f"----Board #{board}----")
        histo_x = [[] for x in range(4)]
        histo_y = [[] for x in range(4)]
        for lane in lanes:
            device = f"talondx-00{board}/histogram/e_{target}_{lane}"
            client = HistogramClient.HistogramClient(device, timeout_ms)
            success, data = client.capture()
            if success:
                print(f"Captured data for Board {board}, lane {lane}")
                histo_x[lane] = data[0]
                histo_y[lane] = data[1]
                print(f"{target}_x Histogram is of dimensions {len(histo_x[lane])}X{len(histo_x[lane][0])}")
                print(f"{target}_y Histogram is of dimensions {len(histo_y[lane])}X{len(histo_y[lane][0])}")
            else:
                print(f"Could not capture data for Board {board}, lane {lane}")
        
        histogram_folder = path + f"/talondx-00{board}/" + "/histograms/" + f"/{target}/"
        folder = pathlib.Path(histogram_folder)
        folder.mkdir(parents=True, exist_ok=True)
        for lane in lanes:
            with open(str(folder) + f"/{target}_x_lane{lane}.csv", "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(histo_x[lane])
                print(f"Wrote histogram data to {histo_x}{target}_x.csv")
            with open(str(folder) + f"/{target}_y_lane{lane}.csv", "w") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(histo_y[lane])
                print(f"Wrote histogram data to {histo_y}{target}_y.csv")

def collect_statecount_data(boards:list[int], path:str):
    """Collects the state count vectors, and power spectrum data from a board. Writes a single .csv file containing all this data to the relevant folder."""
    vcc_statecount_holder = [[] for x in range(4)]
    for board in boards:
        # For each board, link to the wbstatecount under that talon
        device = f"talondx-00{board}/wbstatecount/state_count"
        talon_proxy = DeviceProxy(device)
        # Capture the state count
        talon_proxy.command_inout("state_count_capture")
        # For each of the pieces of data we want to collect, grab the value from the tango device
        # Create a list with it, along with a header text
        state_count_vec_1 = talon_proxy.read_attribute("state_count_vector_1").value
        lst = list(state_count_vec_1)
        lst.insert(0, "State Count Vector 1")
        state_count_vec_1 = np.asarray(lst)

        state_count_vec_2 = talon_proxy.read_attribute("state_count_vector_2").value
        lst = list(state_count_vec_2)
        lst.insert(0, "State Count Vector 2")
        state_count_vec_2 = np.asarray(lst)

        power_spectrum_1 = talon_proxy.read_attribute("psd_vector_1").value
        lst = list(power_spectrum_1)
        lst.insert(0, "Power Spectrum 1")
        power_spectrum_1 = np.asarray(lst)

        power_spectrum_2 = talon_proxy.read_attribute("psd_vector_2").value
        lst = list(power_spectrum_2)
        lst.insert(0, "Power Spectrum 2")
        power_spectrum_2 = np.asarray(lst)

        # Store all these in an array
        vcc_statecount_holder[board] = [
            state_count_vec_1,
            state_count_vec_2,
            power_spectrum_1,
            power_spectrum_2,
        ]
    # For each board, write a file with rows of the data collected for that board
    for board in boards:
        statecount_folder = path + f"/talondx-00{board}/statecounts/"
        folder = pathlib.Path(statecount_folder)
        folder.mkdir(parents=True, exist_ok=True)
        with open(statecount_folder + "talon-" + str(board) + "_statecounts.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(vcc_statecount_holder[board])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Collects histogram and state count data from active namespaces for specified boards/lanes. Stores data to .csv files in a .zip file."
    )
    parser.add_argument('-ns', "--namespace", help = "The id of the namespace to target", type = str, required=True)
    parser.add_argument('-b', "--boards", help = "The list of boards to target", nargs= "+", type = int, required=True)
    parser.add_argument('-l', "--lanes", help = "The lanes to target for post-vcc/16k histograms", nargs= "+", type = int, required=True)
    parser.add_argument('--pre_vcc', help = "Set if pre_vcc histogram data should be collected.")
    parser.add_argument('--post_vcc', help = "Set if pre_vcc histogram data should be collected.")
    parser.add_argument('--post_16k', help = "Set if pre_vcc histogram data should be collected. ")
    args = parser.parse_args()
    print(args)
    boards = list(args.boards)
    lanes = list(args.lanes)
    namespace = args.namespace
    print(f"Targeting namespace:{namespace}, with targeted boards {boards}, lanes {lanes}")
    collect_statecount_histograms(namespace,boards,lanes)
