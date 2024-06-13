"""Test target specifications."""

import json

from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_pdm.entities.sdp import BeamMapping
from ska_tmc_cdm.messages.central_node.sdp import Channel
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand
from ska_tmc_cdm.schemas.central_node.assign_resources import AssignResourcesRequestSchema
from ska_tmc_cdm.schemas.subarray_node.configure.core import ConfigureRequestSchema

from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec

# pylint: disable=E1101


def test_validate_target_spec_add_configuration_for_mid_sb():
    """
    Validates Target Spec AddConfiguration for Mid Non SB
    """

    observation = ObservationSB()
    observation._channel_configurations = {}  # pylint: disable=W0212
    observation.eb_id = "eb-miditf-20240415-00006"
    target_specs = DEFAULT_TARGET_SPECS

    channel_configuration = DEFAULT_CHANNEL_CONFIGURATION

    observation.add_target_specs(target_specs)
    for target_id, target in target_specs.items():
        observation.add_scan_type_configuration(
            target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )
        observation.add_channel_configuration(target.channelisation, channel_configuration)

    pdm_allocation = observation.generate_pdm_object_for_sbd_save(target_specs)
    pdm_allocation.sbd_id = "sbd-miditf-20240415-00006"
    obsconfig_assign_resource_configuration_object = observation.generate_allocate_config_sb(
        pdm_allocation
    ).as_object

    obsconfig_assign_resource_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )

    obsconfig_assign_resource_dict = json.loads(obsconfig_assign_resource_json)

    obsconfig_configure_resource_object = observation.generate_scan_config_sb(
        pdm_allocation, "flux calibrator"
    ).as_object
    obsconfig_configure_resource_json = ConfigureRequestSchema().dumps(
        obsconfig_configure_resource_object
    )
    obsconfig_configure_resource_dict = json.loads(obsconfig_configure_resource_json)

    assert any(
        channel["channels_id"] == "vis_channels9"
        for channel in obsconfig_assign_resource_dict["sdp"]["execution_block"]["channels"]
    )

    assert any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in obsconfig_assign_resource_dict["sdp"]["execution_block"]["scan_types"]
    )

    assert obsconfig_configure_resource_dict["sdp"]["scan_type"] == "flux calibrator"


def test_validate_target_spec_remove_configuration_for_mid_sb():
    """
    Validates Target Spec Remove Configuration for Mid SB
    """

    observation = ObservationSB()
    observation.target_specs = {}
    observation._channel_configurations = {}  # pylint: disable=W0212
    observation.eb_id = "eb-miditf-20240415-00006"

    target_specs = DEFAULT_TARGET_SPECS

    # User can update freq_min and freq_max based on ReceiverBand
    channel_configuration = DEFAULT_CHANNEL_CONFIGURATION
    for value in target_specs.values():
        observation.add_channel_configuration(value.channelisation, channel_configuration)

    observation.add_target_specs(target_specs)

    for target_id in target_specs:
        observation.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )

    pdm_allocation = observation.generate_pdm_object_for_sbd_save(target_specs)
    pdm_allocation.sbd_id = "sbd-miditf-20240415-00006"
    obsconfig_assign_resource_configuration_object = observation.generate_allocate_config_sb(
        pdm_allocation
    ).as_object
    obsconfig_assign_resource_configuration_object.sdp_config.execution_block.channels = [
        channel
        for channel in
        obsconfig_assign_resource_configuration_object.sdp_config.execution_block.channels
        if channel.channels_id != "vis_channels6"
    ]
    obsconfig_assign_resource_configuration_object.sdp_config.execution_block.scan_types = [
        scan_type
        for scan_type in
        obsconfig_assign_resource_configuration_object.sdp_config.execution_block.scan_types
        if scan_type.scan_type_id != "flux calibrator"
    ]

    obsconfig_assign_resource_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )

    obsconfig_assign_resource_dict = json.loads(obsconfig_assign_resource_json)

    obsconfig_configure_resource_object = observation.generate_scan_config_sb(
        pdm_allocation, "flux calibrator"
    ).as_object
    obsconfig_configure_resource_object.sdp.scan_type = ""
    obsconfig_configure_resource_json = ConfigureRequestSchema().dumps(
        obsconfig_configure_resource_object
    )
    obsconfig_configure_resource_dict = json.loads(obsconfig_configure_resource_json)

    assert not any(
        channel["channels_id"] == "vis_channels6"
        for channel in obsconfig_assign_resource_dict["sdp"]["execution_block"]["channels"]
    )

    assert not any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in obsconfig_assign_resource_dict["sdp"]["execution_block"]["scan_types"]
    )

    assert not obsconfig_configure_resource_dict["sdp"]["scan_type"] == "flux calibrator"


