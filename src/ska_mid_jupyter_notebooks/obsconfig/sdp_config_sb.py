"""Science data processor configuration stuff with added storage block goodness."""

from typing import Any

from ska_oso_pdm.entities.sdp.sdp_configuration import (  # type: ignore[import-untyped]
    SDPConfiguration,
)

from ska_mid_jupyter_notebooks.obsconfig.base import encoded
from ska_mid_jupyter_notebooks.obsconfig.dishes import Dishes
from ska_mid_jupyter_notebooks.obsconfig.sb import ExecutionBlockSpecsSB
from ska_mid_jupyter_notebooks.obsconfig.sdp_config import ProcessingBlockSpec


# pylint: disable-next=too-many-ancestors
class SdpConfigSpecsSB(Dishes, ExecutionBlockSpecsSB, ProcessingBlockSpec):
    """Store SDP config specs with SB"""

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize SdpConfigSpecsSB class.

        :param kwargs: Keyword arguments
        """
        super().__init__(**kwargs)

    def _generate_sdp_assign_resources_sb_config(self) -> SDPConfiguration:
        """
        Generate the sdp assign resources sb config.

        :return: sdp assign resources sb config
        """
        return SDPConfiguration(
            execution_block=self.execution_block_sb,
            resources=self.resource_configuration,
            processing_blocks=self.processing_blocks,
        )

    @encoded
    def generate_sdp_assign_resources_sb_config(self) -> SDPConfiguration:
        """
        Generate the sdp assign resources sb config.

        :return: SDP assign resource object
        """
        return self._generate_sdp_assign_resources_sb_config()
