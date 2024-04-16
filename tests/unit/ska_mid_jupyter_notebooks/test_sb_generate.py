import json
import os
from pprint import pprint

import pytest
from deepdiff import DeepDiff
from ska_oso_pdm.entities.common.sb_definition import SBDefinition
from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_pdm.entities.sdp import BeamMapping
from ska_oso_pdm.schemas import CODEC as pdm_CODEC
from ska_tmc_cdm.messages.central_node.sdp import Channel
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand
from ska_tmc_cdm.schemas.central_node.assign_resources import AssignResourcesRequestSchema

from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec

VALID_SB_MID_JSON = """{
  "sbd_id": "sbi-mvp01-20200325-00001",
  "interface": "https://schema.skao.int/ska-oso-pdm-sbd/0.1",
  "telescope": "ska_mid",
  "metadata": {
    "version": 1,
    "created_on": "2022-03-28T15:43:53.971548+00:00",
    "created_by": "test_user",
    "last_modified_on": "2022-03-28T15:43:53.971548+00:00",
    "last_modified_by": "test_user"
  },
  "activities": {
    "allocate": {
      "kind": "git",
      "function_args": {
        "init": {
          "args": [],
          "kwargs": {
            "subarray_id": 1
          }
        },
        "main": {
          "args": [],
          "kwargs": {}
        }
      },
      "path": "git://scripts/allocate_from_file_mid_sb.py",
      "repo": "https://gitlab.com/ska-telescope/oso/ska-oso-scripting.git",
      "branch": "nak-710-jupyter-scripts"
    },
    "observe": {
      "kind": "git",
      "function_args": {
        "init": {
          "args": [],
          "kwargs": {
            "subarray_id": 1
          }
        },
        "main": {
          "args": [],
          "kwargs": {}
        }
      },
      "path": "git://scripts/observe_mid_sb.py",
      "repo": "https://gitlab.com/ska-telescope/oso/ska-oso-scripting.git",
      "branch": "nak-710-jupyter-scripts"
    }
  },
  "scan_definitions": [
    {
      "scan_definition_id": "flux calibrator",
      "scan_duration": 10000,
      "dish_configuration": "dish config 123",
      "scan_type": "flux calibrator",
      "csp_configuration": "sbi-mvp01-20200325-00001-science_A",
      "target": "flux calibrator"
    },
    {
      "scan_definition_id": "M87",
      "scan_duration": 10000,
      "dish_configuration": "dish config 123",
      "scan_type": "M87",
      "csp_configuration": "sbi-mvp01-20200325-00001-science_A",
      "target": "M87"
    }
  ],
  "scan_sequence": [
    "flux calibrator"
  ],
  "sdp_configuration": {
    "execution_block": {
      "eb_id": "eb-mvp01-20231010-82511",
      "max_length": 3600.0,
      "context": {},
      "beams": [
        {
          "beam_id": "vis0",
          "function": "visibilities"
        }
      ],
      "scan_types": [
        {
          "scan_type_id": "M87",
          "derive_from": ".default",
          "beams": [
            {
              "beam_id": "vis0",
              "field_id": "M83"
            }
          ]
        },
        {
          "scan_type_id": ".default",
          "beams": [
            {
              "beam_id": "vis0",
              "channels_id": "vis_channels",
              "polarisations_id": "all"
            }
          ]
        },
        {
          "scan_type_id": "Polaris Australis",
          "derive_from": ".default",
          "beams": [
            {
              "beam_id": "vis0",
              "field_id": "Polaris Australis"
            }
          ]
        },
        {
          "scan_type_id": "flux calibrator",
          "derive_from": ".default",
          "beams": [
            {
              "beam_id": "vis0",
              "field_id": "M83"
            }
          ]
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
            "YY",
            "YX"
          ]
        }
      ]
    },
    "resources": {
      "receptors": [
        "SKA036",
        "SKA001"
      ]
    },
    "processing_blocks": [
      {
        "pb_id": "pb-mvp01-20231010-79879",
        "script": {
          "name": "test-receive-addresses",
          "kind": "realtime",
          "version": "0.7.1"
        },
        "sbi_ids": [
          "sbi-mvp01-20231010-79879"
        ],
        "parameters": {}
      }
    ]
  },
  "csp_configurations": [
    {
      "config_id": "sbi-mvp01-20200325-00001-science_A",
      "subarray": {
        "subarray_name": "dummy name"
      },
      "common": {
        "subarray_id": 1
      },
      "cbf": {
        "fsp": [
          {
            "fsp_id": 1,
            "function_mode": "CORR",
            "frequency_slice_id": 1,
            "zoom_factor": 0,
            "integration_factor": 10,
            "output_link_map": [
              [
                0,
                0
              ],
              [
                200,
                1
              ]
            ],
            "channel_offset": 0
          },
          {
            "fsp_id": 2,
            "function_mode": "CORR",
            "frequency_slice_id": 1,
            "zoom_factor": 0,
            "integration_factor": 10,
            "output_link_map": [
              [
                0,
                4
              ],
              [
                200,
                5
              ]
            ],
            "channel_offset": 744
          }
        ]
      }
    }
  ],
  "dish_configurations": [
    {
      "dish_configuration_id": "dish config 123",
      "receiver_band": "2"
    }
  ],
  "dish_allocations": {
    "receptor_ids": [
      "SKA036",
      "SKA001"
    ]
  },
  "targets": [
    {
      "target_id": "Polaris Australis",
      "pointing_pattern": {
        "active": "SinglePointParameters",
        "parameters": [
          {
            "offset_x_arcsec": 0.0,
            "offset_y_arcsec": 0.0,
            "kind": "SinglePointParameters"
          }
        ]
      },
      "reference_coordinate": {
        "kind": "equatorial",
        "ra": "21:08:47.92 degrees",
        "dec": "-88:57:22.9 degrees",
        "reference_frame": "ICRS",
        "unit": [
          "hourangle",
          "deg"
        ]
      }
    },
    {
      "target_id": ".default",
      "pointing_pattern": {
        "active": "SinglePointParameters",
        "parameters": [
          {
            "offset_x_arcsec": 0.0,
            "offset_y_arcsec": 0.0,
            "kind": "SinglePointParameters"
          }
        ]
      },
      "reference_coordinate": {
        "kind": "equatorial",
        "ra": "21:08:47.92 degrees",
        "dec": "-88:57:22.9 degrees",
        "reference_frame": "ICRS",
        "unit": [
          "hourangle",
          "deg"
        ]
      }
    },
    {
      "target_id": "flux calibrator",
      "pointing_pattern": {
        "active": "SinglePointParameters",
        "parameters": [
          {
            "offset_x_arcsec": 0.0,
            "offset_y_arcsec": 0.0,
            "kind": "SinglePointParameters"
          }
        ]
      },
      "reference_coordinate": {
        "kind": "equatorial",
        "ra": "19:24:51.05 degrees",
        "dec": "-29:14:30.12 degrees",
        "reference_frame": "ICRS",
        "unit": [
          "hourangle",
          "deg"
        ]
      }
    },
    {
      "target_id": "M87",
      "pointing_pattern": {
        "active": "SinglePointParameters",
        "parameters": [
          {
            "offset_x_arcsec": 0.0,
            "offset_y_arcsec": 0.0,
            "kind": "SinglePointParameters"
          }
        ]
      },
      "reference_coordinate": {
        "kind": "equatorial",
        "ra": "19:24:51.05 degrees",
        "dec": "-29:14:30.12 degrees",
        "reference_frame": "ICRS",
        "unit": [
          "hourangle",
          "deg"
        ]
      }
    }
  ]
}"""
VALID_ASSIGN_RESOURCE_MID_JSON_SB = """
{
  "interface": "https://schema.skao.int/ska-tmc-assignresources/2.1",
  "transaction_id": "txn-....-00001",
  "subarray_id": 1,
  "dish": {
    "receptor_ids": [
      "SKA036",
      "SKA001"
    ]
  },
  "sdp": {
    "resources": {
      "receptors": [
        "SKA036",
        "SKA001"
      ]
    },
    "interface": "https://schema.skao.int/ska-sdp-assignres/0.4",
    "execution_block": {
      "max_length": 3600.0,
      "beams": [
        {
          "beam_id": "vis0",
          "function": "visibilities"
        }
      ],
      "scan_types": [
        {
          "beams": {
            "vis0": {
              "channels_id": "vis_channels",
              "polarisations_id": "all"
            }
          },
          "scan_type_id": ".default"
        },
        {
          "beams": {
            "vis0": {
              "field_id": "M85"
            }
          },
          "derive_from": ".default",
          "scan_type_id": "M87"
        },
        {
          "beams": {
            "vis0": {
              "field_id": "Polaris Australis"
            }
          },
          "derive_from": ".default",
          "scan_type_id": "Polaris Australis"
        },
        {
          "beams": {
            "vis0": {
              "field_id": "M85"
            }
          },
          "derive_from": ".default",
          "scan_type_id": "flux calibrator"
        }
      ],
      "fields": [
        {
          "field_id": "Polaris Australis",
          "phase_dir": {
            "ra": [
              21.14664
            ],
            "dec": [
              -88.95636
            ],
            "reference_time": "2023-08-25T03:47:28.575617+00:00",
            "reference_frame": "ICRF3"
          }
        },
        {
          "field_id": ".default",
          "phase_dir": {
            "ra": [
              21.14664
            ],
            "dec": [
              -88.95636
            ],
            "reference_time": "2023-08-25T03:47:28.578000+00:00",
            "reference_frame": "ICRF3"
          }
        },
        {
          "field_id": "flux calibrator",
          "phase_dir": {
            "ra": [
              19.41418
            ],
            "dec": [
              -29.24170
            ],
            "reference_time": "2023-10-03T19:45:07.997338+00:00",
            "reference_frame": "ICRF3"
          }
        },
        {
          "field_id": "M87",
          "phase_dir": {
            "ra": [
              19.41418
            ],
            "dec": [
              -29.24170
            ],
            "reference_time": "2023-10-03T19:45:07.997338+00:00",
            "reference_frame": "ICRF3"
          }
        }
      ],
      "eb_id": "eb-test-20230825-35248",
      "channels": [
        {
          "spectral_windows": [
            {
              "stride": 2,
              "start": 0,
              "spectral_window_id": "fsp_1_channels",
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
              "count": 14880,
              "freq_max": 368000000.0,
              "freq_min": 350000000.0
            }
          ],
          "channels_id": "vis_channels1"
        },
        {
          "spectral_windows": [
            {
              "stride": 2,
              "start": 0,
              "spectral_window_id": "fsp_1_channels",
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
              "count": 14880,
              "freq_max": 368000000.0,
              "freq_min": 350000000.0
            }
          ],
          "channels_id": "vis_channels10"
        }
      ],
      "context": {},
      "polarisations": [
        {
          "corr_type": [
            "XX",
            "XY",
            "YX",
            "YY"
          ],
          "polarisations_id": "all"
        }
      ]
    },
    "processing_blocks": [
      {
        "script": {
          "name": "test-receive-addresses",
          "version": "0.7.1",
          "kind": "realtime"
        },
        "pb_id": "pb-test-20230825-35248",
        "parameters": {},
        "sbi_ids": [
          "sbi-test-20230825-35248"
        ]
      }
    ]
  }
}
"""

