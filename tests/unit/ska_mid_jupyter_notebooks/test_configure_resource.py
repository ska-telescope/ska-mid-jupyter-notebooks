import json

from ska_oso_pdm.entities.common.target import (
    CrossScanParameters,
    FivePointParameters,
    RasterParameters,
    SinglePointParameters,
    StarRasterParameters,
)
from ska_oso_pdm.entities.sdp import BeamMapping
from ska_tmc_cdm.messages.subarray_node.configure.core import ReceiverBand
from ska_tmc_cdm.schemas.subarray_node.configure.core import ConfigureRequestSchema
from ska_tmc_cdm.schemas.subarray_node.configure.tmc import TMCConfigurationSchema
from ska_tmc_cdm.utils import assert_json_is_equal

from ska_mid_jupyter_notebooks.obsconfig.config import ObservationSB
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpec

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

VALID_TMC_BLOCK_PI16_MID_JSON = """{
    "scan_duration": 10.0
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


def test_validate_csp_configuration_object_using_mid_observation_class():
    """
    Validates that Mid CSP config object returned using ObsConfig Observation class
    """


def test_validate_tmc_configuration_object_using_mid_observation_class():
    """
    Validates that TMC config object returned using ObsConfig Observation class for Mid
    """

    obsconfig_tmc_configuration_object = ObservationSB().generate_tmc_scan_config(10)
    valid_tmc_configuration_object = TMCConfigurationSchema().loads(VALID_TMC_BLOCK_PI16_MID_JSON)
    assert obsconfig_tmc_configuration_object == valid_tmc_configuration_object


def test_validate_sdp_configuration_object_using_mid_observation_class():
    """
    Validates SDP config object returned using ObsConfig Observation class for mid
    """


def test_configure_resource_sb():
    """
    Validates that Configure request object returned using ObsConfig Observation class
    """
    # Given
    configure_data = dict(json.loads(VALID_CONFIGURE_RESOURCE_MID_JSON))

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
                    "five_point_parameters": FivePointParameters(offset_arcsec=0.0),
                    "cross_scan_parameters": CrossScanParameters(offset_arcsec=0.0),
                    "active_pointing_pattern_type": "single_pointing_parameters",
                },
            },
            scan_type="M87",
            band=ReceiverBand.BAND_2,
            channelisation="vis_channels",
            polarisation="all",
            processing="test-receive-addresses",
            dish_ids=["ska000"],
            target=None,
        )
    }

    observation = ObservationSB()
    observation.add_target_specs(DEFAULT_TARGET_SPECS)
    for target_id in DEFAULT_TARGET_SPECS.keys():
        observation.add_scan_type_configuration(
            config_name=target_id,
            beams={"vis0": BeamMapping(beam_id="vis0", field_id="M85")},
            derive_from=".default",
        )

    scan_sequence = ["M87"]
    observation.add_scan_sequence(scan_sequence)

    observation.eb_id = "eb-test-20230825-35248"

    pdm_allocation = observation.generate_pdm_object_for_sbd_save(DEFAULT_TARGET_SPECS)

    configure_object = observation.generate_scan_config_sb(
        pdm_observation_request=pdm_allocation,
        scan_definition_id=scan_sequence[0],
        scan_duration=10.0,
    ).as_object

    configure_json = ConfigureRequestSchema().dumps(configure_object)

    assert_json_is_equal(configure_json, VALID_CONFIGURE_RESOURCE_MID_JSON_SB)
