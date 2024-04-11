import os
from typing import Any

from ska_tmc_cdm.messages.central_node.sdp import Channel, ChannelConfiguration

from ska_mid_jupyter_notebooks.obsconfig.target_spec import TargetSpecs

DEFAULT_CHANNELS = {
    "vis_channels": ChannelConfiguration(
        channels_id="vis_channels",
        spectral_windows=[
            Channel(
                spectral_window_id="fsp_1_channels",
                count=14880,
                start=0,
                stride=2,
                freq_min=0.35e9,
                freq_max=0.368e9,
                link_map=[[0, 0], [200, 1], [744, 2], [944, 3]],
            )
        ],
    )
}


class Channelisation(TargetSpecs):
    def __init__(
        self,
        additional_channels: list[ChannelConfiguration] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes Channelization class
        :param additional_channels: additional channels to be added
        :param kwargs: keyword arguments
        :return: None
        """
        super().__init__(**kwargs)
        self._channel_configurations = DEFAULT_CHANNELS
        if additional_channels is not None:
            self._channel_configurations = {
                **self._channel_configurations,
                **{
                    additional_channel.channels_id: additional_channel
                    for additional_channel in additional_channels
                },
            }

    def add_channel_configuration(self, config_name: str, spectral_windows: list[Channel]):
        """
        Add channel configuration
        :param config_name: name of the configuration
        :param spectral_windows: list of spectral windows
        :return: None
        """
        assert (
            self._channel_configurations.get(config_name) is None
        ), f"configuration {config_name} already exists."

        self._channel_configurations[config_name] = ChannelConfiguration(
            channels_id=config_name, spectral_windows=spectral_windows
        )

    @property
    def channel_configurations(self) -> list[str]:
        """
        Get the channel configurations
        :return: list of channel configurations
        """
        return list(self._channel_configurations.keys())

    def get_channel_configuration(self, config_name: str) -> ChannelConfiguration:
        """
        Get the channel configuration
        :param config_name: channel name for getting the configuration
        :return: ChannelConfiguration object
        """
        assert (
            self._channel_configurations.get(config_name) is not None
        ), f"configuration {config_name} does not exist."
        return self._channel_configurations[config_name]

    @property
    def target_spec_channels(self):
        """
        Get the target spec channels
        :return: list of target spec channels
        """
        return {target.channelisation for target in self.target_specs.values()}

    @property
    def channels(self) -> list[ChannelConfiguration]:
        """
        Get the channels
        :return: list of channels
        """
        unique_keys = self.target_spec_channels

        return [
            channel_config
            for key in unique_keys
            if (channel_config := self._channel_configurations.get(key)) is not None
        ]
