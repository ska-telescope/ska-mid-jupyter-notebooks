import json
import os

import pytest
from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand
from ska_tmc_cdm.schemas.subarray_node.configure.core import (
    ConfigureRequestSchema,
)
from ska_tmc_cdm.schemas.subarray_node.configure.csp import (
    CommonConfigurationSchema,
    CSPConfigurationSchema,
    LowCBFConfigurationSchema,
    StationConfigurationSchema,
    StnBeamConfigurationSchema,
    SubarrayConfigurationSchema,
)
from ska_tmc_cdm.schemas.subarray_node.configure.mccs import (
    MCCSConfigurationSchema,
)
from ska_tmc_cdm.schemas.subarray_node.configure.sdp import (
    SDPConfigurationSchema,
)
from ska_tmc_cdm.schemas.subarray_node.configure.tmc import (
    TMCConfigurationSchema,
)
from ska_tmc_cdm.utils import assert_json_is_equal

from ska_mid_jupyter_notebooks.obsconfig.config import Observation, ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec

VALID_CONFIGURE_RESOURCE_PI17_LOW_JSON = """{
  "interface": "https://schema.skao.int/ska-low-tmc-configure/3.0",
  "transaction_id": "txn-....-00001",
  "mccs": {
    "stations": [
      {
        "station_id": 1
      },
      {
        "station_id": 2
      }
    ],
    "subarray_beams": [
      {
        "subarray_beam_id": 1,
        "station_ids": [
          1,
          2
        ],
        "update_rate": 0,
        "channels": [
          [
            0,
            8,
            1,
            1
          ],
          [
            8,
            8,
            2,
            1
          ],
          [
            24,
            16,
            2,
            1
          ]
        ],
        "antenna_weights": [
          1,
          1,
          1
        ],
        "phase_centre": [
          0,
          0
        ],
        "target": {
          "reference_frame": "HORIZON",
          "target_name": "DriftScan",
          "az": 180,
          "el": 45
        }
      }
    ]
  },
  "sdp": {
    "interface": "https://schema.skao.int/ska-sdp-configure/0.4",
    "scan_type": "target:a"
  },
  "csp": {
    "interface": "https://schema.skao.int/ska-csp-configure/2.5",
    "subarray": {
      "subarray_name": "science period 23"
    },
    "common": {
      "config_id": "sbi-mvp01-20200325-00001-science_A"
    },
    "lowcbf": {
      "stations": {
        "stns": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            3,
            0
          ],
          [
            4,
            0
          ]
        ],
        "stn_beams": [
          {
            "beam_id": 1,
            "freq_ids": [
              64,
              65,
              66,
              67,
              68,
              69,
              70,
              71
            ],
            "boresight_dly_poly": "url"
          }
        ]
      },
      "timing_beams": {
        "beams": [
          {
            "pst_beam_id": 13,
            "stn_beam_id": 1,
            "offset_dly_poly": "url",
            "stn_weights": [
              0.9,
              1,
              1,
              0.9
            ],
            "jones": "url",
            "dest_chans": [
              128,
              256
            ],
            "rfi_enable": [
              true,
              true,
              true
            ],
            "rfi_static_chans": [
              1,
              206,
              997
            ],
            "rfi_dynamic_chans": [
              242,
              1342
            ],
            "rfi_weighted": 0.87
          }
        ]
      }
    }
  },
  "tmc": {
    "scan_duration": 10.0
  }
}
"""

VALID_CONFIGURE_RESOURCE_PI16_MID_JSON = """{
  "interface": "https://schema.skao.int/ska-tmc-configure/2.1",
  "pointing": {
    "target": {
      "ra": "00:49:56.4466",
      "dec": "+02:03:08.598",
      "reference_frame": "ICRS",
      "target_name": "target:a"
    }
  },
  "dish": {
    "receiver_band": "2"
  },
  "sdp": {
    "interface": "https://schema.skao.int/ska-sdp-configure/0.4",
    "scan_type": "target:a"
  },
  "csp": {
    "interface": "https://schema.skao.int/ska-csp-configure/2.5",
    "subarray": {
      "subarray_name": "dummy name"
    },
    "common": {
      "config_id": "eb-mvp01-20231219-25117",
      "frequency_band": "2",
      "subarray_id": 1
    },
    "cbf": {
      "fsp": [
        {
          "fsp_id": 1,
          "function_mode": "CORR",
          "frequency_slice_id": 1,
          "zoom_factor": 0,
          "integration_factor": 1,
          "channel_averaging_map": [
            [
              0,
              2
            ],
            [
              744,
              0
            ]
          ],
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
          "zoom_factor": 1,
          "integration_factor": 1,
          "channel_averaging_map": [
            [
              0,
              2
            ],
            [
              744,
              0
            ]
          ],
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
          "channel_offset": 744,
          "zoom_window_tuning": 1050000
        }
      ]
    }
  },
  "tmc": {
    "scan_duration": 10.0
  }
}"""

