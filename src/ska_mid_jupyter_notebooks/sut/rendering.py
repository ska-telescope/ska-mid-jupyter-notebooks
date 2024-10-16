# pylint: disable=C,R
from typing import Literal, OrderedDict

from ska_mid_jupyter_notebooks.monitoring.rendering import (
    BoxLabels,
    Colours,
    ItemStates,
    MonitorPlot,
)
from ska_mid_jupyter_notebooks.sut.state import (
    SubarrayConfigurationState,
    SubarrayResourceState,
    SubarrayScanningState,
)


class TelescopeMononitorPlot(MonitorPlot[BoxLabels, ItemStates]):
    _items = OrderedDict[BoxLabels, ItemStates](
        {
            "On/Off": "DISABLED",
            "Resources Assigned?": "DISABLED",
            "Subarray Configured?": "DISABLED",
            "Subarray Scanning?": "DISABLED",
        }
    )

    _state_mapping_to_clr: dict[ItemStates, Colours] = {
        "DISABLED": "darkmagenta",
        "BUSY": "yellow",
        "ACTIVE": "forestgreen",
        "OFFLINE": "pink",
    }

    def __init__(self, plot_width: int, plot_height: int) -> None:
        """
        Initialises TelescopeMononitorPlot class
        :param plot_width: width of the plot
        :param plot_height: height of the plot
        :return: None
        """
        super().__init__(plot_width, plot_height, self._items, self._state_mapping_to_clr)
        self.on_off_state: Literal["ON", "OFF", "OFFLINE"] = "OFF"
        self.resourcing_state: SubarrayResourceState = "EMPTY"
        self.configuration_state: SubarrayConfigurationState = "NOT_CONFIGURED"
        self.scanning_state: SubarrayScanningState = "NOT_SCANNING"

    def set_resources_assigning(self):
        """
        Set resources assigning state
        :return: None
        """
        self._set_box("Resources Assigned?", "BUSY")
        self.resourcing_state = "RESOURCING"

    def set_resources_assigned(self):
        """
        Set resources assigned state
        :return: None
        """
        self._set_box("Resources Assigned?", "ACTIVE")
        self.resourcing_state = "COMPOSED"

    def set_resources_removed(self):
        """
        Set resources removed state
        :return: None
        """
        self._set_box("Resources Assigned?", "DISABLED")
        self.resourcing_state = "EMPTY"

    def set_configuring(self):
        """
        Set configuring state
        :return: None
        """
        self._set_box("Subarray Configured?", "BUSY")
        self.configuration_state = "CONFIGURING"

    def set_configured(self):
        self._set_box("Subarray Configured?", "ACTIVE")
        self.configuration_state = "READY"
        if self.scanning_state == "SCANNING":
            self.scanning_state = "NOT_SCANNING"

    def set_configuration_cleared(self):
        """
        Set configuration cleared state
        :return: None
        """
        self._set_box("Subarray Configured?", "DISABLED")
        self.configuration_state = "NOT_CONFIGURED"

    def set_scanning(self):
        """
        Set scanning state
        :return: None
        """
        self._set_box("Subarray Scanning?", "BUSY")
        self.scanning_state = "SCANNING"

    def set_not_scanning(self):
        """
        Set not scanning state
        :return: None
        """
        self._set_box("Subarray Scanning?", "DISABLED")
        self.scanning_state = "NOT_SCANNING"

    def set_scanning_ready(self):
        """
        Set scanning ready state
        :return: None
        """
        # Only consider to be 'ACTIVE' after 'SCANNING'.
        # Otherwise we haven't started scanning yet, so we are 'DISABLED'.
        if self.scanning_state in ["SCANNING", "READY"]:
            self._set_box("Subarray Scanning?", "ACTIVE")
            self.scanning_state = "READY"
        else:
            self._set_box("Subarray Scanning?", "DISABLED")
            self.scanning_state = "NOT_SCANNING"

    def set_on(self):
        """
        Set on state
        :return: None
        """
        self._set_box("On/Off", "ACTIVE")
        self.on_off_state = "ON"

    def set_off(self):
        """
        Set off state
        :return: None
        """
        self._set_box("On/Off", "DISABLED")
        self.on_off_state = "OFF"

    def set_offline(self):
        """
        Set offline state
        :return: None
        """
        self._set_box("On/Off", "OFFLINE")
        self.on_off_state = "OFFLINE"

    def observe_telescope_on_off(self, state: Literal["ON", "ERROR", "OFFLINE", "OFF"]):
        """
        Observe telescope on/off state
        :param state: current state
        :return: None
        """
        if state == "ON":
            self.set_on()
        elif state == "OFFLINE":
            self.set_offline()
        else:
            self.set_off()

    def observe_subarray_resources_state(self, state: SubarrayResourceState):
        """
        Observe subarray resources state
        :param state: subarray resources state
        :return: None
        """
        if state != self.resourcing_state:
            if state == "COMPOSED":
                self.set_resources_assigned()
            elif state == "RESOURCING":
                self.set_resources_assigning()
            else:
                self.set_resources_removed()

    def observe_subarray_configuration_state(
        self, state: SubarrayConfigurationState | SubarrayResourceState
    ):
        """
        Observe subarray configuration state
        :param state: subarray configuration state
        :return: None
        """
        if state != self.resourcing_state:
            if state == "READY":
                self.set_resources_assigned()
                self.set_configured()
            elif state == "CONFIGURING":
                self.set_configuring()
            else:
                self.set_configuration_cleared()

    def observe_subarray_scanning_state(self, state: SubarrayScanningState):
        """
        Observe subarray scanning state
        :param state: subarray scanning state
        :return: None
        """
        if state == "SCANNING":
            self.set_scanning()
        elif state == "READY":
            self.set_scanning_ready()
        elif state == "NOT_SCANNING":
            self.set_not_scanning()
