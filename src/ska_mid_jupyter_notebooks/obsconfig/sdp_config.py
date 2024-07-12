"""Science data processor configuration stuff."""

from typing import Any, Dict, List, NamedTuple, Union

from ska_oso_pdm.entities.sdp import (  # type: ignore[import-untyped]
    BeamMapping,
    ProcessingBlock,
    ScanType,
)
from ska_oso_pdm.entities.sdp.beam import Beam, BeamFunction  # type: ignore[import-untyped]
from ska_oso_pdm.entities.sdp.processing_block import (  # type: ignore[import-untyped]
    Script,
    ScriptKind,
)
from ska_tmc_cdm.messages.central_node.sdp import (  # type: ignore[import-untyped]
    BeamConfiguration,
    EBScanType,
    EBScanTypeBeam,
    PolarisationConfiguration,
    ScriptConfiguration,
)

from ska_mid_jupyter_notebooks.obsconfig.base import load_next_sb
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpecs


class Beamgrouping(NamedTuple):
    """Store beam grouping data."""

    id: str
    configuration: BeamConfiguration
    types: dict[str, EBScanTypeBeam]


class BeamgroupingSB(NamedTuple):
    """Store beam grouping SB data."""

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


def default_scan_types_sb(owner: "ScanTypes") -> Dict[str, ScanType]:
    """
    Returns the default scan types.

    :param owner: ScanTypes object
    :return: Default scan types dictionary for SB
    """
    scan_type_details = {  # list of beam mappiing
        ".default": ScanType(
            scan_type_id=".default",
            beams=[
                owner.get_beam_configurations("vis0").types["default_beam_type"],
            ],
        ),
        "bandpass calibrator": ScanType(
            scan_type_id="bandpass calibrator",
            beams=[owner.get_beam_configurations("vis0").types["default_beam_type"]],
            derive_from=".default",
        ),
        "Polaris Australis": ScanType(
            scan_type_id="Polaris Australis",
            beams=[owner.get_beam_configurations("vis0").types["polaris_australis_beam_type"]],
            derive_from=".default",
        ),
        "M85": ScanType(
            scan_type_id="M85",
            beams=[owner.get_beam_configurations("vis0").types["default_beam_type"]],
            derive_from=".default",
        ),
    }
    return scan_type_details


DEFAULT_SCAN_SEQUENCE_LIST = ["Polaris Australis"]


