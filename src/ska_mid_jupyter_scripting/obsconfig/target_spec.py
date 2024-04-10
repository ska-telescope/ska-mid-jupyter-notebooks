from dataclasses import dataclass
from typing import List, Optional, Union
from ska_mid_jupyter_scripting.obsconfig.base import SchedulingBlock
from ska_oso_pdm.entities.common.target import Target as PDMTarget
from ska_tmc_cdm.messages.subarray_node.configure.core import (
    ReceiverBand,
    Target,
)
from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    EquatorialCoordinates,
    EquatorialCoordinatesReferenceFrame,
    FivePointParameters,
    HorizontalCoordinates,
    PointingPattern,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_pdm.entities.common.target import Target as PDMTarget


@dataclass
class TargetSpec:
    # since dishes and band parameters are not required for low imaging scenario hence we have kept default attribute provision

    scan_type: Optional[str] = None
    target: Optional[Union[Target, PDMTarget]] = None
    band: Optional[ReceiverBand] = None
    channelisation: str = None
    polarisation: str = None
    field: str = None
    processing: str = None
    dishes: Optional[str] = None
    dish_ids: Optional[List[str]] = None
    scan_duration: Optional[float] = 10.0  # default scan duration
    target_sb_detail: Optional[dict] = None


class Scan:
    def __init__(self) -> None:
        """
        Initialise the scan instance
        :return: None
        """
        self._instance_count: int = 0

    def _init_scan(self):
        """
        Initialise the scan instance count
        :return: None
        """
        self._instance_count = 0

    def _inc(self):
        """
        Increment the scan instance count
        :return: None
        """
        self._instance_count += 1

    def generate_next_scan_id(self, backwards: bool = False):
        """
        Generate the next scan id
        :param backwards: If True, return the previous scan id
        :return: The next scan id
        """
        self._inc()
        if backwards:
            return {"id": self._instance_count}
        return {"scan_id": self._instance_count}

    @property
    def current_scan_id_value(self) -> int:
        """
        Get the current scan id
        :return: The current scan id
        """
        return self._instance_count

    @property
    def current_scan_id(self) -> dict[str, int]:
        """
        Get the current scan id
        :return: The current scan id
        """
        return {"scan_id": self._instance_count}

    @property
    def current_scan_id_backwards(self) -> dict[str, int]:
        """
        Get the current scan id
        :return: The current scan id
        """
        return {"id": self._instance_count}


class TargetSpecs(SchedulingBlock, Scan):
    def __init__(self, target_specs: dict[str, TargetSpec]) -> None:
        """
        Initialize a new instance of the TargetSpecs class
        :param target_specs: dictionary containing target specs data
        :return: None
        """
        super().__init__()
        self._init_scan()

        self.targets = []
        self.add_target_specs(target_specs)

    def add_target_specs(self, target_specs: dict[str, TargetSpec] = None):
        """
        Add target specs
        :param target_specs: dictionary containing target specs data
        :return: None
        """
        self.target_specs = {**self.target_specs, **target_specs}

        for key, value in self.target_specs.items():
            target_id = key
            if self.target_specs[
                list(self.target_specs.keys())[0]
            ].target_sb_detail:
                parameters = [
                    value.target_sb_detail["pointing_pattern_type"][
                        value.target_sb_detail["pointing_pattern_type"][
                            "active_pointing_pattern_type"
                        ]
                    ]
                ]
                active = parameters[0].kind
                pointing_pattern = PointingPattern(
                    active=active, parameters=parameters
                )

                if value.target_sb_detail["co_ordinate_type"] == "Equatorial":

                    reference_frame = EquatorialCoordinatesReferenceFrame[
                        value.target_sb_detail["reference_frame"].upper()
                    ]
                    reference_coordinate = EquatorialCoordinates(
                        ra=value.target_sb_detail["ra"],
                        dec=value.target_sb_detail["dec"],
                        reference_frame=reference_frame,
                        unit=value.target_sb_detail["unit"],
                    )
                else:
                    reference_coordinate = HorizontalCoordinates(
                        az=value.target_sb_detail["az"],
                        el=value.target_sb_detail["el"],
                        unit=value.target_sb_detail["unit"],
                        reference_frame=value.target_sb_detail[
                            "reference_frame"
                        ],
                    )

                pdm_target = PDMTarget(
                    target_id=target_id,
                    pointing_pattern=pointing_pattern,
                    reference_coordinate=reference_coordinate,
                )
                value.target = pdm_target

                if len(self.targets) == 0:
                    self.targets.append(pdm_target)
                else:
                    for i, present_pdm_target in enumerate(self.targets):
                        if (
                            present_pdm_target.target_id
                            == pdm_target.target_id
                        ):
                            self.targets[i] = pdm_target
                            break
                    else:
                        self.targets.append(pdm_target)

    def get_target_spec(self, target_id: str | None = None):
        """
        Get the target spec
        :param target_id: target id
        :return: TargetSpec object
        """
        if target_id is not None:
            return self.target_specs[target_id]
        return list(self.target_specs.values())[0]

    @property
    def next_target_id(self) -> str:
        """
        Get the next target id
        :return: The next target id
        """
        return list(self.target_specs.keys())[0]