DEFAULT_TARGET_SPECS = {
    "flux calibrator": TargetSpec(
        dish_ids=["SKA001", "SKA036"],
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
        channelisation="vis_channels10",
        polarisation="all",
        processing="test-receive-addresses",
    ),
    "M87": TargetSpec(
        dish_ids=["SKA001", "SKA036"],
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
        channelisation="vis_channels1",
        polarisation="all",
        processing="test-receive-addresses",
        target=None,
    ),
}
flux_calibrator_target = {
    "target_id": "flux calibrator",
    "pointing_pattern": {
        "active": "SinglePointParameters",
        "parameters": [
            {
                "offset_x_arcsec": 0,
                "offset_y_arcsec": 0,
                "kind": "SinglePointParameters",
            }
        ],
    },
    "reference_coordinate": {
        "kind": "equatorial",
        "ra": "19:24:51.05 degrees",
        "dec": "-29:14:30.12 degrees",
        "reference_frame": "ICRS",
        "unit": ["hourangle", "deg"],
    },
}
polaris_australis_target = {
    "target_id": "Polaris Australis",
    "pointing_pattern": {
        "active": "SinglePointParameters",
        "parameters": [
            {
                "offset_x_arcsec": 0.0,
                "offset_y_arcsec": 0.0,
                "kind": "SinglePointParameters",
            }
        ],
    },
    "reference_coordinate": {
        "kind": "equatorial",
        "ra": "21:08:47.92 degrees",
        "dec": "-88:57:22.9 degrees",
        "reference_frame": "ICRS",
        "unit": ["hourangle", "deg"],
    },
}
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