class ScanTypes(TargetSpecs):
    """Store scan types here."""

    def __init__(
        self,
        additional_beam_groupings: Union[list[Beamgrouping], list[BeamgroupingSB]] | None = None,
        additional_scan_types: Union[list[EBScanType], list[ScanType]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize ScanTypes class.

        :param additional_beam_groupings: list of Beamgrouping or BeamgroupingSB
        :param additional_scan_types: list of EBScanType or ScanType
        :param **kwargs: Any
        :return: None
        """
        super().__init__(**kwargs)

        self._beam_configurations: Any = DEFAULT_BEAMS_SB
        self._scan_type_configurations: dict[str, ScanType] = default_scan_types_sb(self)

        self.scan_sequence_data = DEFAULT_SCAN_SEQUENCE_LIST

        if additional_beam_groupings is not None:
            self._beam_configurations = {
                **self._beam_configurations,
                **{beam_grouping.id: beam_grouping for beam_grouping in additional_beam_groupings},
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

    # pylint: disable-next=dangerous-default-value,too-many-arguments
    def add_beam_configuration(
        self,
        config_name: str,
        function: Union[str, BeamFunction],
        # beam_types: dict[str, Union[EBScanTypeBeam, ScanType]] | None = None,
        beam_types: dict[str, Any | Any] = {},
        search_beam_id: int | None = None,
        timing_beam_id: int | None = None,
        vlbi_beam_id: int | None = None,
    ) -> None:
        """
        Add a beam configuration
        :param config_name: name of the beam configuration
        :param function: beam function
        :param beam_types: beam types
        :param search_beam_id: search beam id
        :param timing_beam_id: timing beam id
        :param vlbi_beam_id: vlbi beam id
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
        beam_types: dict[str, Union[EBScanTypeBeam, ScanType]],
    ) -> None:
        """
        Add beam types.

        :param grouping_id: grouping id
        :param beam_types: type of beam
        """
        assert self._beam_configurations.get(
            grouping_id
        ), f"grouping {grouping_id} does not exist, did you call `add_beam_configuration()`."
        current_beam_types = self._beam_configurations[grouping_id].types
        current_beam_configuration = self._beam_configurations[grouping_id].configuration
        self._beam_configurations[grouping_id] = Beamgrouping(
            grouping_id,
            current_beam_configuration,
            {**current_beam_types, **beam_types},
        )

    def add_scan_type_configuration(
        self,
        config_name: str,
        beams: dict[str, dict[str, BeamMapping]],
        derive_from: str | None = None,
    ) -> None:
        """
        Add a scan type configuration.

        :param config_name: name of scan_type configuration
        :param beams: beams
        :param derive_from: derive from
        """
        agg_beam_types: dict[str, Union[EBScanTypeBeam, ScanType]] = {}

        def add_beam(grouping_id: str, beam_type_id: str) -> dict:
            """
            Add a beam
            :param grouping_id: grouping id
            :param beam_type_id: beam type id
            :return: dictionary
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
            # TODO this is evil genius stuff
            beam_types: list | dict
            for beam_grouping_id, beam_types in beams.items():
                beam_grouping = self._beam_configurations.get(beam_grouping_id)
                assert beam_grouping, (
                    f"beam configuration {beam_grouping_id} does not exist,"
                    "you first need to create a beam configuration by calling"
                    " cat `add_beam_configuration'"
                )
                scan_type_data = {"scan_type_id": config_name}
                if derive_from:
                    scan_type_data["derive_from"] = derive_from
                if isinstance(beam_types, BeamMapping):
                    beam_types = [beam_types]
                scan_type_data["beams"] = beam_types
                scan_type_obj = ScanType(**scan_type_data)

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
                eb_scan_type = EBScanType(
                    config_name, beams=agg_beam_types, derive_from=derive_from
                )
            else:
                eb_scan_type = EBScanType(config_name, beams=agg_beam_types)
            self._scan_type_configurations[config_name] = eb_scan_type

    @property
    def target_spec_scan_types(self) -> set:
        """
        Get the target spec scan types.

        :return: list of target spec scan types
        """
        return {target.scan_type for target in self.target_specs.values()}

    @property
    def scan_types(self) -> List[ScanType]:
        """
        Get the scan types.

        :return:  list of scan types
        """
        unique_keys = self.target_spec_scan_types
        return [self._scan_type_configurations[key] for key in unique_keys]

    @property
    def target_spec_beams(self) -> set:
        """
        Get the target spec beams.

        :return: list of target spec beams
        """
        beams = []
        for scan_type in self.scan_types:
            for beam_x in scan_type.beams:
                beams.append(beam_x.beam_id)
        return set(beams)

    @property
    def beams(self) -> list:
        """
        Get the beams.

        :return: list of beams
        """
        unique_keys = self.target_spec_beams
        return [
            beam_configuration.configuration
            for beam_configuration in [self._beam_configurations.get(key) for key in unique_keys]
            if beam_configuration
        ]

    @property
    def scan_type_configurations(self) -> list:
        """
        Get the scan type configurations.

        :return: list of scan type configurations
        """
        return list(self._scan_type_configurations.keys())

    def get_scan_type_configuration(self, config_name: str) -> Any:
        """
        Get the scan type configuration.

        :return: ScanTypeConfiguration object
        """
        # TODO where is ScanTypeConfiguration defined?
        assert (
            self._scan_type_configurations.get(config_name) is not None
        ), f"configuration {config_name} does not exist."
        return self._scan_type_configurations[config_name]

    @property
    def beam_configurations(self) -> list:
        """
        Get the beam configurations.

        :return: list of beam configurations
        """
        return list(self._beam_configurations.keys())

    def get_beam_configurations(self, config_name: str) -> BeamConfiguration:
        """
        Get the beam configurations
        :return: BeamConfiguration object
        """
        assert (
            self._beam_configurations.get(config_name) is not None
        ), f"configuration {config_name} does not exist."
        return self._beam_configurations[config_name]

    @property
    def pending_scan_type_id(self) -> Any:
        """
        Get the pending scan type.

        :return: ScanTypeConfiguration object
        """
        # TODO where is ScanTypeConfiguration defined?
        return self._pending_scan_type

    def add_scan_sequence(self, scan_sequence: Any) -> None:
        """
        Add a scan sequence
        :return: None
        """
        self.scan_sequence_data.extend(scan_sequence)


class ProcessingSpec(NamedTuple):
    """Store processing specification."""

    script: ScriptConfiguration
    parameters: dict[Any, Any] = {}

    def __hash__(self) -> int:
        """
        Do a hash bash.

        :return: hash of script name
        """
        return hash(f"{self.script.name}")


DEFAULT_SCRIPT_SB_PDM = Script(
    kind=ScriptKind.REALTIME, name="test-receive-addresses", version="0.7.1"
)


class ProcessingSpecs(TargetSpecs):
    """Store processing specification for target."""

    def __init__(
        self,
        additional_processing_specs: list[ProcessingSpec] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the processing specs class.

        :param additional_processing_specs: list of additional processing specs
        :param kwargs: keyword arguments
        """
        super().__init__(**kwargs)
        self._processing_specs = {
            "test-receive-addresses": ProcessingSpec(script=DEFAULT_SCRIPT_SB_PDM)
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
    def target_processings(self) -> set:
        """
        Get the target processings.

        :return: set of target processings
        """
        return {target.processing for target in self.target_specs.values()}

    @property
    def processing_scripts(self) -> list:
        """
        Get the processing scripts.

        :return: list of processing scripts
        """
        unique_keys = self.target_processings
        return [self._processing_specs[key] for key in unique_keys]

    # pylint: disable-next=too-many-arguments
    def add_processing_specs(
        self,
        spec_name: str,
        script_version: str,
        script_name: str | None = None,
        script_kind: str = "realtime",
        parameters: dict[Any, Any] | None = None,
    ) -> None:
        """
        Add a processing spec.

        :param spec_name: name of the processing spec
        :param script_version: version of the processing script
        :param script_name: name of the processing script
        :param script_kind: kind of the processing script
        :param parameters: parameters of the processing script
        """
        assert (
            self._processing_specs.get(spec_name) is None
        ), f"The processing spec {spec_name}already exists"

        if script_name is None:
            script_name = spec_name

        if parameters is None:
            parameters = {}

        script = ScriptConfiguration(kind=script_kind, name=script_name, version=script_version)
        self._processing_specs[spec_name] = ProcessingSpec(script=script, parameters=parameters)


class ProcessingBlockSpec(ProcessingSpecs):
    """Processing block specifications."""

    @property
    def processing_blocks(self) -> list:
        """
        Get the processing blocks.

        :return: list of processing blocks
        """
        next_sb = load_next_sb()
        self.eb_id = next_sb.eb
        self.pb_id = next_sb.pb

        return [
            ProcessingBlock(
                pb_id=self.pb_id,
                script=processing_script.script,
                sbi_ids=["sbi" + self.eb_id[2:]],
                parameters=processing_script.parameters,
            )
            for processing_script in self.processing_scripts
        ]


DEFAULT_POLARISATIONS = {
    "all": PolarisationConfiguration(polarisations_id="all", corr_type=["XX", "XY", "YX", "YY"])
}


class Polarisations(TargetSpecs):
    """Store polarisations here."""

    def __init__(
        self,
        additional_polarizations: list[PolarisationConfiguration] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the polarisations class.

        :param additional_polarizations: list of additional polarisations
        :param kwargs: keyword arguments
        """
        super().__init__(**kwargs)

        self.polarizations = DEFAULT_POLARISATIONS
        if additional_polarizations is not None:
            self.polarizations = {
                **self.polarizations,
                **{
                    additional_polarization.polarisations_id: additional_polarization
                    for additional_polarization in additional_polarizations
                },
            }

    def get_polarisations_from_target_specs(self) -> list:
        """
        Get the polarisations.

        :return: list of polarisations
        """
        unique_keys: set = {target.polarisation for target in self.target_specs.values()}
        return [self.polarizations[key] for key in unique_keys]
