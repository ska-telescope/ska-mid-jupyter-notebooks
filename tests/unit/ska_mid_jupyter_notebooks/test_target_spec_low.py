import json
import os
from collections import OrderedDict

import pytest
from ska_tmc_cdm.messages.central_node.sdp import Channel
from ska_tmc_cdm.schemas.central_node.assign_resources import (
    AssignResourcesRequestSchema,
)
from ska_tmc_cdm.schemas.subarray_node.configure.core import (
    ConfigureRequestSchema,
)

from ska_jupyter_scripting.obsconfig.config import (  # noqa : E402
    Observation,
    ObservationSB,
)
from ska_jupyter_scripting.obsconfig.types import (
    ReceiverBand,
    SubarrayBeamTarget,
    Target,
    TargetSpec,
)


# pylint: disable=E1101
@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_target_spec_add_configuration_for_low_non_sb():
    """
    Validates Target Spec Add Configuration for Low Non SB
    """

    observation = Observation()
    observation._channel_configurations = {}  # pylint: disable=W0212
    target_specs = OrderedDict(
        {
            "flux calibrator": TargetSpec(
                target=SubarrayBeamTarget(
                    reference_frame="HORIZON",
                    target_name="DriftScan",
                    az=270.0,
                    el=60.0,
                ),
                scan_type="flux calibrator",
                band=ReceiverBand.BAND_2,
                channelisation="vis_channels6",
                polarisation="all",
                field="field_a",
                processing="test-receive-addresses",
                dishes="two",
                scan_duration=5,
            ),
        }
    )

    # User can update freq_min and freq_max based on ReceiverBand
    channel_configuration = [
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

    if target_specs and len(target_specs) > 0:
        observation.add_target_specs(target_specs)
        for target_id, target in target_specs.items():
            observation.add_scan_type_configuration(
                target_id,
                {"vis0": {"vis0": {"field_id": "field_a"}}},
                ".default",
            )
            observation.add_channel_configuration(
                target.channelisation, channel_configuration
            )

    obsconfig_assign_resource_configuration_object = (
        observation.generate_assign_resources_config_low().as_object
    )

    obsconfig_assign_resource_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )

    obsconfig_assign_resource_dict = json.loads(obsconfig_assign_resource_json)

    obsconfig_configure_resource_object = observation.generate_scan_config_low(
        target_id="flux calibrator"
    ).as_object
    obsconfig_configure_resource_json = ConfigureRequestSchema().dumps(
        obsconfig_configure_resource_object
    )
    obsconfig_configure_resource_dict = json.loads(
        obsconfig_configure_resource_json
    )

    assert any(
        channel["channels_id"] == "vis_channels6"
        for channel in obsconfig_assign_resource_dict["sdp"][
            "execution_block"
        ]["channels"]
    )

    assert any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in obsconfig_assign_resource_dict["sdp"][
            "execution_block"
        ]["scan_types"]
    )

    assert (
        obsconfig_configure_resource_dict["sdp"]["scan_type"]
        == "flux calibrator"
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_target_spec_remove_configuration_for_low_non_sb():
    """
    Validates Target Spec RemoveConfiguration for Low Non SB
    """

    observation = Observation()
    observation._channel_configurations = {}  # pylint: disable=W0212
    target_specs = OrderedDict(
        {
            "flux calibrator": TargetSpec(
                target=SubarrayBeamTarget(
                    reference_frame="HORIZON",
                    target_name="DriftScan",
                    az=270.0,
                    el=60.0,
                ),
                scan_type="flux calibrator",
                band=ReceiverBand.BAND_2,
                channelisation="vis_channels6",
                polarisation="all",
                field="field_a",
                processing="test-receive-addresses",
                dishes="two",
                scan_duration=5,
            ),
        }
    )

    # User can update freq_min and freq_max based on ReceiverBand
    channel_configuration = [
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

    if target_specs and len(target_specs) > 0:
        observation.add_target_specs(target_specs)
        for target_id, target in target_specs.items():
            observation.add_scan_type_configuration(
                target_id,
                {"vis0": {"vis0": {"field_id": "field_a"}}},
                ".default",
            )
            observation.add_channel_configuration(
                target.channelisation, channel_configuration
            )

    obsconfig_assign_resource_configuration_object = (
        observation.generate_assign_resources_config_low().as_object
    )

    obsconfig_assign_resource_configuration_object.sdp_config.execution_block.channels = [
        channel
        for channel in obsconfig_assign_resource_configuration_object.sdp_config.execution_block.channels
        if channel.channels_id != "vis_channels6"
    ]
    obsconfig_assign_resource_configuration_object.sdp_config.execution_block.scan_types = [
        scan_type
        for scan_type in obsconfig_assign_resource_configuration_object.sdp_config.execution_block.scan_types
        if scan_type.scan_type_id != "flux calibrator"
    ]

    obsconfig_assign_resource_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )

    obsconfig_assign_resource_dict = json.loads(obsconfig_assign_resource_json)

    obsconfig_configure_resource_object = observation.generate_scan_config_low(
        target_id="flux calibrator"
    ).as_object
    obsconfig_configure_resource_object.sdp.scan_type = ""
    obsconfig_configure_resource_json = ConfigureRequestSchema().dumps(
        obsconfig_configure_resource_object
    )
    obsconfig_configure_resource_dict = json.loads(
        obsconfig_configure_resource_json
    )

    assert not any(
        channel["channels_id"] == "vis_channels6"
        for channel in obsconfig_assign_resource_dict["sdp"][
            "execution_block"
        ]["channels"]
    )

    assert not any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in obsconfig_assign_resource_dict["sdp"][
            "execution_block"
        ]["scan_types"]
    )

    assert (
        not obsconfig_configure_resource_dict["sdp"]["scan_type"]
        == "flux calibrator"
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_default_target_spec_configuration_for_low_non_sb():
    """
    Validates Default Target Spec Configuration for Low Non SB
    """
    observation = Observation()
    observation._channel_configurations = {}  # pylint: disable=W0212

    obsconfig_assign_resource_configuration_object = (
        observation.generate_assign_resources_config_low().as_object
    )

    obsconfig_assign_resource_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )

    obsconfig_assign_resource_dict = json.loads(obsconfig_assign_resource_json)

    obsconfig_configure_resource_object = (
        observation.generate_scan_config_low().as_object
    )

    obsconfig_configure_resource_json = ConfigureRequestSchema().dumps(
        obsconfig_configure_resource_object
    )
    obsconfig_configure_resource_dict = json.loads(
        obsconfig_configure_resource_json
    )

    assert any(
        scan_type["scan_type_id"] == "target:a"
        for scan_type in obsconfig_assign_resource_dict["sdp"][
            "execution_block"
        ]["scan_types"]
    )

    assert obsconfig_configure_resource_dict["sdp"]["scan_type"] == "target:a"
