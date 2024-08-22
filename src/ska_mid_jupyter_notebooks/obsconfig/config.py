from ska_oso_pdm.common.sb_definition import SBD_SCHEMA_URI, SBDefinition, TelescopeType
from ska_oso_pdm.common.scan_definition import ScanDefinition
from ska_oso_pdm.dish.dish_configuration import DishConfiguration
from ska_oso_pdm.schemas import CODEC as pdm_CODEC
from ska_oso_pdm.schemas.common.sb_definition import SBDefinitionSchema
from ska_oso_scripting.functions import pdm_transforms
from ska_tmc_cdm.messages.central_node.assign_resources import AssignResourcesRequest
from ska_tmc_cdm.messages.central_node.common import DishAllocation as cdm_DishAllocation
from ska_tmc_cdm.messages.central_node.csp import CSPConfiguration as CentralCSPConfiguration
from ska_tmc_cdm.messages.subarray_node.configure import ConfigureRequest

from ska_mid_jupyter_notebooks.obsconfig.base import encoded
from ska_mid_jupyter_notebooks.obsconfig.csp import CSPconfig
from ska_mid_jupyter_notebooks.obsconfig.dishes import Dishes
from ska_mid_jupyter_notebooks.obsconfig.sb import ActivitiesSB, MetaDataSB, ScanDefinitionSB
from ska_mid_jupyter_notebooks.obsconfig.sdp_config_sb import SdpConfigSpecsSB
from ska_mid_jupyter_notebooks.obsconfig.tmc_config import TMCConfig

# pylint: disable=E1101


