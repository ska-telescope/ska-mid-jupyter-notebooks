from typing import Any, Callable, Literal, NamedTuple, TypedDict, cast

from ska_mid_jupyter_notebooks.monitoring.statemonitoring import (
    EventData,
    EventsReducer,
    MonState,
    Reducer,
    RemoteDeviceFactory,
    Selector,
    event_key,
)
from ska_mid_jupyter_notebooks.test_equipment.base import DeviceDevState, TestDevice
from ska_mid_jupyter_notebooks.test_equipment.configure import TangoTestEquipment


class DeviceNameAndState(NamedTuple):
    device_name: str
    device_state: DeviceDevState


class EquipmentState(TypedDict):
    devices_states: dict[str, DeviceDevState]


def get_equipment_model(test_equipment: TangoTestEquipment):
    """
    Get equipment status
    :param test_equipment: TangoTestEquipment
    :return: Test Equipment Model object
    """
    return TestEquipmentModel(test_equipment)


class TestEquipmentModel:

    test_devices: list[TestDevice] = [
        "mid-itf/progattenuator/1",
        "mid-itf/siggen/1",
        "mid-itf/skysimctl/4",
    ]

    def __init__(self, test_equipment: TangoTestEquipment) -> None:
        """
        Initialises TestEquipmentModel class
        :param test_equipment: TangoTestEquipment
        :return: None
        """
        self._dev_factory = RemoteDeviceFactory(test_equipment.tango_host())
        init_state = EquipmentState(
            devices_states={f"{device}:state": "UNKNOWN" for device in test_equipment.devices}
        )
        self._state_monitor: MonState[EquipmentState] = MonState(init_state)

        reducers = [
            EventsReducer(
                device,
                "state",
                self._reducer_set_device_attribute,
                self._dev_factory,
            )
            for device in test_equipment.devices
        ]
        self._state_monitor.add_reducers(cast(list[Reducer[Any]], reducers))
        self._active = False

    def get_last_poll_latency(self):
        """
        Get last poll latency
        :return: last poll latency
        """
        return self._state_monitor.get_last_poll_latency()

    def get_average_poll_latency(self):
        """
        Get average poll latency
        :return: average poll latency
        """
        return self._state_monitor.get_last_poll_latency()

    @property
    def listening_state(self):
        """
        Get listening state
        :return: listening state
        """
        return self._state_monitor.listening_state

    @classmethod
    def _reducer_set_device_attribute(
        cls, state: EquipmentState, event: EventData
    ) -> EquipmentState:
        """
        Reducer set device attribute
        :param state: Equipment state
        :param event: Event data
        :return: Equipment state
        """
        value = event.attr_value.value
        state["devices_states"][event.key] = cast(DeviceDevState, str(value))
        return state

    @classmethod
    def _generate_select_device_name_and_attr_state(
        cls, device_name: str, attr: str
    ) -> Selector[EquipmentState, DeviceNameAndState]:
        """
        Generate select device name and attr state
        :param device_name: Device name
        :param attr: Attribute
        :return: Selector
        """

        def _select_device_attr(state: EquipmentState) -> DeviceNameAndState:
            """
            Select device attributes
            :param state: Equipment state
            :return: DeviceNameAndState
            """
            state_val = state["devices_states"][event_key(device_name, attr)]
            return DeviceNameAndState(device_name, state_val)

        return Selector(_select_device_attr)

    def subscribe_to_test_equipment_state(
        self, observe_function: Callable[[dict[str, DeviceDevState]], None]
    ):
        """
        Subscribe to test equipment state
        :param observe_function: Observe function
        :return: None
        """
        input_test_equipment_states = [
            self._generate_select_device_name_and_attr_state(device, "state")
            for device in self.test_devices
        ]

        def select_agg_dev_state(
            *states: DeviceNameAndState,
        ) -> dict[str, DeviceDevState]:
            """
            Select aggregate device state
            :param states: Device name and state
            :return: device state
            """
            return {state.device_name: state.device_state for state in states}

        test_equipment_state_selector = Selector[EquipmentState, dict[str, DeviceDevState]](
            select_agg_dev_state, *input_test_equipment_states
        )

        self._state_monitor.add_observer(observe_function, test_equipment_state_selector)

    @property
    def state(self) -> EquipmentState:
        """
        Get state
        :return: Equipment state
        """
        if not self._active:
            self._state_monitor.start_subscriptions()
            self._state_monitor.start_listening()
            self._active = True
        return self._state_monitor.state

    def activate(self):
        """
        Activate
        :return: None
        """
        if not self._active:
            self._state_monitor.start_subscriptions()
            self._state_monitor.start_listening()
            self._active = True
