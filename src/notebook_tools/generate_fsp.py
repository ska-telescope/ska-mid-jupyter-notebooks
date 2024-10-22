# pylint: disable=C,R
import math

FS_BW = 198180864
HALF_FS_BW = 99090432
CHANNEL_WIDTH = 13440

def generate_fsp_list(start_freq: int, end_freq: int, target_talons: list[int]) -> list:
    """
    Generates a list of FSP json objects, given the start frequency, end frequency, channel list, and target talons
    Arguments:
    start_freq -- Requested started frequency for visibilities
    end_freq -- Requested started frequency for visibilities
    target_talons -- The list of talons boards to use, if using 1 or 4 of them, used to generate FSPs.
    Returns:
    A list of JSON FSP config JSON objects.
    """
    fsp_list = []
    
    coarse_channel_low = math.floor((start_freq + HALF_FS_BW)/FS_BW)
    coarse_channel_high = math.floor((end_freq + HALF_FS_BW)/FS_BW)

    num_fsps = list(range(coarse_channel_low, coarse_channel_high + 1))

    if len(num_fsps) > len(target_talons):
        raise Exception('Required FSPs is lower than number of deployed talon boards')
    
    for i in range(len(num_fsps)):
        sorted_talons = sorted(target_talons)
        fsp_list.append(sorted_talons[i])
    
    return fsp_list

def calculate_channel_count(start_freq: int, end_freq: int, channel_width: int) -> int:
    """
    Generates a list of FSP json objects, given the start frequency, end frequency, channel list, and target talons
    Arguments:
    start_freq -- Requested started frequency for visibilities
    end_freq -- Requested started frequency for visibilities
    channel_width -- provided channel width in configure json
    Returns:
    The expected channel count to process frequency range given the start,end, and width
    """
    return (((end_freq - channel_width - start_freq) // channel_width) // 20 ) * 20

def calculate_end_freq(start_freq: int, num_fsps_available: int) -> int:
    """
    Generates a list of FSP json objects, given the start frequency, end frequency, channel list, and target talons
    Arguments:
    start_freq -- Requested started frequency for visibilities
    num_fsps_available -- Number of FSPs available which is equal to talons available in your deployment
    Returns:
    The maximum end frequency given the number of FSPs available and requested start frequency
    """
    coarse_channel_low = math.floor((start_freq + HALF_FS_BW)/FS_BW)
    coarse_channel_high = coarse_channel_low + num_fsps_available - 0.01

    return (coarse_channel_high * FS_BW) - HALF_FS_BW



