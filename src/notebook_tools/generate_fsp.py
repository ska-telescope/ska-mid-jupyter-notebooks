# pylint: disable=C,R
import math

FS_BW = 198180864
HALF_FS_BW = 99090432
CHANNEL_WIDTH = 13440
FINE_CHANNELS_PER_FSP = 14880


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

    coarse_channel_low = math.floor((start_freq + HALF_FS_BW) / FS_BW)
    coarse_channel_high = math.floor((end_freq + HALF_FS_BW) / FS_BW)

    num_fsps = list(range(coarse_channel_low, coarse_channel_high + 1))

    # if len(num_fsps) > len(target_talons):
    #     raise Exception(f"Required FSPs is lower than number of deployed talon boards {num_fsps}")

    for i in range(len(num_fsps)):
        sorted_talons = sorted(target_talons)
        fsp_list.append(sorted_talons[i])

    return fsp_list


def generate_band_params(band_num: int):
    """Generate start frequency, end frequency and channel count per band.
    Generates start_freq and channel count
    14880 = Number of fine channels a single FSP can provide
    13440 = Bandwidth per fine channel
    2MHz = Overlap (496.4e6 - 296.4e6)

    :param band_num: _description_
    :type band_num: int
    :return: _description_
    :rtype: _type_
    """
    band_params = {}
    course_channel_overlap = 2.1e06
    if band_num == 1:
        band_params["start_freq"] = 350e6  # 330e6
        course_channel_start = 296.4e6
    elif band_num == 2:
        band_params["start_freq"] = 940e6
        course_channel_start = 890.9e6

    band_params["channel_count"] = int(
        (
            math.floor(
                (
                    FINE_CHANNELS_PER_FSP * 4
                    - (
                        math.floor(
                            (band_params["start_freq"] - course_channel_start) / CHANNEL_WIDTH
                        )
                        + (math.floor((course_channel_overlap / CHANNEL_WIDTH) * 3))
                    )
                )
                / 20
            )
            * 20
        )
    )

    band_params["end_freq"] = (band_params["channel_count"] * CHANNEL_WIDTH) + band_params[
        "start_freq"
    ]

    return band_params


def calculate_channel_count(start_freq: int, end_freq: int) -> int:
    """
    Generates a list of FSP json objects, given the start frequency, end frequency, channel list, and target talons
    Arguments:
    start_freq -- Requested started frequency for visibilities
    end_freq -- Requested started frequency for visibilities
    Returns:
    The expected channel count to process frequency range given the start,end, and width
    """
    return (((end_freq - CHANNEL_WIDTH - start_freq) // CHANNEL_WIDTH) // 20) * 20


def calculate_end_freq(start_freq: int, num_fsps_available: int) -> int:
    """
    Generates a list of FSP json objects, given the start frequency, end frequency, channel list, and target talons
    Arguments:
    start_freq -- Requested started frequency for visibilities
    num_fsps_available -- Number of FSPs available which is equal to talons available in your deployment
    Returns:
    The maximum end frequency given the number of FSPs available and requested start frequency
    """
    coarse_channel_low = math.floor((start_freq + HALF_FS_BW) / FS_BW)
    coarse_channel_high = coarse_channel_low + num_fsps_available - 0.01

    return int((coarse_channel_high * FS_BW)) - HALF_FS_BW
