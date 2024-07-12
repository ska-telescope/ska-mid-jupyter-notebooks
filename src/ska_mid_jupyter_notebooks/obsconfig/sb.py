"""Storage block stuff."""

from datetime import datetime, timedelta, timezone
from typing import Any

from ska_oso_pdm.entities.common.procedures import (  # type: ignore[import-untyped]
    FilesystemScript,
    GitScript,
    PythonArguments,
)
from ska_oso_pdm.entities.common.sb_definition import MetaData  # type: ignore[import-untyped]
from ska_oso_pdm.entities.common.scan_definition import (  # type: ignore[import-untyped]
    ScanDefinition,
)
from ska_oso_pdm.entities.sdp.execution_block import ExecutionBlock  # type: ignore[import-untyped]
from ska_oso_pdm.entities.sdp.scan_type import BeamMapping  # type: ignore[import-untyped]

from ska_mid_jupyter_notebooks.obsconfig.base import encoded, load_next_sb
from ska_mid_jupyter_notebooks.obsconfig.channelisation import Channelisation
from ska_mid_jupyter_notebooks.obsconfig.sdp_config import Polarisations, ScanTypes
from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpecs

DEFAULT_SCAN_TYPE = [
    {
        "scan_type_id": ".default",
        "beams": [
            {
                "beam_id": "vis0",
                "channels_id": "vis_channels",
                "polarisations_id": "all",
            },
            {
                "beam_id": "pss1",
                "field_id": "M83",
                "channels_id": "pulsar_channels",
                "polarisations_id": "all",
            },
            {
                "beam_id": "pss2",
                "field_id": "Polaris Australis",
                "channels_id": "pulsar_channels",
                "polarisations_id": "all",
            },
            {
                "beam_id": "pst1",
                "field_id": "M83",
                "channels_id": "pulsar_channels",
                "polarisations_id": "all",
            },
            {
                "beam_id": "pst2",
                "field_id": "Polaris Australis",
                "channels_id": "pulsar_channels",
                "polarisations_id": "all",
            },
            {
                "beam_id": "vlbi",
                "field_id": "Polaris Australis",
                "channels_id": "vlbi_channels",
                "polarisations_id": "all",
            },
        ],
    },
    {
        "scan_type_id": "bandpass calibrator",
        "derive_from": ".default",
        "beams": [{"beam_id": "vis0", "field_id": "M83"}],
    },
]

DEFAULT_SCAN_SEQUENCE_LIST = ["Polaris Australis"]


# pylint: disable-next=too-few-public-methods
class ScanDefinitionSB:
    """Definition of scan storage block."""

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        scan_definition_id: str = "Polaris Australis",
        scan_duration: int = 10,
        target_id: str = "Polaris Australis",
        scan_type_id: str = "Polaris Australis",
        dish_configuration_id: str = "dish config 123",
        csp_configuration_id: str = "sbi-mvp01-20200325-00001-science_A",
    ) -> None:
        """
        Initialize a new instance of the ScanClass.

        :param scan_definition_id: ID of the scan definition.
        :param scan_duration: Duration of the scan in seconds.
        :param target_id: ID of the target.
        :param scan_type_id: ID of the scan type.
        :param dish_configuration_id: ID of the dish configuration.
        :param csp_configuration_id: ID of the CSP configuration.
        """

        self.scan_definition_id = scan_definition_id
        self.scan_duration = timedelta(seconds=scan_duration)
        self.target_id = target_id
        self.dish_configuration_id = dish_configuration_id
        self.scan_type_id = scan_type_id
        self.csp_configuration_id = csp_configuration_id

    def get_scan_definition(self) -> ScanDefinition:
        """
        Generate Scan Definition Block.

        :return: ScanDefinition object
        """
        return ScanDefinition(
            scan_definition_id=self.scan_definition_id,
            scan_duration=self.scan_duration,
            target_id=self.target_id,
            dish_configuration_id=self.dish_configuration_id,
            scan_type_id=self.scan_type_id,
            csp_configuration_id=self.csp_configuration_id,
        )


