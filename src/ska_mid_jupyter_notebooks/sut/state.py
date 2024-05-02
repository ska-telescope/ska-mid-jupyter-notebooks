from threading import Event
from typing import Callable, List, Literal, NamedTuple, TypedDict, Union, cast

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment
from ska_mid_jupyter_notebooks.monitoring.statemonitoring import (
    DeviceAttrPoller,
    EventData,
    EventsReducer,
    MonState,
    Reducer,
    RemoteDeviceFactory,
    Selector,
    event_key,
    explode_from_key,
)

from .base import SubarrayConfigurationState, SubarrayResourceState, SubarrayScanningState

DeviceDevState = Literal["ON", "ERROR", "DISABLE", "OFF", "UNKNOWN"]

DeviceState = Union[DeviceDevState, "SubarrayObsState"]


class TelescopeState(TypedDict):
    devices_states: dict[str, DeviceState]


SubarrayObsState = Literal[
    "EMPTY", "RESOURCING", "IDLE", "CONFIGURING", "READY", "SCANNING", "ERROR"
]
SubarrayInputObsState = int

obsstate_mapping = dict[SubarrayInputObsState, SubarrayObsState](
    {
        0: "EMPTY",
        1: "RESOURCING",
        2: "IDLE",
        3: "CONFIGURING",
        4: "READY",
        5: "SCANNING",
    }
)


class TelescopeDeviceModel:
    _dish_ids: List[str]
    _subarray_count: int

    def __init__(self, dish_ids: List[str], subarray_count: int):
        self._dish_ids = dish_ids
        self._subarray_count = subarray_count

    def tm_devices(self) -> List[str]:
        return [
            "ska_mid/tm_central/central_node",
            *[f"ska_mid/tm_subarray_node/{index}" for index in range(1, self._subarray_count + 1)],
            "ska_mid/tm_leaf_node/csp_master",
            "ska_mid/tm_leaf_node/sdp_master",
            *[
                f"ska_mid/tm_leaf_node/csp_subarray{index:0>2}"
                for index in range(1, self._subarray_count + 1)
            ],
            *[
                f"ska_mid/tm_leaf_node/sdp_subarray{index:0>2}"
                for index in range(1, self._subarray_count + 1)
            ],
            *[f"ska_mid/tm_leaf_node/d{id}" for id in self._dish_ids],
        ]

    def csp_devices(self) -> List[str]:
        return [
            "mid-csp/control/0",
            *[f"mid-csp/subarray/{index:0>2}" for index in range(1, self._subarray_count + 1)],
        ]

    def sdp_devices(self) -> List[str]:
        return [
            "mid-sdp/control/0",
            *[f"mid-sdp/subarray/{index:0>2}" for index in range(1, self._subarray_count + 1)],
        ]

    def tmc_devices(self) -> List[str]:
        return [*self.tm_devices(), *self.csp_devices()]

    def subarray_devices(self) -> List[str]:
        return [
            *["ska_mid/tm_subarray_node/1"],
            *["mid-csp/subarray/01"],
        ]


TelescopeAggState = Literal["ON", "ERROR", "OFFLINE", "OFF", "UNKNOWN"]


class DeviceNameAndState(NamedTuple):
    device_name: str
    device_state: DeviceState


