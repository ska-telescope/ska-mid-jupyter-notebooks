"""Test the configuration of observations."""

from assertpy import assert_that
from ska_tmc_cdm.messages.central_node.sdp import EBScanTypeBeam

from ska_mid_jupyter_notebooks.obsconfig.channelisation import Channelisation
from ska_mid_jupyter_notebooks.obsconfig.sdp_config import ScanTypes
from ska_mid_jupyter_notebooks.obsconfig.target_spec import get_default_target_specs_sb

# mypy: disable-error-code="import-untyped"


def test_channelisation() -> None:
    """
    Test to validate channelisation configuration.
    """
    dish_ids = ["SKA001", "SKA036"]
    channelisation = Channelisation(target_specs=get_default_target_specs_sb(dish_ids))
    channel_configurations = channelisation.channel_configurations
    assert_that(channel_configurations).is_type_of(list)
    target_spec_channels = channelisation.target_spec_channels
    assert_that(target_spec_channels).is_type_of(set)
    default_channels = channelisation.channels
    assert_that(default_channels).is_not_empty()
    default_channel = default_channels[0]
    assert_that(default_channel).is_true()
    dummy_windows = default_channel.spectral_windows
    channelisation.add_channel_configuration("dummy", dummy_windows)
    assert_that(channelisation.channel_configurations).contains("dummy")
    assert_that(channelisation.get_channel_configuration("dummy").spectral_windows).is_equal_to(
        dummy_windows
    )


# pylint: disable-next=too-many-locals
def test_scan_types() -> None:
    """
    Test to validate ScanTypes configuration
    """
    dish_ids = ["SKA001", "SKA036"]
    scan_type_config = ScanTypes(target_specs=get_default_target_specs_sb(dish_ids))
    scan_type_configurations = scan_type_config.scan_type_configurations
    assert_that(scan_type_configurations).is_type_of(list)
    target_spec_scan_types = scan_type_config.target_spec_scan_types
    assert_that(target_spec_scan_types).is_type_of(set)
    default_scan_types = scan_type_config.scan_types
    assert_that(default_scan_types).is_not_empty()
    default_scan_type = default_scan_types[0]
    assert_that(default_scan_type).is_true()
    default_beams = scan_type_config.beams
    assert_that(default_beams).is_not_empty()
    default_beam = default_beams[0]
    assert_that(default_beam).is_true()
    target_spec_beams = scan_type_config.target_spec_beams
    assert_that(target_spec_beams).is_type_of(set)
    scan_type_config.add_scan_type_configuration(
        "dummy", {default_beam.beam_id: default_scan_type.beams}
    )
    assert_that(scan_type_config.scan_type_configurations).contains("dummy")
    beam_grouping_id = target_spec_beams.pop()
    beam_configuration = scan_type_config.get_beam_configurations(beam_grouping_id)
    new_beam_types: dict[str, EBScanTypeBeam] = {}
    new_beam_types_keys = [f"{key}_dummy" for key in beam_configuration.types.keys()]
    new_beam_type_values = list(beam_configuration.types.values())
    new_beam_types[new_beam_types_keys[0]] = new_beam_type_values[0]
    new_beam_types[new_beam_types_keys[1]] = new_beam_type_values[1]
    scan_type_config.add_beam_types(beam_grouping_id, new_beam_types)
    required_entry1_key, required_entry1_val = list(new_beam_types.items())[0]
    required_entry2_key, required_entry2_val = list(new_beam_types.items())[1]
    required_entry1 = {required_entry1_key: required_entry1_val}
    required_entry2 = {required_entry2_key: required_entry2_val}
    assert_that(scan_type_config.get_beam_configurations(beam_grouping_id).types).contains_entry(
        required_entry1
    )
    assert_that(scan_type_config.get_beam_configurations(beam_grouping_id).types).contains_entry(
        required_entry2
    )
    new_config_name = f"{beam_configuration.id}dummy"
    scan_type_config.add_beam_configuration(new_config_name, "dummy")
    assert_that(scan_type_config.get_beam_configurations(new_config_name)).is_true()
    new_config_name = f"{beam_configuration.id}dummy2"
    scan_type_config.add_beam_configuration(new_config_name, "dummy", beam_types=new_beam_types)
