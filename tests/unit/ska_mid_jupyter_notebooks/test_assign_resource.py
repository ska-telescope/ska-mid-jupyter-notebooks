import json
import os
from collections import OrderedDict

import pytest
from deepdiff import DeepDiff
from ska_tmc_cdm.messages.central_node.sdp import Channel
from ska_tmc_cdm.schemas.central_node.assign_resources import (
    AssignResourcesRequestSchema,
)
from ska_tmc_cdm.schemas.central_node.csp import CSPConfigurationSchema
from ska_tmc_cdm.schemas.central_node.mccs import MCCSAllocateSchema
from ska_tmc_cdm.schemas.central_node.sdp import SDPConfigurationSchema
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand, Target

from ska_mid_jupyter_notebooks.obsconfig.config import (  # noqa : E402
    ObservationSB,
)
from ska_mid_jupyter_notebooks.obsconfig.target_spec import (
    TargetSpec,
)

# pylint: disable=E1101

VALID_ASSIGN_RESOURCE_PI17_LOW_JSON = """{
  "interface": "https://schema.skao.int/ska-low-tmc-assignresources/3.0",
  "transaction_id": "txn-....-00001",
  "subarray_id": 1,
  "mccs": {
    "subarray_beam_ids": [
      1
    ],
    "station_ids": [
      [
        1,
        2
      ]
    ],
    "channel_blocks": [
      3
    ]
  },
  "sdp": {
    "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
    "resources": {
      "receptors": [
        "SKA001",
        "SKA036"
      ]
    },
    "execution_block": {
      "context": {},
      "max_length": 3600.0,
      "beams": [
        {
          "beam_id": "vis0",
          "function": "visibilities"
        }
      ],
      "scan_types": [
        {
          "scan_type_id": "Science Target",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        },
        {
          "scan_type_id": "bandpass calibrator",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        },
        {
          "scan_type_id": "target:a",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        },
        {
          "scan_type_id": "Complex Gain Calibrator",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        },
        {
          "scan_type_id": ".default",
          "beams": {
            "vis0": {
              "channels_id": "vis_channels",
              "polarisations_id": "all"
            }
          }
        },
        {
          "scan_type_id": "flux calibrator",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        }
      ],
      "channels": [
        {
          "channels_id": "vis_channels1",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        },
        {
          "channels_id": "vis_channels2",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        },
        {
          "channels_id": "vis_channels3",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        },
        {
          "channels_id": "vis_channels4",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        },
        {
          "channels_id": "vis_channels",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        }
      ],
      "polarisations": [
        {
          "polarisations_id": "all",
          "corr_type": [
            "XX",
            "XY",
            "YX",
            "YY"
          ]
        }
      ],
      "fields": [
        {
          "field_id": "field_a",
          "phase_dir": {
            "ra": [
              123.0
            ],
            "dec": [
              -60.0
            ],
            "reference_time": "...",
            "reference_frame": "ICRF3"
          },
          "pointing_fqdn": "..."
        }
      ]
    },
    "processing_blocks": [
      {
        "pb_id": "pb-test-20220916-00000",
        "script": {
          "kind": "realtime",
          "name": "test-receive-addresses",
          "version": "0.7.1"
        },
        "sbi_ids": [
          "sbi-test-20220916-00000"
        ],
        "parameters": {}
      }
    ]
  },
  "csp": {
    "interface": "https://schema.skao.int/ska-low-csp-assignresources/2.0",
    "common": {
      "subarray_id": 1
    },
    "lowcbf": {
      "resources": [
        {
          "device": "fsp_01",
          "shared": true,
          "fw_image": "pst",
          "fw_mode": "unused"
        },
        {
          "device": "p4_01",
          "shared": true,
          "fw_image": "p4.bin",
          "fw_mode": "p4"
        }
      ]
    }
  }
}
"""

VALID_SDP_BLOCK_PI17_LOW_JSON = """{
    "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
    "resources": {
      "receptors": [
        "SKA001",
        "SKA036"
      ]
    },
    "execution_block": {
      "eb_id": "eb-test-20220916-00000",
      "context": {

      },
      "max_length": 3600.0,
      "beams": [
        {
          "beam_id": "vis0",
          "function": "visibilities"
        }
      ],
      "scan_types": [
        {
          "scan_type_id": "target:a",
          "derive_from": ".default",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          }
        },
        {
          "scan_type_id": ".default",
          "beams": {
            "vis0": {
              "channels_id": "vis_channels",
              "polarisations_id": "all"
            }
          }
        }
      ],
      "channels": [
        {
          "channels_id": "vis_channels",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        }
      ],
      "polarisations": [
        {
          "polarisations_id": "all",
          "corr_type": [
            "XX",
            "XY",
            "YX",
            "YY"
          ]
        }
      ],
      "fields": [
        {
          "field_id": "field_a",
          "phase_dir": {
            "ra": [
              123.0
            ],
            "dec": [
              -60.0
            ],
            "reference_time": "...",
            "reference_frame": "ICRF3"
          },
          "pointing_fqdn": "..."
        }
      ]
    },
    "processing_blocks": [
      {
        "pb_id": "pb-test-20220916-00000",
        "script": {
          "kind": "realtime",
          "name": "test-receive-addresses",
          "version": "0.7.1"
        },
        "sbi_ids": [
          "sbi-test-20220916-00000"
        ],
        "parameters": {

        }
      }
    ]
  }"""