class ObservationSB(SdpConfigSpecsSB, MetaDataSB, Dishes, CSPconfig, TMCConfig, ActivitiesSB):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ActivitiesSB.__init__(self)

    assign_resources_schema = "https://schema.skao.int/ska-tmc-assignresources/2.1"
    config_resources_schema = "https://schema.skao.int/ska-tmc-configure/2.2"
    sdp_schema = "https://schema.skao.int/ska-sdp-configure/0.4"
    transaction_id = "txn-....-00001"

    def generate_pdm_object(
        self,
        csp_configuration: list[CentralCSPConfiguration],
        scan_configuration: list[ScanDefinition],
        dish_configurations: list[DishConfiguration],
    ) -> SBDefinition:
        """
        Generates Scheduling Block Definition instance based on below configuration details recieved
        :param: csp_configuration: List of CSP configuration
        :param: scan_configuration: List of Scan definition
        :param: dish_configurations: List of  DishConfiguration
        :return: Scheduling Block Definition
        """
        sdp_configuration = self.generate_sdp_assign_resources_sb_config().as_object
        sb_specs = SBDefinition(
            interface=SBD_SCHEMA_URI,
            telescope=TelescopeType.MID,
            metadata=self.get_metadata().as_object,
            activities=self.get_activities(),
            sdp_configuration=sdp_configuration,
            dish_allocations=self.dish_allocation,
            targets=self.targets,
            csp_configurations=csp_configuration,
            scan_sequence=(
                self.scan_sequence_data[1:]
                if len(self.scan_sequence_data) > 1
                else self.scan_sequence_data
            ),
            scan_definitions=scan_configuration,
            dish_configurations=dish_configurations,
        )

        sb = SBDefinitionSchema().dumps(sb_specs)
        pdm_request: SBDefinition = pdm_CODEC.loads(SBDefinition, sb)
        return pdm_request

    def generate_pdm_object_for_sbd_save(self, DEFAULT_TARGET_SPECS: dict = None) -> SBDefinition:
        """
        Generates CSP, DISH,Scan Definition configuration based on the Target SPec data provided and creates an SBD
        :param: DEFAULT_TARGET_SPECS : Target Spec details
        :return: Scheduling Block Definition
        """
        configure_request = []
        if not DEFAULT_TARGET_SPECS:
            default_target_specs = self.target_specs
        else:
            default_target_specs = DEFAULT_TARGET_SPECS

        for key, value in default_target_specs.items():
            configure_request.append(
                {
                    "scan_definition_id": key,
                    "target_id": key,
                    "scan_type_id": value.scan_type,
                    "scan_duration": value.scan_duration,
                }
            )
        csp_configuration = []
        scan_configuration = []
        dish_configurations = []
        for data in configure_request:
            csp_configuration.append(
                self.generate_csp_scan_config(
                    target_id=data["target_id"], sb_target_flag=True
                ).as_object
            )
            # this condition is used for creating configure request object

            scan_configuration.append(
                ScanDefinitionSB(
                    data["scan_definition_id"],
                    data["scan_duration"],
                    data["target_id"],
                    data["scan_type_id"],
                ).get_scan_definition(),
            )
            # this condition is used for creating configure request object

            dish_configurations.append(self.get_dish_configuration_sb(data["target_id"]))

        pdm_allocation = self.generate_pdm_object(
            csp_configuration, scan_configuration, dish_configurations
        )
        return pdm_allocation

    def convert_pdm_allocate_request_to_cdm(
        self, pdm_request: SBDefinition, cdm_request: AssignResourcesRequest
    ) -> AssignResourcesRequest:
        """
        Transforms PDM Allocate request to CDM
        :param: pdm_request: SBDefinition Instance
        :param: cdm_request: AssignResourcesRequest Instance
        :return: AssignResourcesRequest
        """

        # Configure PDM DishAllocation to the equivalent CDM DishAllocation
        pdm_dish = pdm_request.dish_allocations
        cdm_dish = cdm_DishAllocation(receptor_ids=pdm_dish.receptor_ids)

        # Transform pdm sdp to cdm sdp configuration
        pdm_sdp_config = pdm_request.sdp_configuration
        cdm_sdp_config = pdm_transforms.convert_sdpconfiguration_centralnode(
            pdm_sdp_config, pdm_request.targets
        )

        cdm_request.dish = cdm_dish
        cdm_request.sdp_config = cdm_sdp_config

        return cdm_request

    def _generate_cdm_allocate_config(
        self, pdm_allocation_request: SBDefinition, subarray_id: int = 1
    ) -> AssignResourcesRequest:
        """
        Generates CDM Allocation Request
        :param: pdm_allocation_request: SBDefinition Instance
        :param: subarray_id: Subarray ID
        :return: AssignResourcesRequest
        """

        pdm_allocation_request.sdp_configuration.processing_blocks[0].sbi_ids[0] = (
            "sbi" + pdm_allocation_request.sbd_id[3:]
        )
        cdm_allocation_request = AssignResourcesRequest(
            subarray_id=subarray_id,
            interface=self.assign_resources_schema,
            transaction_id=self.transaction_id,
        )
        # PDM to CDM conversion
        cdm_converted = self.convert_pdm_allocate_request_to_cdm(
            pdm_request=pdm_allocation_request,
            cdm_request=cdm_allocation_request,
        )

        return cdm_converted

    @encoded
    def generate_allocate_config_sb(
        self, pdm_allocation_request: SBDefinition
    ) -> AssignResourcesRequest:
        """
        Generates CDM Allocation Request by calling _generate_cdm_allocate_config and can return in object or json format as needed
        :param: pdm_allocation_request: SBDefinition Instance
        :return:  AssignResourcesRequest
        """
        return self._generate_cdm_allocate_config(pdm_allocation_request)

    def convert_pdm_observation_request_to_cdm(
        self,
        pdm_config: SBDefinition,
        cdm_config: ConfigureRequest,
        scan_definition,
    ) -> ConfigureRequest:
        """Transforms PDM Observation request to CDM for configure resource
        :param: pdm_config: SBDefinition Instance
        :param: cdm_config: ConfigureRequest Instance
        :param: scan_definition : Scan Definition instance
        :return: ConfigureRequest
        """

        scan_definitions = {
            scan_definition.scan_definition_id: scan_definition
            for scan_definition in pdm_config.scan_definitions
        }

        dish_configurations = {
            dish_configuration.dish_configuration_id: dish_configuration
            for dish_configuration in pdm_config.dish_configurations
        }

        csp_configurations = {
            csp_configuration.config_id: csp_configuration
            for csp_configuration in pdm_config.csp_configurations
        }

        targets = {target.target_id: target for target in pdm_config.targets}

        scan_definition = scan_definitions[scan_definition]
        target = targets[scan_definition.target_id]

        cdm_config.pointing = pdm_transforms.convert_pointingconfiguration(
            target, scan_definition.pointing_correction
        )

        dish_configuration = dish_configurations[scan_definition.dish_configuration_id]
        cdm_config.dish = pdm_transforms.convert_dishconfiguration(dish_configuration)

        pdm_cspconfiguration = csp_configurations[scan_definition.csp_configuration_id]
        cdm_config.csp = pdm_transforms.convert_cspconfiguration(
            pdm_cspconfiguration, cdm_config.dish.receiver_band
        )

        # workaround against pdm transform for SDP
        cdm_config.sdp = pdm_transforms.convert_sdpconfiguration_subarraynode(scan_definition)
        cdm_config.sdp.interface = self.sdp_schema
        return cdm_config

    def _generate_cdm_observation_config(
        self,
        scan_definition_id: str = None,
        scan_duration: float = None,
        pdm_observation_request: SBDefinition = None,
    ) -> ConfigureRequest:
        """
        Generates CDM Observation request from PDM Observation request
        :param: scan_definition_id: Scan definition ID
        :param: scan_duration: Duration of Scan
        :param: pdm_observation_request: SBDefinition Instance
        :return: ConfigureRequest
        """
        cdm_observation_request = ConfigureRequest(
            interface=self.config_resources_schema,
            transaction_id=self.transaction_id,
            tmc=self.generate_tmc_scan_config(scan_duration),
        )

        cdm_transformed = self.convert_pdm_observation_request_to_cdm(
            pdm_config=pdm_observation_request,
            cdm_config=cdm_observation_request,
            scan_definition=scan_definition_id,
        )
        return cdm_transformed

    @encoded
    def generate_scan_config_sb(
        self,
        pdm_observation_request: SBDefinition,
        scan_definition_id="flux calibrator",
        scan_duration: float = 10.0,
    ) -> ConfigureRequest:
        """
        Generates CDM SCAN  Request by calling _generate_cdm_observation_config and can return in object or json format as needed
        :param: pdm_observation_request: SBDefinition Instance
        :param: scan_definition_id: Scan definition ID
        :param: scan_duration: Duration of Scan
        :return: ConfigureRequest
        """
        return self._generate_cdm_observation_config(
            scan_definition_id=scan_definition_id,
            scan_duration=scan_duration,
            pdm_observation_request=pdm_observation_request,
        )