def test_validate_target_spec_configuration_for_mid_sb():
    """
    Validates Target Spec Configuration for Mid Non SB
    """

    observation = ObservationSB()
    observation.target_specs = {}
    observation.eb_id = "eb-miditf-20240415-00006"
    observation._channel_configurations = {}  # pylint: disable=W0212

    for value in DEFAULT_TARGET_SPECS.values():
        observation.add_channel_configuration(value.channelisation, DEFAULT_CHANNEL_CONFIGURATION)

    observation.add_target_specs(DEFAULT_TARGET_SPECS)

    for target_id in DEFAULT_TARGET_SPECS:
        observation.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )
    scan_sequence = ["flux calibrator", "M87"]
    observation.add_scan_sequence(scan_sequence)

    pdm_allocation = observation.generate_pdm_object_for_sbd_save(DEFAULT_TARGET_SPECS)
    pdm_allocation.sbd_id = "sbd-miditf-20240415-00006"
    obsconfig_assign_resource_configuration_object = observation.generate_allocate_config_sb(
        pdm_allocation
    ).as_object

    obsconfig_assign_resource_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )

    obsconfig_assign_resource_dict = json.loads(obsconfig_assign_resource_json)

    obsconfig_configure_resource_object = observation.generate_scan_config_sb(
        pdm_allocation, "flux calibrator"
    ).as_object

    obsconfig_configure_resource_json = ConfigureRequestSchema().dumps(
        obsconfig_configure_resource_object
    )
    obsconfig_configure_resource_dict = json.loads(obsconfig_configure_resource_json)

    assert any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in obsconfig_assign_resource_dict["sdp"]["execution_block"]["scan_types"]
    )

    assert obsconfig_configure_resource_dict["sdp"]["scan_type"] == "flux calibrator"


DEFAULT_CHANNEL_CONFIGURATION = [
    Channel(
        spectral_window_id="fsp_1_channels",
        count=14880,
        start=0,
        stride=2,
        freq_min=0.35e9,
        freq_max=0.368e9,
        link_map=[[0, 0], [200, 1], [744, 2], [944, 3]],
    )
]

DEFAULT_TARGET_SPECS = {
    "flux calibrator": TargetSpec(
        target_sb_detail={
            "co_ordinate_type": "Equatorial",
            "ra": "19:24:51.05 degrees",
            "dec": "-29:14:30.12 degrees",
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
                "five_point_parameters": FivePointParameters(offset_arcsec=0.0),
                "cross_scan_parameters": CrossScanParameters(offset_arcsec=0.0),
                "active_pointing_pattern_type": "single_pointing_parameters",
            },
        },
        scan_type="flux calibrator",
        band=ReceiverBand.BAND_2,
        channelisation="vis_channels9",
        polarisation="all",
        processing="test-receive-addresses",
        dish_ids=["SKA001", "SKA036"],
        target=None,
    ),
    "M87": TargetSpec(
        target_sb_detail={
            "co_ordinate_type": "Equatorial",
            "ra": "19:24:51.05 degrees",
            "dec": "-29:14:30.12 degrees",
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
                "five_point_parameters": FivePointParameters(offset_arcsec=0.0),
                "cross_scan_parameters": CrossScanParameters(offset_arcsec=0.0),
                "active_pointing_pattern_type": "single_pointing_parameters",
            },
        },
        scan_type="M87",
        band=ReceiverBand.BAND_2,
        channelisation="vis_channels10",
        polarisation="all",
        processing="test-receive-addresses",
        dish_ids=["SKA001", "SKA036"],
        target=None,
    ),
}