# pylint: disable-next=too-few-public-methods
class BeamMappingSB:
    """Storage block for beam mapping."""

    def __init__(self, beams: Any) -> None:
        """
        Initialize a new instance of the BeamMappingSB class.

        :param beams (list): A list of dictionaries representing beam data.
        """
        self.beams = beams

    def _get_beam_mapping(self) -> list:
        """
        Private method to transform raw beam data into a list of BeamMapping objects.

        :return: list of BeamMapping objects
        """
        beams_list = []
        for beam_data in self.beams:
            beams_list.append(
                BeamMapping(
                    beam_id=beam_data.get("beam_id", None),
                    field_id=beam_data.get("field_id", None),
                    channels_id=beam_data.get("channels_id", None),
                    polarisations_id=beam_data.get("polarisations_id", None),
                )
            )
        return beams_list

    def get_beam_mapping(self) -> list:
        """
        Get the list of BeamMapping objects based on the provided beam data.

        :return: list of BeamMapping objects
        """
        return self._get_beam_mapping()


class MetaDataSB(TargetSpecs):
    """Metadata for storage block."""

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        version: int = 1,
        created_on: datetime = datetime.now(timezone.utc),
        created_by: str = "test_user",
        last_modified_on: datetime = datetime.now(timezone.utc),
        last_modified_by: str = "test_user",
        **kwargs: Any,
    ) -> None:
        """
        Initialise a new instance of the MetaDataSB class.

        :param version: The version of the metadata.
        :param created_on: The date and time when the metadata was created.
        :param created_by: The user who created the metadata.
        :param last_modified_on: The date and time when the metadata was last modified.
        :param last_modified_by: The user who last modified the metadata.
        """

        super().__init__(**kwargs)
        self.version = version
        self.created_on = created_on
        self.created_by = created_by
        self.last_modified_on = last_modified_on
        self.last_modified_by = last_modified_by

    def _get_metadata(self) -> MetaData:
        """
        Private method to create a MetaData object based on the current instance's attributes.
        :return: MetaData object
        """
        return MetaData(
            version=self.version,
            created_on=self.created_on,
            created_by=self.created_by,
            last_modified_on=self.last_modified_on,
            last_modified_by=self.last_modified_by,
        )

    @encoded
    def get_metadata(self) -> MetaData:
        """
        Get the encoded representation of the metadata.

        :return: MetaData object
        """
        return self._get_metadata()


class ExecutionBlockSpecsSB(ScanTypes, Channelisation, Polarisations):
    """Execution block specs for SB."""

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        context: dict[Any, Any] | None = None,
        max_length: float = 3600.0,
        eb_id: str | None = None,
        target_specs: dict[Any, Any] | None = None,
        additional_channels: Any = None,
        additional_polarizations: Any = None,
        additional_scan_types: Any = None,
        **kwargs: Any,
    ) -> None:
        """
        Generate Execution BLock- for SB.

        :param context: Additional context information
        :param max_length: The maximum length of the execution block in seconds
        :param eb_id: The ID of the execution block
        :param target_specs: Additional target specifications
        :param additional_channels: Additional channels for the execution block.
        :param additional_polarizations: Additional polarizations for the execution block.
        :param additional_scan_types: Additional scan types for the execution block.
        """
        super().__init__(
            target_specs=target_specs,
            additional_channels=additional_channels,
            additional_polarizations=additional_polarizations,
            additional_scan_types=additional_scan_types,
            **kwargs,
        )
        if context is None:
            context = {}
        self._context = context
        self._max_length = max_length
        self.eb_id: str = str(eb_id)

    @property
    def execution_block_sb(self) -> ExecutionBlock:
        """
        Get the execution block based on the specifications provided For SB.
        :return: ExecutionBlock object
        """
        context = self._context
        max_length = self._max_length
        scan_types = self.scan_types
        beams = self.beams

        channels = self.channels
        polarisations = self.get_polarisations_from_target_specs()
        next_sb = load_next_sb()
        return ExecutionBlock(
            eb_id=next_sb.eb,
            context=context,
            max_length=max_length,
            beams=beams,
            scan_types=scan_types,
            channels=channels,
            polarisations=polarisations,
        )


