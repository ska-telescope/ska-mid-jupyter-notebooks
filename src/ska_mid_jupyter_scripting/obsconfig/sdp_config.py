from typing import Any, NamedTuple, Tuple, Union
from ska_mid_jupyter_scripting.obsconfig.target_spec import TargetSpecs
from ska_mid_jupyter_scripting.obsconfig.base import load_next_sb
from ska_oso_pdm.entities.sdp import BeamMapping, ProcessingBlock
from ska_oso_pdm.entities.sdp.beam import Beam, BeamFunction
from ska_oso_pdm.entities.sdp import ScanType as ScanTypeSB
from ska_oso_pdm.entities.sdp.processing_block import Script, ScriptKind
from ska_tmc_cdm.messages.central_node.sdp import (
    BeamConfiguration,
    ChannelConfiguration,
    EBScanType,
    EBScanTypeBeam,
    ExecutionBlockConfiguration,
    FieldConfiguration,
    PhaseDir,
    PolarisationConfiguration,
    ProcessingBlockConfiguration,
    ScriptConfiguration,
    SDPConfiguration,
)


class Beamgrouping(NamedTuple):
    id: str
    configuration: BeamConfiguration
    types: dict[str, EBScanTypeBeam]


class BeamgroupingSB(NamedTuple):
    id: str
    configuration: Beam
    types: dict[str, BeamMapping]


DEFAULT_BEAMS_SB = {
    "vis0": BeamgroupingSB(
        "vis0",
        Beam(beam_id="vis0", function=BeamFunction.VISIBILITIES),
        {
            "default_beam_type": BeamMapping(
                beam_id="vis0",
                channels_id="vis_channels",
                polarisations_id="all",
            ),
            "polaris_australis_beam_type": BeamMapping(
                beam_id="vis0", field_id="Polaris Australis"
            ),
        },
    ),
    "vlbi": BeamgroupingSB(
        "vlbi",
        Beam(beam_id="vlbi", function=BeamFunction.VISIBILITIES),
        {
            "polaris_australis_beam_type": BeamMapping(
                beam_id="vlbi",
                field_id="Polaris Australis",
                channels_id="vlbi_channels",
                polarisations_id="all",
            ),
        },
    ),
}

def default_scan_types_sb(owner: "ScanTypes"):
    """
    Returns the default scan types
    :param owner: ScanTypes object
    :return: Default scan types dictionary for SB
    """
    scan_type_details = {  # list of beam mappiing
        ".default": ScanTypeSB(
            scan_type_id=".default",
            beams=[
                owner.get_beam_configurations("vis0").types[
                    "default_beam_type"
                ],
            ],
        ),
        "bandpass calibrator": ScanTypeSB(
            scan_type_id="bandpass calibrator",
            beams=[
                owner.get_beam_configurations("vis0").types[
                    "default_beam_type"
                ]
            ],
            derive_from=".default",
        ),
        "Polaris Australis": ScanTypeSB(
            scan_type_id="Polaris Australis",
            beams=[
                owner.get_beam_configurations("vis0").types[
                    "polaris_australis_beam_type"
                ]
            ],
            derive_from=".default",
        ),
        "M85": ScanTypeSB(
            scan_type_id="M85",
            beams=[
                owner.get_beam_configurations("vis0").types[
                    "default_beam_type"
                ]
            ],
            derive_from=".default",
        ),
    }
    return scan_type_details

DEFAULT_SCAN_SEQUENCE_LIST = ["Polaris Australis"]

