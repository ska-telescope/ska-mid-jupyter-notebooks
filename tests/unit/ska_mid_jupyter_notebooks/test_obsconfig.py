from assertpy import assert_that

from ska_mid_jupyter_notebooks.obsconfig import Channelization, ScanTypes, types


def test_channelisation():
    """
    Test to validate channelisation configuration
    """
    channelisation = Channelization(sb_driven=False)
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


def test_scan_types():
    """
    Test to validate ScanTypes configuration
    """
    scan_type_config = ScanTypes(sb_driven=False)
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
    scan_type_config.add_scan_type_configuration(
        "dummy2",
        (beam_grouping_id, list(beam_configuration.types.keys())[0]),
    )
    assert_that(scan_type_config.scan_type_configurations).contains("dummy2")
    scan_type_config.add_scan_type_configuration(
        "dummy3",
        [
            (beam_grouping_id, list(beam_configuration.types.keys())[0]),
            (beam_grouping_id, list(beam_configuration.types.keys())[1]),
        ],
    )
    assert_that(scan_type_config.scan_type_configurations).contains("dummy3")
    new_beam_types: dict[str, types.EBScanTypeBeam] = dict()
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
