def generate_fsp_list(fsp_count: int, target_talons: list[int]):
    """
    Generates a list of FSP json objects, given a number to generate, and the target talons.
    Arguments:
    fsp_count -- Number of FSPs to generate
    target_talons -- The list of talons boards to use, if using 1 or 4 of them, used to generate FSPs.
    Returns:
    A list of JSON FSP config JSON objects.
    """
    fsp_list = []
    # For singular FSP, set up based on first target talon used
    # If using 4 boards, must also match
    if fsp_count == 1 or fsp_count == 4:
        offset = 0
        for board in target_talons:
            fsp = {}
            fsp["fsp_id"] = board
            fsp["function_mode"] = "CORR"
            fsp["frequency_slice_id"] = board
            fsp["zoom_factor"] = 0
            fsp["integration_factor"] = 10
            fsp["output_link_map"] = [[0, 1]]
            fsp["channel_offset"] = 14880 * offset
            fsp["zoom_window_tuning"] = 450000
            fsp_list.append(fsp)
            offset += 1
    else:
        for fsp_id in range(fsp_count):
            fsp = {}
            fsp["fsp_id"] = fsp_id + 1
            fsp["function_mode"] = "CORR"
            fsp["frequency_slice_id"] = fsp_id + 1
            fsp["zoom_factor"] = 0
            fsp["integration_factor"] = 10
            fsp["output_link_map"] = [[0, 1]]
            fsp["channel_offset"] = 14880 * fsp_id
            fsp["zoom_window_tuning"] = 450000
            fsp_list.append(fsp)

    return fsp_list