class TelescopeModel:
    """Object use to generate reducers and selectors on a Monitor state object."""

    def __init__(
        self,
        state_monitor: MonState[TelescopeState],
        device_model: TelescopeDeviceModel,
        deployment: TangoDeployment,
    ) -> None:
        """Initialise the object

        :param state_monitor: The provided state monitor object.
        """
        self.state_monitor = state_monitor
        self._device_model = device_model
        self._deployment = deployment
        # add device state reducers
        keys = [key for key in state_monitor.state["devices_states"].keys()]
        dev_factory = RemoteDeviceFactory(self._deployment.tango_host)
        poller = DeviceAttrPoller(dev_factory)
        reducers = [
            EventsReducer(device, attr, self._reducer_set_device_attribute, dev_factory, poller)
            for device, attr in [explode_from_key(key) for key in keys]
        ]
        self.state_monitor.add_reducers(cast(list[Reducer[TelescopeState]], reducers))
        self._tel_ready = Event()
        self.subscribe_to_on_off(self.monitor_ready)

    def get_last_poll_latency(self):
        """Get the last poll latency"""
        return self.state_monitor.get_last_poll_latency()

    def get_average_poll_latency(self):
        """Get the average poll latency"""
        return self.state_monitor.get_last_poll_latency()

    @property
    def listening_state(self):
        """Get the listening state"""
        return self.state_monitor.listening_state

    @property
    def state(self) -> TelescopeState:
        """Get monitoring state"""
        return self.state_monitor.state

    def subscribe_to_on_off(
        self,
        observe_function: Callable[[Literal["ON", "ERROR", "OFFLINE", "OFF"]], None],
    ):
        """
        Add an observe function to be called when the telescope aggregate state change between ON/OFF
        :param observe_function: observe function
        """

        input_telescope_agg_state_selector = self._generate_select_all_devices_agg_state(
            self._device_model
        )
        input_central_node_tel_state_selector = self._generate_select_device_attr(
            "ska_mid/tm_central/central_node", "telescopestate"
        )

        def select_telescope_state(
            agg_state: TelescopeAggState, cn_tel_state: Literal["ON", "ERROR"]
        ) -> Literal["ON", "ERROR", "OFFLINE", "OFF"]:
            """
            Select the state of the telescope based on the aggregate state and the state of the central node
            :param agg_state: aggregate state
            :param cn_tel_state: state of the central node
            """
            if all([agg_state == "ON", cn_tel_state == "ON"]):
                return "ON"
            elif any([agg_state == "ERROR", cn_tel_state == "ERROR"]):
                return "ERROR"
            elif agg_state == "OFFLINE":
                return "OFFLINE"
            else:
                return "OFF"

        telescope_state_selector = Selector[
            TelescopeState, Literal["ON", "ERROR", "OFFLINE", "OFF"]
        ](
            select_telescope_state,
            input_telescope_agg_state_selector,
            input_central_node_tel_state_selector,
        )

        self.state_monitor.add_observer(observe_function, telescope_state_selector)

    def monitor_ready(self, state: Literal["ON", "ERROR", "OFFLINE", "OFF"]):
        """
        Check current state and call _tel_ready if state is ON, OFFLINE or OFF
        :param state: current state
        """
        if any([state == "ON", state == "OFFLINE", state == "OFF"]):
            self._tel_ready.set()

    def wait_til_ready(self, timeout: float | None):
        """
        Wait until _tel_ready is ready
        :param timeout: timeout
        """
        self._tel_ready.wait(timeout)

    def subscribe_to_subarray_resource_state(
        self,
        observe_function: Callable[[SubarrayResourceState], None],
    ):
        """
        Add an observe function when the aggregate subarray resource state have changed.
        :param observe_function: observe function
        :return: None
        """

        input_subarray_obsstates = [
            self._generate_select_device_attr(device, "obsstate")
            for device in self._device_model.subarray_devices()
        ]

        def select_agg_subarray_resource_state(
            *obsstates: SubarrayObsState,
        ) -> SubarrayResourceState:
            """
            Select the subarray resource state based on the subarray observation states
            :param obsstates: subarray observation states
            :return: SubarrayResourceState
            """
            if all([obsstate == "EMPTY" for obsstate in obsstates]):
                return "EMPTY"
            elif all([obsstate == "IDLE" for obsstate in obsstates]):
                return "COMPOSED"
            elif any([obsstate == "RESOURCING" for obsstate in obsstates]):
                return "RESOURCING"
            # if it is already passed COMPOSED
            elif any(
                [
                    any(
                        [
                            obsstate == "READY",
                            obsstate == "CONFIGURING",
                            obsstate == "SCANNING",
                        ]
                    )
                    for obsstate in obsstates
                ]
            ):
                return "COMPOSED"
            return "EMPTY"

        subarray_resource_state_selector = Selector[TelescopeState, SubarrayResourceState](
            select_agg_subarray_resource_state, *input_subarray_obsstates
        )
        self.state_monitor.add_observer(observe_function, subarray_resource_state_selector)

    def subscribe_to_subarray_configurational_state(
        self,
        observe_function: Callable[[SubarrayConfigurationState], None],
    ):
        """
        Add an observe function when the aggregate subarray configurational state have changed.
        :param observe_function: observe function
        :return: None
        """
        input_subarray_obsstates = [
            self._generate_select_device_attr(device, "obsstate")
            for device in self._device_model.subarray_devices()
        ]

        def select_agg_subarray_config_state(
            *obsstates: SubarrayObsState,
        ) -> SubarrayConfigurationState:
            """
            Select the subarray configurational state based on the subarray observation states
            :param obsstates: subarray observation states
            :return: SubarrayConfigurationState
            """
            if any([obsstate == "CONFIGURING" for obsstate in obsstates]):
                return "CONFIGURING"
            elif all([obsstate == "READY" for obsstate in obsstates]):
                return "READY"
            # if it is already passed READY
            elif any([obsstate == "SCANNING" for obsstate in obsstates]):
                return "READY"
            return "NOT_CONFIGURED"

        subarray_resource_state_selector = Selector[TelescopeState, SubarrayConfigurationState](
            select_agg_subarray_config_state, *input_subarray_obsstates
        )

        self.state_monitor.add_observer(observe_function, subarray_resource_state_selector)

    def subscribe_to_subarray_scanning_state(
        self,
        observe_function: Callable[[SubarrayScanningState], None],
    ):
        """
        Add an observe function when the aggregate subarray scanning state have changed.
        :param observe_function: observe function
        :return: None
        """
        input_subarray_obsstates = [
            self._generate_select_device_attr(device, "obsstate")
            for device in self._device_model.subarray_devices()
        ]

        def select_agg_subarray_config_state(
            *obsstates: SubarrayObsState,
        ) -> SubarrayScanningState:
            """
            Select the subarray scanning state based on the subarray observation states
            :param obsstates: subarray observation states
            :return: SubarrayScanningState
            """
            if any([obsstate == "SCANNING" for obsstate in obsstates]):
                return "SCANNING"
            if all([obsstate == "READY" for obsstate in obsstates]):
                return "READY"
            return "NOT_SCANNING"

        subarray_resource_state_selector = Selector[TelescopeState, SubarrayScanningState](
            select_agg_subarray_config_state, *input_subarray_obsstates
        )

        self.state_monitor.add_observer(observe_function, subarray_resource_state_selector)

    def subscribe_to_subarrays_obsstate(
        self,
        observe_function: Callable[[dict[str, SubarrayObsState]], None],
    ):
        """
        Add an observe function when the aggregate subarray scanning state have changed.
        :param observe_function: observe function
        :return: None
        """
        input_subarray_obsstates = [
            self._generate_select_device_name_and_attr_state(device, "obsstate")
            for device in self._device_model.subarray_devices()
        ]

        def select_agg_subarray_state(
            *obsstates: DeviceNameAndState,
        ) -> dict[str, SubarrayObsState]:
            """
            Select the subarray observation states based on the subarray observation states
            :param obsstates: subarray observation states
            :return: Obsstate of device
            """
            return {
                obsstate.device_name: cast(SubarrayObsState, obsstate.device_state)
                for obsstate in obsstates
            }

        subarray_resource_state_selector = Selector[TelescopeState, dict[str, SubarrayObsState]](
            select_agg_subarray_state, *input_subarray_obsstates
        )

        self.state_monitor.add_observer(observe_function, subarray_resource_state_selector)

    def activate(self):
        """
        Activate the state monitor
        :return: None
        """
        self.state_monitor.start_subscriptions()
        self.state_monitor.start_listening()

        # reducers

    @classmethod
    def _reducer_set_device_attribute(
        cls, state: TelescopeState, event: EventData
    ) -> TelescopeState:
        """
        Set device attribute
        :param state: telescope state
        :param event: event data
        :return: telescope state
        """
        value = event.attr_value.value
        if event.attr_name == "obsstate":
            if obsstate_value := obsstate_mapping.get(value):
                value = obsstate_value
            else:
                value = "UNKNOWN"
        state["devices_states"][event.key] = cast(DeviceState, str(value))
        return state

    # factory functions for selectors

    @classmethod
    def _generate_select_device_attr(
        cls, device_name: str, attr: str
    ) -> Selector[TelescopeState, DeviceState]:
        """
        Generate a selector for a device attribute
        :param device_name: device name
        :param attr: attribute
        :return: selector
        """

        def _select_device_attr(state: TelescopeState) -> DeviceState:
            """
            Select device attribute
            :param state: telescope state
            :return: device state
            """
            return state["devices_states"][event_key(device_name, attr)]

        return Selector(_select_device_attr)

    @classmethod
    def _generate_select_device_name_and_attr_state(
        cls, device_name: str, attr: str
    ) -> Selector[TelescopeState, DeviceNameAndState]:
        """
        Generate a selector for a device attribute
        :param device_name: device name
        :param attr: attribute
        :return: selector
        """

        def _select_device_attr(state: TelescopeState) -> DeviceNameAndState:
            """
            Select device attribute
            :param state: telescope state
            :return: DeviceNameAndState
            """
            state_val = state["devices_states"][event_key(device_name, attr)]
            return DeviceNameAndState(device_name, state_val)

        return Selector(_select_device_attr)

    @classmethod
    def _generate_select_all_devices_agg_state(
        cls,
        device_model: TelescopeDeviceModel,
    ) -> Selector[TelescopeState, TelescopeAggState]:
        """
        Generate a selector for a device attribute
        :return selector
        """
        input_selectors = [
            cls._generate_select_device_attr(device, "state")
            for device in device_model.tmc_devices()
        ]

        def select_telescope_state(
            *states: TelescopeAggState,
        ) -> TelescopeAggState:
            """
            Select the telescope state based on the states of the devices
            :param states: states of the devices
            :return: TelescopeAggState
            """
            if all([state == "ON" for state in states]):
                return "ON"
            elif any([state == "ERROR" for state in states]):
                return "ERROR"
            elif any([state == "OFFLINE" for state in states]):
                return "OFFLINE"
            elif all([state == "OFF" for state in states]):
                return "OFF"
            else:
                return "UNKNOWN"

        return Selector[TelescopeState, TelescopeAggState](
            select_telescope_state, *input_selectors
        )


# run this after setting execution mode
def get_telescope_state(
    device_model: TelescopeDeviceModel,
    deployment: TangoDeployment,
) -> TelescopeModel:
    """Get TMC mid telescope state"""
    tmc_devices_states = {
        event_key(device, "state"): "UNKNOWN" for device in device_model.tm_devices()
    }
    tmc_devices_states[event_key("ska_mid/tm_central/central_node", "telescopestate")] = "UNKNOWN"

    csp_device_states = {
        event_key(device, "state"): "UNKNOWN" for device in device_model.csp_devices()
    }

    sdp_device_state = {
        event_key(device, "state"): "UNKNOWN" for device in device_model.sdp_devices()
    }

    subarray_device_obs_states = {
        event_key(device, "obsstate"): "UNKNOWN" for device in device_model.subarray_devices()
    }

    init_state = TelescopeState(
        devices_states=cast(
            dict[str, DeviceState],
            {
                **tmc_devices_states,
                **csp_device_states,
                **subarray_device_obs_states,
                **sdp_device_state,
            },
        ),
    )
    monitor_state = MonState(init_state, deployment)
    return TelescopeModel(monitor_state, device_model, deployment)