VALID_TMC_BLOCK_PI17_LOW_JSON = """{
    "scan_duration": 10.0
  } """

VALID_TMC_BLOCK_PI16_MID_JSON = """{
    "scan_duration": 10.0
  }"""

VALID_STATION_BEAM_CONFIGURATION = """
    {
      "beam_id": 1,
      "freq_ids": [
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71
      ],
      "boresight_dly_poly": "url"
    }
  """

VALID_MCCS_BLOCK_PI17_LOW_JSON = """{
    "stations": [
      {
        "station_id": 1
      },
      {
        "station_id": 2
      }
    ],
    "subarray_beams": [
      {
        "subarray_beam_id": 1,
        "station_ids": [
          1,
          2
        ],
        "update_rate": 0.0,
        "channels": [
          [
            0,
            8,
            1,
            1
          ],
          [
            8,
            8,
            2,
            1
          ],
          [
            24,
            16,
            2,
            1
          ]
        ],
        "antenna_weights": [
          1.0,
          1.0,
          1.0
        ],
        "phase_centre": [
          0.0,
          0.0
        ],
        "target": {
          "reference_frame": "HORIZON",
          "target_name": "DriftScan",
          "az": 180.0,
          "el": 45.0
        }
      }
    ]
  } """

VALID_SDP_BLOCK_PI17_LOW_JSON = """{
    "interface": "https://schema.skao.int/ska-sdp-configure/0.4",
    "scan_type": "target:a"
  }"""
VALID_SDP_BLOCK_PI16_MID_JSON = """{
    "interface": "https://schema.skao.int/ska-sdp-configure/0.4",
    "scan_type": "target:a"
  }"""

VALID_COMMOM_BLOCK_PI17_LOW_JSON = """{
    "config_id": "sbi-mvp01-20200325-00001-science_A"
  }"""

VALID_SUBARRAY_BLOCK_PI17_LOW_JSON = """{
    "subarray_name": "science period 23"
  }"""

VALID_CSP_BLOCK_PI17_LOW_JSON = """{
    "interface": "https://schema.skao.int/ska-csp-configure/2.5",
    "subarray": {
      "subarray_name": "science period 23"
    },
    "common": {
      "config_id": "sbi-mvp01-20200325-00001-science_A"
    },
    "lowcbf": {
      "stations": {
        "stns": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            3,
            0
          ],
          [
            4,
            0
          ]
        ],
        "stn_beams": [
          {
            "beam_id": 1,
            "freq_ids": [
              64,
              65,
              66,
              67,
              68,
              69,
              70,
              71
            ],
            "boresight_dly_poly": "url"
          }
        ]
      },
      "timing_beams": {
        "beams": [
          {
            "pst_beam_id": 13,
            "stn_beam_id": 1,
            "offset_dly_poly": "url",
            "stn_weights": [
              0.9,
              1,
              1,
              0.9
            ],
            "jones": "url",
            "dest_chans": [
              128,
              256
            ],
            "rfi_enable": [
              true,
              true,
              true
            ],
            "rfi_static_chans": [
              1,
              206,
              997
            ],
            "rfi_dynamic_chans": [
              242,
              1342
            ],
            "rfi_weighted": 0.87
          }
        ]
      }
    }
  } """
VALID_CSP_BLOCK_PI16_MID_JSON = """{
    "interface": "https://schema.skao.int/ska-csp-configure/2.5",
    "subarray": {
      "subarray_name": "dummy name"
    },
    "common": {
      "config_id": "eb-mvp01-20231219-25117",
      "frequency_band": "2",
      "subarray_id": 1
    },
    "cbf": {
      "fsp": [
        {
          "fsp_id": 1,
          "function_mode": "CORR",
          "frequency_slice_id": 1,
          "zoom_factor": 0,
          "integration_factor": 1,
          "channel_averaging_map": [
            [
              0,
              2
            ],
            [
              744,
              0
            ]
          ],
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
          "zoom_factor": 1,
          "integration_factor": 1,
          "channel_averaging_map": [
            [
              0,
              2
            ],
            [
              744,
              0
            ]
          ],
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
          "channel_offset": 744,
          "zoom_window_tuning": 1050000
        }
      ]
    }
  }"""