# pylint: disable-next=too-many-instance-attributes
class ActivitiesSB:
    """Storage block for activities."""

    # pylint: disable-next=dangerous-default-value,too-many-arguments
    def __init__(
        self,
        allocate_path: str = "git://scripts/allocate_from_file_mid_sb.py",
        allocate_repo: str = "https://gitlab.com/ska-telescope/oso/ska-oso-scripting.git",
        allocate_branch: str = "nak-710-jupyter-scripts",
        allocate_function_args_init: dict = {},
        allocate_function_args_main: dict = {},
        allocate_commit: Any = None,
        observe_path: str = "git://scripts/observe_mid_sb.py",
        observe_repo: str = "https://gitlab.com/ska-telescope/oso/ska-oso-scripting.git",
        observe_branch: str = "nak-710-jupyter-scripts",
        observe_commit: Any = None,
        observe_function_args_init: dict = {},
        observe_function_args_main: dict = {},
    ) -> None:
        """
        Initialize a new instance of the ActivitiesSB class.

        :param allocate_path: The path to the allocation script.
        :param allocate_repo: The repository URL for the allocation script.
        :param allocate_branch: The branch of the allocation script repository.
        :param allocate_commit: The commit ID of the allocation script repository.
        :param allocate_function_args_init: Initialization arguments for the allocation script.
        :param allocate_function_args_main: Main function arguments for the allocation script.
        :param observe_path: The path to the observation script.
        :param observe_repo: The repository URL for the observation script.
        :param observe_branch: The branch of the observation script repository.
        :param observe_commit: The commit ID of the observation script repository.
        :param observe_function_args_init: Initialization arguments for the observation script.
        :param observe_function_args_main: Main function arguments for the observation script.
        """
        default_arguments_init: dict = {
            "args": [],
            "kwargs": {"subarray_id": 1},
        }

        default_arguments_main: dict = {
            "args": [],
            "kwargs": {},
        }
        self.allocate_function_args_init: dict = (
            default_arguments_init
            if not allocate_function_args_init
            else allocate_function_args_init
        )
        self.allocate_function_args_main: dict = (
            default_arguments_main
            if not allocate_function_args_main
            else allocate_function_args_main
        )
        self.observe_function_args_init: dict = (
            default_arguments_init
            if not observe_function_args_init
            else observe_function_args_init
        )
        self.observe_function_args_main: dict = (
            default_arguments_main
            if not observe_function_args_main
            else observe_function_args_main
        )

        self.allocate_path: str = allocate_path
        self.allocate_repo: str = allocate_repo
        self.allocate_branch: str = allocate_branch
        self.allocate_commit: Any = allocate_commit
        self.observe_path: str = observe_path
        self.observe_repo: str = observe_repo
        self.observe_branch: str = observe_branch
        self.observe_commit: Any = observe_commit

    def add_activities_parameters(self, activities_params: dict) -> None:
        """
        Modify ActivitySB Instance parameters.

        :param activities_params: Dictionary of parameters to be modified
        """
        for key, value in activities_params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"'ActivitiesSB' object has no attribute '{key}'")

    def get_activities(self) -> dict:
        """
        Get the allocation and observation activities.

        :return: List of activities
        """
        allocate_function_args = {
            "init": PythonArguments(
                args=self.allocate_function_args_init["args"],
                kwargs=self.allocate_function_args_init["kwargs"],
            ),
            "main": PythonArguments(
                args=self.allocate_function_args_main["args"],
                kwargs=self.allocate_function_args_main["kwargs"],
            ),
        }
        observe_function_args = {
            "init": PythonArguments(
                args=self.observe_function_args_init["args"],
                kwargs=self.observe_function_args_init["kwargs"],
            ),
            "main": PythonArguments(
                args=self.observe_function_args_main["args"],
                kwargs=self.observe_function_args_main["kwargs"],
            ),
        }

        allocate_obj = (
            FilesystemScript(path=self.allocate_path, function_args=allocate_function_args)
            if not self.allocate_repo
            else GitScript(
                repo=self.allocate_repo,
                path=self.allocate_path,
                branch=self.allocate_branch,
                commit=self.allocate_commit,
                function_args=allocate_function_args,
            )
        )
        observe_obj = (
            FilesystemScript(path=self.observe_path, function_args=observe_function_args)
            if not self.observe_repo
            else GitScript(
                repo=self.observe_repo,
                path=self.observe_path,
                branch=self.observe_branch,
                commit=self.observe_commit,
                function_args=observe_function_args,
            )
        )
        return {"allocate": allocate_obj, "observe": observe_obj}