def test_sb_generation_validate():
    """
    Test to validate SB generated using ObservationSB class
    """
    observation1 = ObservationSB()

    observation1.add_target_specs(DEFAULT_TARGET_SPECS)

    for target_id in DEFAULT_TARGET_SPECS.keys():
        observation1.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )

    scan_sequence = ["flux calibrator"]
    observation1.add_scan_sequence(scan_sequence)

    observation1.eb_id = "eb-mvp01-20231010-82511"
    obsconfig_scheduling_block_pdm_object = observation1.generate_pdm_object_for_sbd_save(
        DEFAULT_TARGET_SPECS
    )

    valid_scheduling_block_pdm_object = pdm_CODEC.loads(SBDefinition, VALID_SB_MID_JSON)

    obsconfig_scheduling_block_pdm_object.sdp_configuration.processing_blocks[0].pb_id = (
        valid_scheduling_block_pdm_object.sdp_configuration.processing_blocks[0].pb_id
    )
    obsconfig_scheduling_block_pdm_object.sdp_configuration.processing_blocks[0].sbi_ids = (
        valid_scheduling_block_pdm_object.sdp_configuration.processing_blocks[0].sbi_ids
    )
    obsconfig_scheduling_block_pdm_object.sdp_configuration.execution_block.eb_id = (
        valid_scheduling_block_pdm_object.sdp_configuration.execution_block.eb_id
    )
    obsconfig_scheduling_block_pdm_object.metadata.created_on = (
        valid_scheduling_block_pdm_object.metadata.created_on
    )
    obsconfig_scheduling_block_pdm_object.metadata.last_modified_on = (
        valid_scheduling_block_pdm_object.metadata.last_modified_on
    )

    obsconfig_scheduling_block_pdm_object.sbd_id = valid_scheduling_block_pdm_object.sbd_id

    obsconfig_scheduling_block_pdm_object.scan_sequence = (
        valid_scheduling_block_pdm_object.scan_sequence
    )
    obsconfig_scheduling_block_pdm_json = pdm_CODEC.dumps(obsconfig_scheduling_block_pdm_object)

    valid_scheduling_block_pdm_json = pdm_CODEC.dumps(valid_scheduling_block_pdm_object)

    sb_dict = json.loads(obsconfig_scheduling_block_pdm_json)
    valid_dict = json.loads(valid_scheduling_block_pdm_json)

    diff = DeepDiff(sb_dict, valid_dict, ignore_order=True)
    pprint(diff, indent=2)
    assert not diff, f"Dictionaries are not equal:{diff}"