VALID_TIMING_BEAMS_CONFIGURATION = """{
    "beams": [
      {
        "pst_beam_id": 13,
        "stn_beam_id": 1,
        "offset_dly_poly": "url",
        "stn_weights": [
          0.9,
          1.0,
          1.0,
          0.9
        ],
        "jones": "url",
        "dest_chans": [
          128,
          256
        ],
        "rfi_enable": [
          true,
          true,
          true
        ],
        "rfi_static_chans": [
          1,
          206,
          997
        ],
        "rfi_dynamic_chans": [
          242,
          1342
        ],
        "rfi_weighted": 0.87
      }
    ]
  }"""

VALID_BEAM_CONFIGURATION = """
    {
      "pst_beam_id": 13,
      "stn_beam_id": 1,
      "offset_dly_poly": "url",
      "stn_weights": [
        0.9,
        1.0,
        1.0,
        0.9
      ],
      "jones": "url",
      "dest_chans": [
        128,
        256
      ],
      "rfi_enable": [
        true,
        true,
        true
      ],
      "rfi_static_chans": [
        1,
        206,
        997
      ],
      "rfi_dynamic_chans": [
        242,
        1342
      ],
      "rfi_weighted": 0.87
    }
  """

VALID_STATION_CONFIGURATION = """{
    "stns": [
      [
        1,
        0
      ],
      [
        2,
        0
      ],
      [
        3,
        0
      ],
      [
        4,
        0
      ]
    ],
    "stn_beams": [
      {
        "beam_id": 1,
        "freq_ids": [
          64,
          65,
          66,
          67,
          68,
          69,
          70,
          71
        ],
        "boresight_dly_poly": "url"
      }
    ]
  }"""

VALID_CSP_LOWCBF_JSON = """{
      "stations": {
        "stns": [
          [
            1,
            0
          ],
          [
            2,
            0
          ],
          [
            3,
            0
          ],
          [
            4,
            0
          ]
        ],
        "stn_beams": [
          {
            "beam_id": 1,
            "freq_ids": [
              64,
              65,
              66,
              67,
              68,
              69,
              70,
              71
            ],
            "boresight_dly_poly": "url"
          }
        ]
      },
      "timing_beams": {
        "beams": [
          {
            "pst_beam_id": 13,
            "stn_beam_id": 1,
            "offset_dly_poly": "url",
            "stn_weights": [
              0.9,
              1,
              1,
              0.9
            ],
            "jones": "url",
            "dest_chans": [
              128,
              256
            ],
            "rfi_enable": [
              true,
              true,
              true
            ],
            "rfi_static_chans": [
              1,
              206,
              997
            ],
            "rfi_dynamic_chans": [
              242,
              1342
            ],
            "rfi_weighted": 0.87
          }
        ]
      }
    }"""