VALID_MCCS_BLOCK_PI17_LOW_JSON = """{
    "subarray_beam_ids": [
      1
    ],
    "station_ids": [
      [
        1,
        2
      ]
    ],
    "channel_blocks": [
      3
    ]
  }"""

VALID_CSP_BLOCK_PI17_LOW_JSON = """{
    "interface": "https://schema.skao.int/ska-low-csp-assignresources/2.0",
    "common": {
      "subarray_id": 1
    },
    "lowcbf": {
      "resources": [
        {
          "device": "fsp_01",
          "shared": true,
          "fw_image": "pst",
          "fw_mode": "unused"
        },
        {
          "device": "p4_01",
          "shared": true,
          "fw_image": "p4.bin",
          "fw_mode": "p4"
        }
      ]
    }
  }"""

VALID_ASSIGN_RESOURCE_PI16_MID_JSON = """{
  "interface": "https://schema.skao.int/ska-tmc-assignresources/2.1",
  "subarray_id": 1,
  "dish": {
    "receptor_ids": [
      "SKA001",
      "SKA036"
    ]
  },
  "sdp": {
    "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
    "execution_block": {
      "eb_id": "eb-mvp01-20231218-50360",
      "max_length": 3600,
      "context": {},
      "beams": [
        {
          "beam_id": "vis0",
          "function": "visibilities"
        }
      ],
      "channels": [
        {
          "channels_id": "vis_channels",
          "spectral_windows": [
            {
              "count": 14880,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000,
              "freq_max": 368000000,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ],
              "spectral_window_id": "fsp_1_channels"
            }
          ]
        },
        {
          "channels_id": "vis_channels20",
          "spectral_windows": [
            {
              "count": 4,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000,
              "freq_max": 368000000,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ],
              "spectral_window_id": "fsp_1_channels"
            }
          ]
        }
      ],
      "polarisations": [
        {
          "polarisations_id": "all",
          "corr_type": [
            "XX",
            "XY",
            "YX",
            "YY"
          ]
        }
      ],
      "scan_types": [
        {
          "scan_type_id": "flux calibrator",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        },
        {
          "scan_type_id": "target:a",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          },
          "derive_from": ".default"
        },
        {
          "scan_type_id": ".default",
          "beams": {
            "vis0": {
              "channels_id": "vis_channels",
              "polarisations_id": "all"
            }
          }
        }
      ],
      "fields": [
        {
          "field_id": "field_a",
          "phase_dir": {
            "ra": [
              123
            ],
            "dec": [
              -60
            ],
            "reference_time": "...",
            "reference_frame": "ICRF3"
          },
          "pointing_fqdn": "..."
        }
      ]
    },
    "processing_blocks": [
      {
        "pb_id": "pb-mvp01-20231218-50360",
        "parameters": {},
        "sbi_ids": [
          "sbi-mvp01-20231218-50360"
        ],
        "script": {
          "kind": "realtime",
          "name": "test-receive-addresses",
          "version": "0.7.1"
        }
      }
    ],
    "resources": {
      "receptors": [
        "SKA001",
        "SKA036"
      ]
    }
  }
}"""