class ScanTypes(TargetSpecs):
    def __init__(
        self,
        additional_beam_groupings: Union[
            list[Beamgrouping], list[BeamgroupingSB]
        ]
        | None = None,
        additional_scan_types: Union[list[EBScanType], list[ScanTypeSB]]
        | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes ScanTypes class
        :param additional_beam_groupings: list of Beamgrouping or BeamgroupingSB
        :param additional_scan_types: list of EBScanType or ScanTypeSB
        :param **kwargs: Any
        :return: None
        """
        super().__init__(**kwargs)

        self._beam_configurations = DEFAULT_BEAMS_SB
        self._scan_type_configurations = default_scan_types_sb(self)

        self.scan_sequence_data = DEFAULT_SCAN_SEQUENCE_LIST

        if additional_beam_groupings is not None:
            self._beam_configurations = {
                **self._beam_configurations,
                **{
                    beam_grouping.id: beam_grouping
                    for beam_grouping in additional_beam_groupings
                },
            }
        if additional_scan_types is not None:
            self._scan_type_configurations = {
                **self._scan_type_configurations,
                **{
                    additional_scan_type.scan_type_id: additional_scan_type
                    for additional_scan_type in additional_scan_types
                },
            }

        self._pending_scan_type = None

    def add_beam_configuration(
        self,
        config_name: str,
        function: Union[str, BeamFunction],
        beam_types: dict[str, Union[EBScanTypeBeam, ScanTypeSB]] | None = None,
        search_beam_id: int | None = None,
        timing_beam_id: int | None = None,
        vlbi_beam_id: int | None = None,
    ):
        """
        Add a beam configuration
        :param config_name: name of the beam configuration
        :param function: beam function
        :param beam_types: beam types
        :param search_beam_id: search beam id
        :param timing_beam_id: timing beam id
        :param vlbi_beam_id: vlbi beam id
        :return: None
        """
        assert (
            self._beam_configurations.get(config_name) is None
        ), f"configuration {config_name} already exists."

        beam_data = {
            "beam_id": config_name,
            "function": function,
        }

        if search_beam_id:
            beam_data["search_beam_id"] = search_beam_id
        if timing_beam_id:
            beam_data["timing_beam_id"] = timing_beam_id
        if vlbi_beam_id:
            beam_data["vlbi_beam_id"] = vlbi_beam_id

        beam_configuration = Beam(**beam_data)
        self._beam_configurations[config_name] = BeamgroupingSB(
            config_name, beam_configuration, beam_types
        )

    def add_beam_types(
        self,
        grouping_id: str,
        beam_types: dict[str, Union[EBScanTypeBeam, ScanTypeSB]],
    ):
        """
        Add beam types
        :param grouping_id: grouping id
        :param beam_types: type of beam
        :return: None
        """
        assert self._beam_configurations.get(
            grouping_id
        ), f"grouping {grouping_id} does not exist, did you call `add_beam_configuration()`."
        current_beam_types = self._beam_configurations[grouping_id].types
        current_beam_configuration = self._beam_configurations[
            grouping_id
        ].configuration
        self._beam_configurations[grouping_id] = Beamgrouping(
            grouping_id,
            current_beam_configuration,
            {**current_beam_types, **beam_types},
        )

    def add_scan_type_configuration(
        self,
        config_name: str,
        beams: Union[
            dict[str, dict[str, Union[EBScanTypeBeam, BeamMapping, str]]],
            Tuple[str, str],
            list[Tuple[str, str]],
        ],
        derive_from: str | None = None,
    ):
        """
        Add a scan type configuration
        :param config_name: name of scan_type configuration
        :param beams: beams
        :param derive_from: derive from
        :return: None
        """
        agg_beam_types: dict[str, Union[EBScanTypeBeam, ScanTypeSB]] = dict()

        def add_beam(grouping_id: str, beam_type_id: str):
            """
            Add a beam
            :param grouping_id: grouping id
            :param beam_type_id: beam type id
            :return: None
            """
            beam_configuration = self.get_beam_configurations(grouping_id)
            assert beam_configuration, (
                f"Beam grouping {grouping_id} does not exist, did you add a beam configuration"
                " by calling `add_beam_configuration'"
            )
            beam_type = beam_configuration.types.get(beam_type_id)
            assert beam_type, (
                f"Beam type {beam_type_id} does not exist, did you add a beam configuration"
                " by calling `add_beam_configuration'"
            )
            return {grouping_id: beam_type}

        assert (
            self._scan_type_configurations.get(config_name) is None
        ), f"configuration {config_name} already exists."
        if isinstance(beams, dict):
            for beam_grouping_id, beam_types in beams.items():
                beam_grouping = self._beam_configurations.get(beam_grouping_id)
                assert beam_grouping, (
                    f"beam configuration {beam_grouping_id} does not exist,"
                    "you first need to create a beam configuration by calling `add_beam_configuration'"
                )
                scan_type_data = {"scan_type_id": config_name}
                if derive_from:
                    scan_type_data["derive_from"] = derive_from

                scan_type_data["beams"] = [BeamMapping(**beam_types)]
                scan_type_obj = ScanTypeSB(**scan_type_data)

            self._scan_type_configurations[config_name] = scan_type_obj
        else:
            if isinstance(beams, tuple):
                grouping_id = beams[0]
                beam_type_id = beams[1]
                agg_beam_types = {
                    **agg_beam_types,
                    **add_beam(grouping_id, beam_type_id),
                }
            else:
                for mapping in beams:
                    grouping_id = mapping[0]
                    beam_type_id = mapping[1]
                    agg_beam_types = {
                        **agg_beam_types,
                        **add_beam(grouping_id, beam_type_id),
                    }

            if derive_from:
                eb_scan_type = EBScanType(config_name, beams=agg_beam_types)
            else:
                eb_scan_type = EBScanType(
                    config_name, beams=agg_beam_types, derive_from=derive_from
                )
            self._scan_type_configurations[config_name] = eb_scan_type

    @property
    def target_spec_scan_types(self):
        """
        Get the target spec scan types
        :return: list of target spec scan types
        """
        return {target.scan_type for target in self.target_specs.values()}

    @property
    def scan_types(self):
        """
        Get the scan types
        :return:  list of scan types
        """
        unique_keys = self.target_spec_scan_types
        return [self._scan_type_configurations[key] for key in unique_keys]

    @property
    def target_spec_beams(self):
        """
        Get the target spec beams
        :return: list of target spec beams
        """
        beams = []
        for scan_type in self.scan_types:
            for beam_X in scan_type.beams:
                beams.append(beam_X.beam_id)
        return set(beams)

    @property
    def beams(self):
        """
        Get the beams
        :return: list of beams
        """
        unique_keys = self.target_spec_beams
        return [
            beam_configuration.configuration
            for beam_configuration in [
                self._beam_configurations.get(key) for key in unique_keys
            ]
            if beam_configuration
        ]

    @property
    def scan_type_configurations(self):
        """
        Get the scan type configurations
        :return: list of scan type configurations
        """
        return list(self._scan_type_configurations.keys())

    def get_scan_type_configuration(self, config_name: str):
        """
        Get the scan type configuration
        :return: ScanTypeConfiguration object
        """
        assert (
            self._scan_type_configurations.get(config_name) is not None
        ), f"configuration {config_name} does not exist."
        return self._scan_type_configurations[config_name]

    @property
    def beam_configurations(self):
        """
        Get the beam configurations
        :return: list of beam configurations
        """
        return list(self._beam_configurations.keys())

    def get_beam_configurations(self, config_name: str):
        """
        Get the beam configurations
        :return: BeamConfiguration object
        """
        assert (
            self._beam_configurations.get(config_name) is not None
        ), f"configuration {config_name} does not exist."
        return self._beam_configurations[config_name]

    @property
    def pending_scan_type_id(self):
        """
        Get the pending scan type
        :return: ScanTypeConfiguration object
        """
        return self._pending_scan_type

    def add_scan_sequence(self, scan_sequence):
        """
        Add a scan sequence
        :return: None
        """
        self.scan_sequence_data.extend(scan_sequence)


class ProcessingSpec(NamedTuple):
    script: ScriptConfiguration
    parameters: dict[Any, Any] = {}

    def __hash__(self):
        return hash(f"{self.script.name}")

DEFAULT_SCRIPT_SB_PDM = Script(
    kind=ScriptKind.REALTIME, name="test-receive-addresses", version="0.7.1"
)

class ProcessingSpecs(TargetSpecs):
    def __init__(
        self,
        additional_processing_specs: list[ProcessingSpec] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the processing specs class
        :param additional_processing_specs: list of additional processing specs
        :param kwargs: keyword arguments
        :param pdm_default_script: Boolean flag to indicate if the default script is PDM
        :return: None
        """
        super().__init__(**kwargs)
        self._processing_specs = {
            "test-receive-addresses": ProcessingSpec(
                script=DEFAULT_SCRIPT_SB_PDM
            )
        }
        if additional_processing_specs is not None:
            self._processing_specs = {
                **self._processing_specs,
                **{
                    processing_spec.script.name: processing_spec
                    for processing_spec in additional_processing_specs
                },
            }

    @property
    def target_processings(self):
        """
        Get the target processings
        :return: set of target processings
        """
        return {target.processing for target in self.target_specs.values()}

    @property
    def processing_scripts(self):
        """
        Get the processing scripts
        :return: list of processing scripts
        """
        unique_keys = self.target_processings
        return [self._processing_specs[key] for key in unique_keys]

    def add_processing_specs(
        self,
        spec_name: str,
        script_version: str,
        script_name: str | None = None,
        script_kind: str = "realtime",
        parameters: dict[Any, Any] | None = None,
    ):
        """
        Add processing specs
        :param spec_name: name of the processing spec
        :param script_version: version of the processing script
        :param script_name: name of the processing script
        :param script_kind: kind of the processing script
        :param parameters: parameters of the processing script
        :return:  None
        """
        assert (
            self._processing_specs.get(spec_name) is None
        ), f"The processing spec {spec_name}already exists"

        if script_name is None:
            script_name = spec_name

        if parameters is None:
            parameters = {}

        script = ScriptConfiguration(
            kind=script_kind, name=script_name, version=script_version
        )
        self._processing_specs[spec_name] = ProcessingSpec(
            script=script, parameters=parameters
        )


class ProcessingBlockSpec(ProcessingSpecs):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the processing block spec class
        :param kwargs: keyword arguments
        :param args: positional arguments
        :return:  None
        """
        super().__init__(*args, **kwargs)
        self.sb_driven = kwargs.get("sb_driven")

    @property
    def processing_blocks(self):
        """
        Get the processing blocks
        """
        sb = load_next_sb()
        self.eb_id = sb.eb
        self.pb_id = sb.pb

        if self.sb_driven:
            return [
                ProcessingBlock(
                    pb_id=self.pb_id,
                    script=processing_script.script,
                    sbi_ids=["sbi" + self.eb_id[2:]],
                    parameters=processing_script.parameters,
                )
                for processing_script in self.processing_scripts
            ]
        else:
            return [
                ProcessingBlockConfiguration(
                    pb_id=self.pb_id,
                    script=processing_script.script,
                    sbi_ids=["sbi" + self.eb_id[2:]],
                    parameters=processing_script.parameters,
                )
                for processing_script in self.processing_scripts
            ]