def test_sb_generation_validate_target_spec_configuration():
    """Test to validate if required target_spec gets added correctly"""

    observation2 = ObservationSB()

    for key, value in DEFAULT_TARGET_SPECS.items():
        observation2.add_channel_configuration(value.channelisation, channel_configuration)

    observation2.add_target_specs(DEFAULT_TARGET_SPECS)

    for target_id in DEFAULT_TARGET_SPECS.keys():
        observation2.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )

    scan_sequence = ["flux calibrator"]
    observation2.add_scan_sequence(scan_sequence)

    observation2.eb_id = "eb-mvp01-20231010-82511"

    obsconfig_scheduling_block_pdm_object = observation2.generate_pdm_object_for_sbd_save(
        DEFAULT_TARGET_SPECS
    )

    obsconfig_scheduling_block_pdm_json = pdm_CODEC.dumps(obsconfig_scheduling_block_pdm_object)

    sb_dict = json.loads(obsconfig_scheduling_block_pdm_json)

    assert any(
        channel["channels_id"] == "vis_channels10"
        for channel in sb_dict["sdp_configuration"]["execution_block"]["channels"]
    )

    assert any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in sb_dict["sdp_configuration"]["execution_block"]["scan_types"]
    )

    assert sb_dict["dish_allocations"]["receptor_ids"] == [
        "SKA001",
        "SKA036",
    ] or ["SKA036", "SKA001"]

    assert flux_calibrator_target in sb_dict["targets"]


