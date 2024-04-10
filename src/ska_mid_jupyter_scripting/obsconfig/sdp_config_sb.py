from typing import Any

from ska_mid_jupyter_scripting.obsconfig.base import encoded
from ska_mid_jupyter_scripting.obsconfig.dishes import Dishes
from ska_mid_jupyter_scripting.obsconfig.sb import ExecutionBlockSpecsSB
from ska_oso_pdm.entities.sdp.sdp_configuration import SDPConfiguration


class SdpConfigSpecsSB(Dishes, ExecutionBlockSpecsSB, ProcessingBlockSpec):
    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes SdpConfigSpecsSB class
        :param kwargs: Keyword arguments
        """
        super().__init__(pdm_default_script=True, **kwargs)

    def _generate_sdp_assign_resources_sb_config(self):
        """
        Generates the sdp assign resources sb config
        :return: sdp assign resources sb config
        """
        return SDPConfiguration(
            execution_block=self.execution_block_sb,
            resources=self.resource_configuration,
            processing_blocks=self.processing_blocks,
        )

    @encoded
    def generate_sdp_assign_resources_sb_config(self):
        """
        Generates the sdp assign resources sb config by calling _generate_sdp_assign_resources_sb_config
        :return: SDP assign resource object
        """
        return self._generate_sdp_assign_resources_sb_config()