VALID_SDP_BLOCK_PI16_MID_JSON = """{
    "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
    "resources": {
      "receptors": [
        "SKA001",
        "SKA036"
      ]
    },
    "execution_block": {
      "eb_id": "eb-test-20220916-00000",
      "context": {

      },
      "max_length": 3600.0,
      "beams": [
        {
          "beam_id": "vis0",
          "function": "visibilities"
        }
      ],
      "scan_types": [
        {
          "scan_type_id": "target:a",
          "derive_from": ".default",
          "beams": {
            "vis0": {
              "field_id": "field_a"
            }
          }
        },
        {
          "scan_type_id": ".default",
          "beams": {
            "vis0": {
              "channels_id": "vis_channels",
              "polarisations_id": "all"
            }
          }
        }
      ],
      "channels": [
        {
          "channels_id": "vis_channels",
          "spectral_windows": [
            {
              "spectral_window_id": "fsp_1_channels",
              "count": 14880,
              "start": 0,
              "stride": 2,
              "freq_min": 350000000.0,
              "freq_max": 368000000.0,
              "link_map": [
                [
                  0,
                  0
                ],
                [
                  200,
                  1
                ],
                [
                  744,
                  2
                ],
                [
                  944,
                  3
                ]
              ]
            }
          ]
        }
      ],
      "polarisations": [
        {
          "polarisations_id": "all",
          "corr_type": [
            "XX",
            "XY",
            "YX",
            "YY"
          ]
        }
      ],
      "fields": [
        {
          "field_id": "field_a",
          "phase_dir": {
            "ra": [
              123.0
            ],
            "dec": [
              -60.0
            ],
            "reference_time": "...",
            "reference_frame": "ICRF3"
          },
          "pointing_fqdn": "..."
        }
      ]
    },
    "processing_blocks": [
      {
        "pb_id": "pb-test-20220916-00000",
        "script": {
          "kind": "realtime",
          "name": "test-receive-addresses",
          "version": "0.7.1"
        },
        "sbi_ids": [
          "sbi-test-20220916-00000"
        ],
        "parameters": {

        }
      }
    ]
  }"""


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_csp_configuration_object_using_observation_class():
    """
    Validates that CSP config object returned using ObsConfig Observation class
    """

    obsconfig_csp_configuration_object = (
        Observation().generate_csp_assign_resources_config_low().as_object
    )
    valid_csp_configuration_object = CSPConfigurationSchema().loads(
        VALID_CSP_BLOCK_PI17_LOW_JSON
    )

    assert obsconfig_csp_configuration_object == valid_csp_configuration_object


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_sdp_configuration_object_using_observation_class():
    """
    Validates SDP config object returned using ObsConfig Observation class
    """

    obsconfig_sdp_configuration_object = (
        Observation().generate_sdp_assign_resources_config().as_object
    )
    valid_sdp_configuration_object = SDPConfigurationSchema().loads(
        VALID_SDP_BLOCK_PI17_LOW_JSON
    )

    valid_sdp_configuration_object.processing_blocks[
        0
    ].pb_id = obsconfig_sdp_configuration_object.processing_blocks[0].pb_id
    valid_sdp_configuration_object.execution_block.eb_id = (
        obsconfig_sdp_configuration_object.execution_block.eb_id
    )
    valid_sdp_configuration_object.processing_blocks[
        0
    ].sbi_ids = obsconfig_sdp_configuration_object.processing_blocks[0].sbi_ids

    sdp_obsconfig_json = SDPConfigurationSchema().dumps(
        obsconfig_sdp_configuration_object
    )
    sdp_valid_json = SDPConfigurationSchema().dumps(
        valid_sdp_configuration_object
    )

    sdp_obsconfig_dict = json.loads(sdp_obsconfig_json)
    sdp_valid_dict = json.loads(sdp_valid_json)

    diff = DeepDiff(sdp_obsconfig_dict, sdp_valid_dict, ignore_order=True)
    print(diff)
    assert not diff, f"Dictionaries are not equal:{diff}"


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_validate_sdp_configuration_object_using_mid_observation_class():
    """
    Validates SDP config object returned using ObsConfig Observation class for Mid
    """

    obsconfig_sdp_configuration_object = (
        Observation().generate_sdp_assign_resources_config().as_object
    )
    valid_sdp_configuration_object = SDPConfigurationSchema().loads(
        VALID_SDP_BLOCK_PI16_MID_JSON
    )

    valid_sdp_configuration_object.processing_blocks[
        0
    ].pb_id = obsconfig_sdp_configuration_object.processing_blocks[0].pb_id
    valid_sdp_configuration_object.execution_block.eb_id = (
        obsconfig_sdp_configuration_object.execution_block.eb_id
    )
    valid_sdp_configuration_object.processing_blocks[
        0
    ].sbi_ids = obsconfig_sdp_configuration_object.processing_blocks[0].sbi_ids

    sdp_obsconfig_json = SDPConfigurationSchema().dumps(
        obsconfig_sdp_configuration_object
    )
    sdp_valid_json = SDPConfigurationSchema().dumps(
        valid_sdp_configuration_object
    )

    sdp_obsconfig_dict = json.loads(sdp_obsconfig_json)
    sdp_valid_dict = json.loads(sdp_valid_json)

    diff = DeepDiff(sdp_obsconfig_dict, sdp_valid_dict, ignore_order=True)
    assert not diff, f"Dictionaries are not equal:{diff}"


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_mccs_configuration_object_using_observation_class():
    """
    Validates MCCS config object returned using ObsConfig Observation class
    """

    obsconfig_mccs_configuration_object = (
        Observation().generate_mccs_assign_resources_config().as_object
    )
    valid_mccs_configuration_object = MCCSAllocateSchema().loads(
        VALID_MCCS_BLOCK_PI17_LOW_JSON
    )

    assert (
        obsconfig_mccs_configuration_object == valid_mccs_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_assign_resource_configuration_object_using_observation_class():
    """
    Validates Assign Resources config object returned using ObsConfig Observation class
    """

    observation = Observation()
    target_specs = OrderedDict(
        {
            "bandpass calibrator": TargetSpec(
                target=SubarrayBeamTarget(
                    reference_frame="HORIeZON",
                    target_name="DriftScan",
                    az=270.0,
                    el=60.0,
                ),
                scan_type="bandpass calibrator",
                band=ReceiverBand.BAND_1,
                channelisation="vis_channels1",
                polarisation="all",
                field="field_a",
                processing="test-receive-addresses",
                dishes="two",
                scan_duration=10,
            ),
            "flux calibrator": TargetSpec(
                target=SubarrayBeamTarget(
                    reference_frame="HORIeZON",
                    target_name="DriftScan",
                    az=270.0,
                    el=60.0,
                ),
                scan_type="flux calibrator",
                band=ReceiverBand.BAND_2,
                channelisation="vis_channels2",
                polarisation="all",
                field="field_a",
                processing="test-receive-addresses",
                dishes="two",
                scan_duration=5,
            ),
            "Complex Gain Calibrator": TargetSpec(
                target=SubarrayBeamTarget(
                    reference_frame="HORIeZON",
                    target_name="DriftScan",
                    az=270.0,
                    el=60.0,
                ),
                scan_type="Complex Gain Calibrator",
                band=ReceiverBand.BAND_1,
                channelisation="vis_channels3",
                polarisation="all",
                field="field_a",
                processing="test-receive-addresses",
                dishes="two",
                scan_duration=2,
            ),
            "Science Target": TargetSpec(
                target=SubarrayBeamTarget(
                    reference_frame="HORIeZON",
                    target_name="DriftScan",
                    az=270.0,
                    el=60.0,
                ),
                scan_type="Science Target",
                band=ReceiverBand.BAND_1,
                channelisation="vis_channels4",
                polarisation="all",
                field="field_a",
                processing="test-receive-addresses",
                dishes="two",
                scan_duration=15,
            ),
        }
    )

    # User can update freq_min and freq_max based on ReceiverBand
    channel_configuration = [
        Channel(
            spectral_window_id="fsp_1_channels",
            count=4,
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

    valid_assign_resource_configuration_object = (
        AssignResourcesRequestSchema().loads(
            VALID_ASSIGN_RESOURCE_PI17_LOW_JSON
        )
    )

    valid_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].pb_id = obsconfig_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].pb_id

    valid_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].sbi_ids = obsconfig_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].sbi_ids

    obsconfig_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )
    valid_json = AssignResourcesRequestSchema().dumps(
        valid_assign_resource_configuration_object
    )

    obsconfig_dict = json.loads(obsconfig_json)
    valid_dict = json.loads(valid_json)

    diff = DeepDiff(obsconfig_dict, valid_dict, ignore_order=True)
    assert not diff, f"Dictionaries are not equal:{diff}"


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_validate_assign_resource_configuration_object_using_mid_observation_class():
    """
    Validates Assign Resources config object returned using ObsConfig Observation class for Mid
    """

    observation = Observation()
    target_specs = OrderedDict(
        {
            "flux calibrator": TargetSpec(
                target=Target("19:24:51.05 degrees", "-29:14:30.12 degrees"),
                scan_type="flux calibrator",
                band=ReceiverBand.BAND_2,
                channelisation="vis_channels20",
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
            count=4,
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
        observation.generate_assign_resources_config().as_object
    )

    valid_assign_resource_configuration_object = (
        AssignResourcesRequestSchema().loads(
            VALID_ASSIGN_RESOURCE_PI16_MID_JSON
        )
    )

    valid_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].pb_id = obsconfig_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].pb_id

    valid_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].sbi_ids = obsconfig_assign_resource_configuration_object.sdp_config.processing_blocks[
        0
    ].sbi_ids
    valid_assign_resource_configuration_object.sdp_config.execution_block.eb_id = (
        obsconfig_assign_resource_configuration_object.sdp_config.execution_block.eb_id
    )
    obsconfig_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_object
    )
    valid_json = AssignResourcesRequestSchema().dumps(
        valid_assign_resource_configuration_object
    )

    obsconfig_dict = json.loads(obsconfig_json)
    valid_dict = json.loads(valid_json)

    diff = DeepDiff(obsconfig_dict, valid_dict, ignore_order=True)
    assert not diff, f"Dictionaries are not equal:{diff}"