def test_sb_generation_validate_target_spec_configuration_remove():
    """Test to check if Target Specs configurations are removed properly"""

    observation3 = ObservationSB()
    observation3._channel_configurations = {}  # pylint: disable=W0212
    observation3.scan_sequence_data = []

    for key, value in DEFAULT_TARGET_SPECS.items():
        observation3.add_channel_configuration(value.channelisation, channel_configuration)

    observation3.add_target_specs(DEFAULT_TARGET_SPECS)

    for target_id in DEFAULT_TARGET_SPECS.keys():
        observation3.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M83")},
            derive_from=".default",
        )

    scan_sequence = ["flux calibrator"]
    observation3.add_scan_sequence(scan_sequence)

    observation3.eb_id = "eb-mvp01-20231010-82511"

    obsconfig_scheduling_block_pdm_object = observation3.generate_pdm_object_for_sbd_save(
        DEFAULT_TARGET_SPECS
    )

    obsconfig_scheduling_block_pdm_object.sdp_configuration.execution_block.channels = [
        channel
        for channel in obsconfig_scheduling_block_pdm_object.sdp_configuration.execution_block.channels
        if channel.channels_id != "vis_channels10"
    ]
    obsconfig_scheduling_block_pdm_object.sdp_configuration.execution_block.scan_types = [
        scan_type
        for scan_type in obsconfig_scheduling_block_pdm_object.sdp_configuration.execution_block.scan_types
        if scan_type.scan_type_id != "flux calibrator"
    ]
    obsconfig_scheduling_block_pdm_object.dish_allocations.receptor_ids.remove("SKA001")

    obsconfig_scheduling_block_pdm_object.targets = [
        target
        for target in obsconfig_scheduling_block_pdm_object.targets
        if target.target_id != "flux calibrator"
    ]
    obsconfig_scheduling_block_pdm_json = pdm_CODEC.dumps(obsconfig_scheduling_block_pdm_object)

    sb_dict = json.loads(obsconfig_scheduling_block_pdm_json)

    assert not any(
        channel["channels_id"] == "vis_channels10"
        for channel in sb_dict["sdp_configuration"]["execution_block"]["channels"]
    )

    assert not any(
        scan_type["scan_type_id"] == "flux calibrator"
        for scan_type in sb_dict["sdp_configuration"]["execution_block"]["scan_types"]
    )

    assert "SKA001" not in sb_dict["dish_allocations"]["receptor_ids"]

    assert flux_calibrator_target not in sb_dict["targets"]


def test_sb_generation_validate_default_target_spec():
    """Test to check if no Target spec is provided than Default target spec should be present"""
    observation = ObservationSB()
    observation.eb_id = "eb-mvp01-20231010-82511"
    obsconfig_scheduling_block_pdm_object = observation.generate_pdm_object_for_sbd_save()

    obsconfig_scheduling_block_pdm_json = pdm_CODEC.dumps(obsconfig_scheduling_block_pdm_object)
    sb_dict = json.loads(obsconfig_scheduling_block_pdm_json)

    assert polaris_australis_target in sb_dict["targets"]


def test_sb_validate_activities_parameter():
    """Test to check if ActivitySB instance parameters are getting updated"""

    observation = ObservationSB()
    observation.eb_id = "eb-mvp01-20231010-82511"
    default_activities_parameters = observation.get_activities()

    assert (
        default_activities_parameters["allocate"].path
        == "git://scripts/allocate_from_file_mid_sb.py"
    )

    activities_params = {
        "allocate_path": "git://scripts/new_allocate_path.py",
        "allocate_repo": "https://new-repository-url.com/ska-allocate.git",
        "observe_path": "new_observe_path.py",
        "observe_repo": "https://new-repository-url.com/ska-observe.git",
    }
    observation.add_activities_parameters(activities_params)
    modified_activities_parameters = observation.get_activities()

    assert modified_activities_parameters["allocate"].path == "git://scripts/new_allocate_path.py"


def test_sb_validate_invalid_activities_parameter():
    """Test to check if Attribute error is raised ActivitySB instance parameters while passing invalid parameters"""

    observation = ObservationSB()
    observation.eb_id = "eb-mvp01-20231010-82511"
    default_activities_parameters = observation.get_activities()

    assert (
        default_activities_parameters["allocate"].path
        == "git://scripts/allocate_from_file_mid_sb.py"
    )

    activities_params = {
        "invalid_parameter": "git://scripts/new_allocate_path.py",
        "allocate_repo": "https://new-repository-url.com/ska-allocate.git",
        "observe_path": "new_observe_path.py",
        "observe_repo": "https://new-repository-url.com/ska-observe.git",
    }
    with pytest.raises(AttributeError) as exc_info:
        observation.add_activities_parameters(activities_params)


