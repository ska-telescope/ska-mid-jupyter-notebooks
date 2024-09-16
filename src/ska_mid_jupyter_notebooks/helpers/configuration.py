from typing import Dict


def get_band_frequency_limits(
    band_number: int,
    band_overlap: float = 0.2e9,
    band_width: float = 0.7945e9,
    f_min_b1: float = 0.2964e9,
) -> Dict[str, float]:
    """_summary_

    :param band_number: band of interest
    :type band_number: int
    :param band_overlap: frequency overlay between bands in Hz, defaults to 0.2e9 Hz
    :type band_overlap: float, optional
    :param band_width: Band width in Hz, defaults to 0.7945e9 Hz
    :type band_width: float, optional
    :param f_min_b1: f_min for band 1 in Hz, defaults to 0.2964e9 Hz
    :type f_min_b1: float, optional
    :return: f_min and f_max in Hz for the respective band
    :rtype: Dict[str, float]
    """

    f_min_bn = f_min_b1 + (band_number - 1) * (band_width - band_overlap)
    f_max_bn = f_min_bn + band_width

    return {"f_min": f_min_bn, "f_max": f_max_bn}