DEFAULT_TARGET_SPECS_SB = {
    "Polaris Australis": TargetSpec(
        target_sb_detail={
            "co_ordinate_type": "Equatorial",
            "ra": "21:08:47.92 degrees",
            "dec": "-88:57:22.9 degrees",
            "reference_frame": "ICRS",
            "unit": ("hourangle", "deg"),
            "pointing_pattern_type": {
                "single_pointing_parameters": SinglePointParameters(
                    offset_x_arcsec=0.0, offset_y_arcsec=0.0
                ),
                "raster_parameters": RasterParameters(
                    row_length_arcsec=0.0,
                    row_offset_arcsec=0.0,
                    n_rows=1,
                    pa=0.0,
                    unidirectional=False,
                ),
                "star_raster_parameters": StarRasterParameters(
                    row_length_arcsec=0.0,
                    n_rows=1,
                    row_offset_angle=0.0,
                    unidirectional=False,
                ),
                "five_point_parameters": FivePointParameters(
                    offset_arcsec=0.0
                ),
                "cross_scan_parameters": CrossScanParameters(
                    offset_arcsec=0.0
                ),
                "active_pointing_pattern_type": "single_pointing_parameters",
            },
        },
        scan_type="Polaris Australis",
        band=ReceiverBand.BAND_2,
        channelisation="vis_channels",
        polarisation="all",
        processing="test-receive-addresses",
        dishes="two",
        target=None,
    ),
    ".default": TargetSpec(
        target_sb_detail={
            "co_ordinate_type": "Equatorial",
            "ra": "21:08:47.92 degrees",
            "dec": "-88:57:22.9 degrees",
            "reference_frame": "ICRS",
            "unit": ("hourangle", "deg"),
            "pointing_pattern_type": {
                "single_pointing_parameters": SinglePointParameters(
                    offset_x_arcsec=0.0, offset_y_arcsec=0.0
                ),
                "raster_parameters": RasterParameters(
                    row_length_arcsec=0.0,
                    row_offset_arcsec=0.0,
                    n_rows=1,
                    pa=0.0,
                    unidirectional=False,
                ),
                "star_raster_parameters": StarRasterParameters(
                    row_length_arcsec=0.0,
                    n_rows=1,
                    row_offset_angle=0.0,
                    unidirectional=False,
                ),
                "five_point_parameters": FivePointParameters(
                    offset_arcsec=0.0
                ),
                "cross_scan_parameters": CrossScanParameters(
                    offset_arcsec=0.0
                ),
                "active_pointing_pattern_type": "single_pointing_parameters",
            },
        },
        scan_type=".default",
        band=ReceiverBand.BAND_2,
        channelisation="vis_channels",
        polarisation="all",
        processing="test-receive-addresses",
        dishes="two",
        target=None,
    ),
}