VALID_CONFIGURE_RESOURCE_MID_JSON = """{
  "interface": "https://schema.skao.int/ska-tmc-configure/2.2",
  "pointing": {
    "target": {
      "reference_frame": "ICRS",
      "ra": "01:17:39.40333333",
      "dec": "-29:14:30.12",
      "target_name": "M87"
    }
  },
  "dish": {
    "receiver_band": "1"
  },
  "csp": {
    "common": {
      "config_id": "sbi-mvp01-20200325-00001-science_A",
      "frequency_band": "1",
      "subarray_id": 1
    },
    "interface": "https://schema.skao.int/ska-csp-configure/2.0",
    "cbf": {
      "fsp": [
        {
          "frequency_slice_id": 1,
          "integration_factor": 10,
          "zoom_factor": 0,
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
          "fsp_id": 1,
          "channel_offset": 0,
          "function_mode": "CORR"
        },
        {
          "frequency_slice_id": 1,
          "integration_factor": 10,
          "zoom_factor": 0,
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
          "fsp_id": 2,
          "channel_offset": 744,
          "function_mode": "CORR"
        }
      ]
    },
    "subarray": {
      "subarray_name": "science period 23"
    }
  },
  "tmc": {
    "scan_duration": 10.0
  },
  "sdp": {
    "interface": "https://schema.skao.int/ska-sdp-configure/0.4",
    "scan_type": "M87"
  }
}
"""


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_lowcbf_configuration_object_using_observation_class():
    """
    Validates Low cbf config object returned using ObsConfig Observation class
    """

    obsconfig_lowcbf_configuration_object = (
        Observation().generate_lowcbf_configure_resource_config().as_object
    )
    valid_lowcbf_configuration_object = LowCBFConfigurationSchema().loads(
        VALID_CSP_LOWCBF_JSON
    )
    assert (
        obsconfig_lowcbf_configuration_object
        == valid_lowcbf_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_station_configuration_object_using_observation_class():
    """
    Validates Station config object returned using ObsConfig Observation class
    """

    obsconfig_station_configuration_object = (
        Observation().generate_station_config().as_object
    )
    valid_station_configuration_object = StationConfigurationSchema().loads(
        VALID_STATION_CONFIGURATION
    )
    assert (
        obsconfig_station_configuration_object
        == valid_station_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_station_beam_configuration_object_using_observation_class():
    """
    Validates Station beam config object returned using ObsConfig Observation class
    """

    obsconfig_station_beam_configuration_object = (
        Observation().generate_station_beam_config().as_object
    )
    valid_station_beam_configuration_object = (
        StnBeamConfigurationSchema().loads(VALID_STATION_BEAM_CONFIGURATION)
    )
    assert (
        obsconfig_station_beam_configuration_object
        == valid_station_beam_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_csp_configuration_object_using_observation_class():
    """
    Validates that LOW CSP config object returned using ObsConfig Observation class
    """

    obsconfig_csp_configuration_object = (
        Observation().generate_csp_scan_config_low().as_object
    )
    valid_csp_configuration_object = CSPConfigurationSchema().loads(
        VALID_CSP_BLOCK_PI17_LOW_JSON
    )
    assert obsconfig_csp_configuration_object == valid_csp_configuration_object


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_validate_csp_configuration_object_using_mid_observation_class():
    """
    Validates that Mid CSP config object returned using ObsConfig Observation class
    """


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_mccs_configuration_object_using_observation_class():
    """
    Validates MCCS config object returned using ObsConfig Observation class
    """
    obsconfig_mccs_configuration_object = (
        Observation().generate_mccs_scan_config().as_object
    )
    valid_mccs_configuration_object = MCCSConfigurationSchema().loads(
        VALID_MCCS_BLOCK_PI17_LOW_JSON
    )

    assert (
        obsconfig_mccs_configuration_object == valid_mccs_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_tmc_configuration_object_using_observation_class():
    """
    Validates that TMC config object returned using ObsConfig Observation class
    """

    obsconfig_tmc_configuration_object = (
        Observation().generate_tmc_scan_config(10)
    )
    valid_tmc_configuration_object = TMCConfigurationSchema().loads(
        VALID_TMC_BLOCK_PI17_LOW_JSON
    )
    assert obsconfig_tmc_configuration_object == valid_tmc_configuration_object


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_validate_tmc_configuration_object_using_mid_observation_class():
    """
    Validates that TMC config object returned using ObsConfig Observation class for Mid
    """

    obsconfig_tmc_configuration_object = (
        Observation().generate_tmc_scan_config(10)
    )
    valid_tmc_configuration_object = TMCConfigurationSchema().loads(
        VALID_TMC_BLOCK_PI16_MID_JSON
    )
    assert obsconfig_tmc_configuration_object == valid_tmc_configuration_object


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_sdp_configuration_object_using_low_observation_class():
    """
    Validates SDP config object returned using ObsConfig Observation class for low
    """

    obsconfig_sdp_configuration_object = (
        Observation().generate_sdp_scan_config().as_object
    )
    valid_sdp_configuration_object = SDPConfigurationSchema().loads(
        VALID_SDP_BLOCK_PI17_LOW_JSON
    )
    assert obsconfig_sdp_configuration_object == valid_sdp_configuration_object


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_validate_sdp_configuration_object_using_mid_observation_class():
    """
    Validates SDP config object returned using ObsConfig Observation class for mid
    """


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_common_configuration_object_using_observation_class():
    """
    Validates that Common config object returned using ObsConfig Observation class
    """

    obsconfig_common_configuration_object = (
        Observation().generate_common_configure_resource_config_low().as_object
    )
    valid_common_resource_configuration_object = (
        CommonConfigurationSchema().loads(VALID_COMMOM_BLOCK_PI17_LOW_JSON)
    )
    assert (
        obsconfig_common_configuration_object
        == valid_common_resource_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_validate_subarray_configuration_object_using_observation_class():
    """
    Validates that Subarray config object returned using ObsConfig Observation class
    """

    obsconfig_subarray_configuration_object = (
        Observation()
        .generate_subarray_configure_resource_config_low()
        .as_object
    )
    valid_subarray_resource_configuration_object = (
        SubarrayConfigurationSchema().loads(VALID_SUBARRAY_BLOCK_PI17_LOW_JSON)
    )
    assert (
        obsconfig_subarray_configuration_object
        == valid_subarray_resource_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-mid",
    reason="This test is for Low Observation",
)
def test_configure_resource():
    """
    Validates that Configure request object returned using ObsConfig Observation class
    """
    obs_configure_resource_request_JSON = (
        Observation().generate_scan_config_low().as_object
    )
    valid_configure_resource_configuration_object = (
        ConfigureRequestSchema().loads(VALID_CONFIGURE_RESOURCE_PI17_LOW_JSON)
    )
    assert (
        obs_configure_resource_request_JSON
        == valid_configure_resource_configuration_object
    )


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_configure_resource_sb():
    """
    Validates that Configure request object returned using ObsConfig Observation class
    """
    # Given
    configure_data = json.loads(VALID_CONFIGURE_RESOURCE_MID_JSON)

    configure_data["csp"]["common"]["frequency_band"] = "2"
    configure_data["csp"]["subarray"]["subarray_name"] = "dummy name"
    configure_data["dish"]["receiver_band"] = "2"
    configure_data.update({"transaction_id": "txn-....-00001"})
    VALID_CONFIGURE_RESOURCE_MID_JSON_SB = json.dumps(configure_data)

    DEFAULT_TARGET_SPECS = {
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
                    "five_point_parameters": FivePointParameters(
                        offset_arcsec=0.0
                    ),
                    "cross_scan_parameters": CrossScanParameters(
                        offset_arcsec=0.0
                    ),
                    "active_pointing_pattern_type": "single_pointing_parameters",
                },
            },
            scan_type="M87",
            band=ReceiverBand.BAND_2,
            channelisation="vis_channels",
            polarisation="all",
            processing="test-receive-addresses",
            dishes="two",
            target=None,
        )
    }

    observation = ObservationSB()
    observation.add_target_specs(DEFAULT_TARGET_SPECS)
    for target_id in DEFAULT_TARGET_SPECS.keys():
        observation.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": {"beam_id": "vis0", "field_id": "M85"}},
            derive_from=".default",
        )

    scan_sequence = ["M87"]
    observation.add_scan_sequence(scan_sequence)

    observation.eb_id = "eb-test-20230825-35248"

    pdm_allocation = observation.generate_pdm_object_for_sbd_save(
        DEFAULT_TARGET_SPECS
    )

    configure_object = observation.generate_scan_config_sb(
        pdm_observation_request=pdm_allocation,
        scan_definition_id=scan_sequence[0],
        scan_duration=10.0,
    ).as_object

    configure_json = ConfigureRequestSchema().dumps(configure_object)

    assert_json_is_equal(configure_json, VALID_CONFIGURE_RESOURCE_MID_JSON_SB)


@pytest.mark.skipif(
    os.environ["SKA_TELESCOPE"] == "SKA-low",
    reason="This test is for Mid Observation",
)
def test_fsp_add_check_for_configure_resource_mid_non_sb():
    """
    Validates functionality for  Adding FSP Configuration for MID configure resource non SB request
    """
    from ska_tmc_cdm.messages.subarray_node.configure.csp import (
        FSPFunctionMode,
    )

    DEFAULT_FSP_CONFIGURATION = {
        "fsp1": {
            "fsp_id": 1,
            "function_mode": FSPFunctionMode.CORR,
            "frequency_slice_id": 1,
            "integration_factor": 1,
            "zoom_factor": 0,
            "channel_averaging_map": [(0, 2), (744, 0)],
            "output_link_map": [(0, 0), (200, 1)],
            "channel_offset": 0,
        },
        "fsp2": {
            "fsp_id": 2,
            "function_mode": FSPFunctionMode.CORR,
            "frequency_slice_id": 1,
            "integration_factor": 1,
            "zoom_factor": 1,
            "channel_averaging_map": [(0, 2), (744, 0)],
            "output_link_map": [(0, 5), (200, 5)],
            "channel_offset": 744,
            "zoom_window_tuning": 25,
        },
    }

    observation = Observation()
    observation.add_fsp_configuration(DEFAULT_FSP_CONFIGURATION)

    obs_configure_resource_request_object = (
        observation.generate_scan_config().as_object  # pylint: disable=no-member
    )

    # zoom_window_tuning value has been modified for fsp2 from 65000 to 25.
    assert (
        obs_configure_resource_request_object.csp.cbf_config.fsp_configs[
            1
        ].zoom_window_tuning
        == 25
    )
