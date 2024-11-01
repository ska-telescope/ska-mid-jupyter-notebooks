# pylint: disable=C,R


def generate_fsp_list(fsp_count: int, target_talons: list[int]) -> list:
    """
    Generates a list of FSP json objects, given a number to generate, and the target talons.
    Arguments:
    fsp_count -- Number of FSPs to generate
    target_talons -- The list of talons boards to use, if using 1 or 4 of them, used to generate FSPs.
    Returns:
    A list of JSON FSP config JSON objects.
    """
    fsp_list = []
    offset = 0
    for board in range(fsp_count):
        fsp = {}
        fsp["fsp_id"] = target_talons[board]  # Set fsp id equal to boards
        fsp["function_mode"] = "CORR"
        fsp["frequency_slice_id"] = target_talons[board]  # equal to fsp id
        fsp["zoom_factor"] = 0
        fsp["integration_factor"] = 10
        fsp["output_link_map"] = [[0, 1]]
        fsp["channel_offset"] = 14880 * offset  # increment by 14800 for each FSP, starting from 0
        fsp["zoom_window_tuning"] = 450000
        fsp_list.append(fsp)
        offset += 1
    return fsp_list
