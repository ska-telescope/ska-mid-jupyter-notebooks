"""Render test equipment data."""
from typing import Literal, OrderedDict, cast

from ska_mid_jupyter_notebooks.monitoring.rendering import Colours, MonitorPlot
from ska_mid_jupyter_notebooks.test_equipment.base import DeviceDevState, TestDevice

TestEquipmentLabels = Literal[
    "Programmable Attenuator",
    "Signal Generator",
    "SkySim Controller 0",
    "SkySim Controller 4",
]


class TestEquipmentMonitorPlot(MonitorPlot[TestEquipmentLabels, DeviceDevState]):
    test_device_mapping: dict[TestDevice, TestEquipmentLabels] = {
        "mid-itf/progattenuator/1": "Programmable Attenuator",
        "mid-itf/siggen/1": "Signal Generator",
        "mid-itf/skysimctl/4": "SkySim Controller 4",
    }

    _items = OrderedDict[TestEquipmentLabels, DeviceDevState](
        {
            "Programmable Attenuator": "UNKNOWN",
            "Signal Generator": "UNKNOWN",
            "SkySim Controller 4": "UNKNOWN",
        }
    )

    _colour_mapping: dict[DeviceDevState, Colours] = {
        "ON": "forestgreen",
        "ERROR": "red",
        "DISABLE": "pink",
        "OFF": "black",
        "UNKNOWN": "grey",
        "FAULT": "red",
        "ALARM": "orange",
    }

    def __init__(
        self,
        plot_width: int,
        plot_height: int,
    ) -> None:
        """
        Initialises TestEquipmentMonitorPlot class
        :param plot_width: width of the plot
        :param plot_height: height of the plot
        :return: None
        """
        super().__init__(plot_width, plot_height, self._items, self._colour_mapping)

    def handle_device_state_change(self, input_state: dict[str, DeviceDevState]) -> None:
        """
        Handles device state change
        :param input_state: input state
        :return: None
        """
        for key, value in input_state.items():
            key = cast(TestDevice, key)
            if label := self.test_device_mapping.get(key):
                self._set_box(label, value)


def get_test_equipment_monitor_plot() -> TestEquipmentMonitorPlot:
    """
    Get test equipment monitor plot
    :return: test equipment monitor plot
    """
    return TestEquipmentMonitorPlot(plot_width=900, plot_height=200)