def test_assign_resource_allocation_request_sb():
    """Test to check Validate Assign Resource Request using Scheduling Block"""
    observation = ObservationSB()
    observation._channel_configurations = {}  # pylint: disable=W0212

    for value in list(DEFAULT_TARGET_SPECS.values()):
        observation.add_channel_configuration(value.channelisation, channel_configuration)

    observation.add_target_specs(DEFAULT_TARGET_SPECS)
    for target_id in DEFAULT_TARGET_SPECS.keys():
        observation.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M85")},
            derive_from=".default",
        )

    observation.add_scan_sequence(["calibrator scan"])
    observation.eb_id = "eb-test-20230825-35248"
    pdm_allocation = observation.generate_pdm_object_for_sbd_save(DEFAULT_TARGET_SPECS)
    pdm_allocation.sbd_id = "sbd-mvp01-20231106-00002"
    obsconfig_assign_resource_configuration_sb_object = observation.generate_allocate_config_sb(
        pdm_allocation
    ).as_object
    valid_assign_resource_configuration_object = AssignResourcesRequestSchema().loads(
        VALID_ASSIGN_RESOURCE_MID_JSON_SB
    )

    obsconfig_assign_resource_configuration_sb_object.sdp_config.processing_blocks[0].pb_id = (
        valid_assign_resource_configuration_object.sdp_config.processing_blocks[0].pb_id
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.processing_blocks[0].sbi_ids = (
        valid_assign_resource_configuration_object.sdp_config.processing_blocks[0].sbi_ids
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.eb_id = (
        valid_assign_resource_configuration_object.sdp_config.execution_block.eb_id
    )

    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        0
    ].phase_dir.reference_time = valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
        0
    ].phase_dir.reference_time
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        1
    ].phase_dir.reference_time = valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
        1
    ].phase_dir.reference_time
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        2
    ].phase_dir.reference_time = valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
        2
    ].phase_dir.reference_time
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        3
    ].phase_dir.reference_time = valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
        3
    ].phase_dir.reference_time

    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        0
    ].phase_dir.ra[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            0
        ].phase_dir.ra[0],
        5,
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        0
    ].phase_dir.dec[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            0
        ].phase_dir.dec[0],
        5,
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        1
    ].phase_dir.ra[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            1
        ].phase_dir.ra[0],
        5,
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        1
    ].phase_dir.dec[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            1
        ].phase_dir.dec[0],
        5,
    )

    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        2
    ].phase_dir.ra[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            2
        ].phase_dir.ra[0],
        5,
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        2
    ].phase_dir.dec[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            2
        ].phase_dir.dec[0],
        5,
    )

    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        3
    ].phase_dir.ra[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            3
        ].phase_dir.ra[0],
        5,
    )
    obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
        3
    ].phase_dir.dec[0] = round(
        obsconfig_assign_resource_configuration_sb_object.sdp_config.execution_block.fields[
            3
        ].phase_dir.dec[0],
        5,
    )

    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[0].phase_dir.ra[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            0
        ].phase_dir.ra[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[0].phase_dir.dec[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            0
        ].phase_dir.dec[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[1].phase_dir.ra[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            1
        ].phase_dir.ra[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[1].phase_dir.dec[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            1
        ].phase_dir.dec[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[2].phase_dir.dec[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            2
        ].phase_dir.dec[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[2].phase_dir.ra[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            2
        ].phase_dir.ra[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[3].phase_dir.dec[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            3
        ].phase_dir.dec[0],
        5,
    )
    valid_assign_resource_configuration_object.sdp_config.execution_block.fields[3].phase_dir.ra[
        0
    ] = round(
        valid_assign_resource_configuration_object.sdp_config.execution_block.fields[
            3
        ].phase_dir.ra[0],
        5,
    )

    obsconfig_json = AssignResourcesRequestSchema().dumps(
        obsconfig_assign_resource_configuration_sb_object
    )
    valid_json = AssignResourcesRequestSchema().dumps(valid_assign_resource_configuration_object)

    obsconfig_dict = json.loads(obsconfig_json)
    valid_dict = json.loads(valid_json)

    diff = DeepDiff(obsconfig_dict, valid_dict, ignore_order=True)
    pprint(diff, indent=4)
    assert not diff, f"Dictionaries are not equal:{diff}"
