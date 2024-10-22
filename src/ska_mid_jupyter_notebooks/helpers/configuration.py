# pylint: disable=C,R
from typing import Dict


def get_band_frequency_limits(
    band_number: int,
    band_overlap: float = 0.2e9,
    band_width: float = 0.7945e9,
    freq_min_b1: float = 0.2964e9,
) -> Dict[str, float]:
    """_summary_

    :param band_number: band of interest
    :type band_number: int
    :param band_overlap: frequency overlay between bands in Hz, defaults to 0.2e9 Hz
    :type band_overlap: float, optional
    :param band_width: Band width in Hz, defaults to 0.7945e9 Hz
    :type band_width: float, optional
    :param freq_min_b1: freq_min for band 1 in Hz, defaults to 0.2964e9 Hz
    :type freq_min_b1: float, optional
    :return: freq_min and freq_max in Hz for the respective band
    :rtype: Dict[str, float]
    """

    freq_min_bn = freq_min_b1 + (band_number - 1) * (band_width - band_overlap)
    freq_max_bn = freq_min_bn + band_width

    return {"freq_min": freq_min_bn, "freq_max": freq_max_bn}


def get_dish_namespace(sut_namespace: str, dish_id: str) -> str:
    """_summary_

    :param sut_namespace: Namespace to which the SUT has been deployed
    :type sut_namespace: str
    :param dish_id: Dish ID e.g SKA001, SKA002
    :type dish_id: str
    :return: Namespace to which the dishes are deployed
    :rtype: _type_
    """
    if sut_namespace in ["staging", "integration"]:
        return f"{sut_namespace}-dish-lmc-{str.lower(dish_id)}"
    else:
        return f"ci-dish-lmc-{str.lower(dish_id)}-{sut_namespace[15:]}"
