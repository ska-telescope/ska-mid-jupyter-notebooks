"""Helper classes and functions dealing with aggregation of state from tango dev."""

import abc
import functools
import logging
import os
import time
from collections import defaultdict, deque
from concurrent.futures import CancelledError
from datetime import datetime
from queue import Queue
from threading import Event, Lock, Thread
from typing import Any, Callable, Generic, Literal, NamedTuple, TypedDict, TypeVar, Union, cast

from tango import AttributeProxy, DevFailed, DeviceProxy, EventType
from tango.time_val import TimeVal

# pylint: disable=W0107,W0237


class RemoteDeviceFactory:
    def __init__(self, db_host: str) -> None:
        """
        Initialises RemoteDeviceFactory class
        :param db_host: database host
        :return:  None
        """
        self._db_host = db_host

    def get_device(self, device_name: str) -> DeviceProxy:
        """
        Get Device
        :param: device_name: name of the device
        :return: Device Proxy
        """
        return DeviceProxy(f"tango://{self._db_host}/{device_name}")

    def get_attr_proxy(self, att_name: str) -> AttributeProxy:
        """
        Get Attribute Proxy
        :param: att_name: name of the attribute
        :return: Attribute Proxy
        """
        return AttributeProxy(f"tango://{self._db_host}/{att_name}")


class DeviceAttribute(NamedTuple):
    """Alias object of the tango DeviceAttribute."""

    value: Any
    time: Any
    type: Any
    name: str


class EventData(NamedTuple):
    """Alias object of the tango EventData object."""

    attr_name: str
    attr_value: DeviceAttribute
    device: Any
    err: bool
    errors: Any
    event: str
    reception_date: Any

    @property
    def key(self) -> str:
        """
        Get event key
        :return: event key
        """
        return event_key(self.device.name(), self.attr_name)


# denotes the action type set by the user when instantiating an Action object
ACTION = TypeVar("ACTION")


class BaseAction(Generic[ACTION]):
    """Base class objecting representing an producer publishing an action (effect)."""

    action_id = "base"

    def __init__(self, action_state: ACTION) -> None:
        """
        Initialise the object.
        :param action_state: The action state representing an "effect" on the system.
        :return: None
        """
        self._action_state = action_state
        self.source: Union["ActionProducer[ACTION]", None] = None

    def add_source(self, source: "ActionProducer[ACTION]"):
        """
        Add information as to the source producing the particular action in question.
        :param source: the source producing the particular action in question.
        :return:  None
        """
        self.source = source

    @property
    def key(self) -> str:
        """Return a key (hash) uniquely identifying the object.

        This may be useful when storing the object in a dictionary.

        :return: the key (hash) uniquely identifying the object.

        """
        assert self.source
        return str(self.source.__hash__())

    @property
    def action_state(self) -> ACTION:
        """Return the inherent state that the object represents.

        :return: the inherent state that the object represents.
        """
        return self._action_state


# denotes an event occurred that will impact the overall state of the system
# this can either be an external event representing a tango pub/sub event,
# or an action event produced by the application itself.
GenericEvent = Union[EventData, BaseAction[Any]]


class EventsPusher:
    """And controller object used to push new events onto the system."""

    def __init__(self) -> None:
        """
        Initialise the object.
        :return: None
        """
        self._events: Queue[Union[GenericEvent, None]] = Queue()
        init_list: list[float] = []
        self._polling_keep_alive_timestamps = deque(init_list, maxlen=100)

    def push_event(self, event: GenericEvent):
        """
        Push a new event onto the system.

        An event can either be an external event representing a tango pub/sub event,
        or an action event produced by the application itself.

        :param event: The event that needs to be pushed.
        :return: None
        """
        if hasattr(event, "event"):
            # then we know it is an tango event and convert to EventData
            event = cast(EventData, event)
            if event.attr_value:
                event_data = EventData(
                    event.attr_value.name.lower(),
                    event.attr_value,
                    event.device,
                    event.err,
                    event.errors,
                    event.event,
                    event.reception_date,
                )
            else:  # TODO handle way to recognize error events  # pylint: disable=W0511
                return
        else:
            event_data = event
        self._events.put_nowait(event_data)

    def cancel_get(self):
        """
        Places a None event on the events queue signalling a cancellation.
        :return: None
        """
        self._events.put_nowait(None)

    def _get(self, timeout: Union[float, None] = None) -> GenericEvent:
        """
        Get an event
        :param timeout: timeout in seconds
        :return: GenericEvent
        """

        if event := self._events.get(timeout=timeout):
            return event
        raise CancelledError

    def _task_done(self):
        """
        Marking event as done
        :return: None
        """
        self._events.task_done()
        self._polling_keep_alive_timestamps.append(datetime.now().timestamp())

    def get_last_poll_latency(self):
        """
        Get the last poll latency
        :return: last poll latency
        """
        return datetime.now().timestamp() - self._polling_keep_alive_timestamps[-1]

    def get_average_poll_latency(self):
        """
        Get the average poll latency
        :return: average poll latency
        """
        latencies = [
            current - self._polling_keep_alive_timestamps[index - 1]
            for index, current in enumerate(self._polling_keep_alive_timestamps)
            if index > 0
        ]
        return functools.reduce(lambda x, y: x + y, latencies) / len(
            self._polling_keep_alive_timestamps
        )

    def block_until_empty(self):
        """
        Wait until all events have been handled.
        :return: None
        """
        self._events.join()


class ActionProducer(Generic[ACTION]):
    """An object representing user defined actions (effects) occurring on the system.

    Use this in an observer pattern e.g.:

    .. code-block::
       action = ActionProducer()
       action.subscribe_action(my_observer)
       action.push_action # my_observer will be called

    """

    def __init__(self) -> None:
        """
        Initialise the object.
        :return: None
        """
        self._observers: dict[int, EventsPusher] = {}
        self._index = 0

    def subscribe_action(self, observer: EventsPusher) -> int:
        """Add a new  observer to the list of observers.

        :param observer: the observer object to receive new action events.
        :return: a subscription id to be used when unsubscribing.
        """
        index = self._index
        self._observers[index] = observer
        self._index += 1
        return index

    def push_action(self, action_state: ACTION):
        """Push a new action onto the system.

        This will cause all subscribed observers to be called by their respective
        push_event methods.

        :param action_state: the new action to be pushed onto the system.
        :type action_state: ACTION
        """
        action = BaseAction(action_state)
        action.add_source(self)
        for observer in self._observers.values():
            observer.push_event(action)

    def unsubscribe_action(self, sub_id: int):
        """Unsubscribe an observer (identified by it's subscription id).

        :param sub_id: the subscription id identifying the subscriber
        :type sub_id: int
        :return: None
        """
        self._observers.pop(sub_id)

    def __hash__(self) -> int:  # pylint: disable=W0246
        return super().__hash__()


class BaseSubscription:
    """Abstract representation of a running subscription that can be started and stopped."""

    @abc.abstractmethod
    def start(self, pusher: EventsPusher):
        pass

    def stop(self):
        pass


class ActionSubscription(BaseSubscription, Generic[ACTION]):
    """A concrete running subscription representing subscriptions to ActionProducers."""

    def __init__(self, producer: ActionProducer[ACTION]) -> None:
        """
        Initialise the object.
        :param producer: the action producer that will produce action events.
        :return: None
        """
        self.producer = producer
        self._sub_id = None

    def start(self, observer: EventsPusher):
        """
        Start a subscription for a given subscriber.
        :param pusher: the observer to listen for events.
        :type pusher: EventsPusher
        :return: None
        """
        self._sub_id = self.producer.subscribe_action(observer)

    def stop(self):
        """
        Stop a running subscription.
        :return: None
        """
        assert (
            self._sub_id
        ), "You can not stop a subscription that has not been started, did you call start()?."
        self.producer.unsubscribe_action(self._sub_id)


class UnableToPollDevice(Exception):
    def __init__(self, device_name: str, attr: str, *args: object) -> None:
        """
        Initialises UnableToPollDevice class
        :param device_name: name of the device
        :param attr: name of the attribute
        :param args: args
        :return: None
        """
        super().__init__(*args)
        self.device_name = device_name
        self.attr = attr


class UnableToFindDevice(Exception):
    def __init__(self, device_name: str, *args: object) -> None:
        """
        Initialises UnableToFindDevice class
        :param device_name: name of the device
        :param args: args
        :return: None
        """
        super().__init__(*args)
        self.device_name = device_name


class PolledAttribute:
    def __init__(
        self,
        device_name: str,
        attr: str,
        dev_factory: RemoteDeviceFactory,
    ):
        """
        Initialises PolledAttribute class
        :param device_name: name of the device
        :param attr: name of the attribute
        :param dev_factory: device factory
        :return: None
        """
        self.device_name = device_name
        self.attr = attr
        self._dev_factory = dev_factory

    def __hash__(self) -> int:
        return hash(f"{self.device_name}/{self.attr}")

    def get_state(self):
        """
        Get the state of the attribute
        :return: None
        """
        try:
            dev = self._dev_factory.get_attr_proxy(self.name)
            return cast(DeviceAttribute, dev.read())  # type: ignore
        except DevFailed as exception:
            raise UnableToPollDevice(
                self.device_name, self.attr, cast(Exception, exception).args
            ) from exception

    @property
    def name(self) -> str:
        """
        Get the name of the attribute
        :return: name of the attribute
        """
        return f"{self.device_name}/{self.attr}"

    @property
    def device(self) -> DeviceProxy:  # type: ignore
        """
        Get the device
        :return: device
        """
        try:
            return self._dev_factory.get_device(self.device_name)
        except DevFailed as exception:
            raise UnableToFindDevice(
                self.device_name, cast(Exception, exception).args
            ) from exception


SUB_ID = int


class AttrEventsPusher(NamedTuple):
    sub_id: SUB_ID
    events_pusher: EventsPusher

    def __hash__(self) -> int:
        return hash(f"{self.sub_id}{self.events_pusher}")


class HasValue:
    value: Any
    type: Any


def _generate_event(name: str, new_value: DeviceAttribute, device: Any):  # type: ignore
    """
    Generate event
    :param name: name of the attribute
    :param new_value:  Device Attributes
    :param device: Devices
    :return: EventData
    """
    return EventData(
        name,
        new_value,
        device,
        err=False,
        errors=[],
        event="",
        reception_date=TimeVal(),
    )


class PollingState:
    def __init__(self) -> None:
        """
        Initialises PollingState class
        :return: None
        """
        self._events_to_be_pushed: list[AttrEventsPusher] = []
        self._current_value = None

    def remove(self, events_pushing: AttrEventsPusher):
        """
        Remove events pushing
        :param events_pushing: attribute events pushing
        :return: None
        """
        self._events_to_be_pushed.remove(events_pushing)

    def append(self, events_pushing: AttrEventsPusher):
        """
        Append events pushing
        :param events_pushing: attribute events pushing
        :return: None
        """
        self._events_to_be_pushed.append(events_pushing)

    def update_state(self, new_value: DeviceAttribute, device: DeviceProxy):  # type: ignore
        """
        Update state
        :param new_value:  Device Attributes
        :param device: Devices
        :return: None
        """
        value = new_value.value
        if self._current_value != value:
            self._current_value = value
            event = _generate_event(new_value.name, new_value, device)
            for event_to_be_pushed in self._events_to_be_pushed:
                event_to_be_pushed.events_pusher.push_event(event)  # type: ignore


class DeviceAttrPoller:
    def __init__(
        self,
        dev_factory: RemoteDeviceFactory,
        poll_rate: float = 2,
    ) -> None:
        """
        Initialises DeviceAttrPoller class
        :param poll_rate: poll rate
        :param dev_factory: device factory
        :return: None
        """

        self._poll_rate = poll_rate
        self._active = Event()
        self._thread = Thread(target=self._polling_thread, daemon=True)
        self._index = 0
        self._dev_factory = dev_factory
        self._subscriptions: dict[SUB_ID, tuple[PolledAttribute, AttrEventsPusher]] = {}
        self._device_attribute_pollings: dict[PolledAttribute, PollingState] = defaultdict(
            PollingState
        )
        self._lock = Lock()
        self._thread.start()

    def add_subscription(
        self,
        device_name: str,
        attr: str,
        events_pusher: EventsPusher,
        dev_factory: RemoteDeviceFactory | None = None,
    ) -> SUB_ID:
        """
        Add subscription
        :param device_name: device name
        :param attr: attribute
        :param events_pusher: events pusher
        :param dev_factory: device factory
        :return: sub_id
        """
        if dev_factory is None:
            dev_factory = self._dev_factory
        # first we get an updated state
        device_attribute = PolledAttribute(device_name, attr, dev_factory)
        state = device_attribute.get_state()
        # then we immediately push it as an event
        event = _generate_event(state.name, state, device_attribute.device)
        events_pusher.push_event(event)  # type: ignore
        if polling_state := self._device_attribute_pollings.get(device_attribute):
            # if there are already existing subscriptions
            polling_state.update_state(state, device_attribute.device)  # type: ignore
        with self._lock:
            self._index += 1
            atr_events_pusher = AttrEventsPusher(self._index, events_pusher)
            self._subscriptions[self._index] = (
                device_attribute,
                atr_events_pusher,
            )
            self._device_attribute_pollings[device_attribute].append(atr_events_pusher)
        # we only start the thread once we have an active subscription
        if not self._active.is_set():
            self._active.set()
        return self._index

    def remove_subscription(self, sub_id: SUB_ID):
        """
        Remove subscription
        :param sub_id: subscription id
        :return: None
        """
        with self._lock:
            device_attribute, attr_events_pusher = self._subscriptions.pop(sub_id)
            self._device_attribute_pollings[device_attribute].remove(attr_events_pusher)

    def _get_attr_to_poll(self) -> list[tuple[PolledAttribute, PollingState]]:
        """
        Get attributes to poll
        :return: attributes to poll
        """
        with self._lock:
            return list(self._device_attribute_pollings.items())

    def _update(self):
        """
        Update State
        :return: None
        """
        for device_attr, polling_state in self._get_attr_to_poll():
            result = device_attr.get_state()
            polling_state.update_state(result, device_attr.device)  # type: ignore

    def start(self):
        """
        Start polling
        :return: None
        """
        self._active.set()

    def stop(self):
        """
        Stop polling
        :return: None
        """
        self._active.clear()

    def _polling_thread(self):
        """
        Polling Thread
        :return: None
        """
        while self._active:
            self._update()
            time.sleep(self._poll_rate)


class UnableToStartSubscription(Exception):
    def __init__(self, device_name: str, attr: str, *args: object) -> None:
        """
        Initialises UnableToStartSubscription class
        :param device_name: name of the device
        :param attr: attribute
        :param args: args
        :return: None
        """
        super().__init__(*args)
        self.device_name = device_name
        self.attr = attr


class EventsSubscription(BaseSubscription):
    """A concrete running subscription representing subscriptions to a Tango Device."""

    attr: str
    device_name: str

    def __init__(
        self,
        device_name: str,
        attr: str,
        dev_factory: RemoteDeviceFactory,
        poller: DeviceAttrPoller,
    ) -> None:
        """Initialise the object.

        :param device_name: The tango device FQD name
        :param attr: The attribute of that device to be subscribed to for change events.
        :param dev_factory: The device factory to use
        :return: None
        """
        self.attr = attr
        self.device_name = device_name
        self._poller = poller
        self._sub_id: Union[None, int] = None
        self._dev_factory = dev_factory
        self._device_proxy = dev_factory.get_device(self.device_name)

    def start(self, observer: EventsPusher):
        """Start a subscription for a given subscriber on a tango device.

        :param pusher: the observer to listen for events.
        :type pusher: EventsPusher
        :return: None
        """
        if os.getenv("USE_POLLING"):
            try:
                self._sub_id = self._poller.add_subscription(
                    self.device_name, self.attr, observer, self._dev_factory
                )
                return
            except UnableToPollDevice as exception:
                raise UnableToStartSubscription(
                    exception.device_name, exception.attr, exception.args
                ) from exception
        try:
            self._sub_id = self._device_proxy.subscribe_event(
                self.attr, EventType.CHANGE_EVENT, observer
            )
        except DevFailed:
            print(
                f"Warning: no polling setup for subscribing to {self.device_name} on {self.attr}, "
                f"setting a polling of 100ms in order to implement subscription."
            )
            try:
                self._device_proxy.poll_attribute(self.attr, 100)
                self._sub_id = self._device_proxy.subscribe_event(
                    self.attr, EventType.CHANGE_EVENT, observer
                )
            except DevFailed as exception:
                raise UnableToStartSubscription(
                    self.device_name,
                    self.attr,
                    cast(Exception, exception).args,
                ) from exception

    def stop(self):
        """
        Stop a running subscription.
        :return: None
        """
        assert (
            self._sub_id
        ), "You can not stop a subscription that has not been started, did you call start()?."
        if os.getenv("USE_POLLING"):
            self._poller.remove_subscription(self._sub_id)
            return
        self._device_proxy.unsubscribe_event(self._sub_id)


STATE = TypeVar("STATE")  # STATE defines the current state of the entity being modeled
VALUE = TypeVar("VALUE")  # VALUE is the particular derived value obtained from querying the state


# user defined function that updates (returns) the given state based on an given action
ActionReducerFunction = Callable[[STATE, ACTION], STATE]
# user defined function that updates (returns) the given state based on given EventData
EventsReducerFunction = Callable[[STATE, EventData], STATE]
# generic reducer function that can be of either of the above
ReduceFunction = Union[ActionReducerFunction[STATE, Any], EventsReducerFunction[STATE]]


class Reducer(Generic[STATE]):
    """Abstract object representing the act of reducing the state based on new events."""

    @abc.abstractmethod
    def reduce(self, state: STATE, event_or_action: GenericEvent) -> STATE:
        """Returns an updated state based on event or action."""
        pass

    @abc.abstractmethod
    def generate_subscription(self) -> BaseSubscription:
        """Generate a running subscription based on the inherent producer."""
        pass

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """Generate a unique key to identify the reducer in a dictionary."""
        pass


class ActionsReducer(Reducer[STATE], Generic[STATE, ACTION]):
    """Concrete implementation of a Reducer for Action events."""

    def __init__(
        self,
        producer: ActionProducer[ACTION],
        reduce_function: ActionReducerFunction[STATE, ACTION],
    ) -> None:
        """
        Initialise the object.

        :param producer: the inherent producer responsible for generating events.
        :param reduce_function: the user provided reduce function.
        :return: None
        """
        self.producer = producer
        self._reduce_function = reduce_function

    def reduce(self, state: STATE, event_or_action: GenericEvent) -> STATE:
        """
        Effects the reduction of the system by running the user provided reduce function.

        :param state: The current state of the system
        :param event_or_action: The event to be used as input to the reduce function
        :return: The updated state
        """
        action = cast(BaseAction[ACTION], event_or_action)
        return self._reduce_function(state, action.action_state)

    def generate_subscription(self) -> BaseSubscription:
        """
        Generate a running subscription based on the inherent producer.
        :return: the subscription
        """
        return ActionSubscription(self.producer)

    @property
    def key(self) -> str:
        """
        Generate a unique key to identify the reducer in a dictionary.
        :return: the key
        """
        return str(self.producer.__hash__())


class EventsReducer(Reducer[STATE], Generic[STATE]):
    """Concrete implementation of a Reducer for Tango Device change events."""

    def __init__(
        self,
        device_name: str,
        attr_name: str,
        reduce_function: EventsReducerFunction[STATE],
        dev_factory: RemoteDeviceFactory,
        poller: DeviceAttrPoller,
    ) -> None:
        """Initialise the object.

        :param device_name: The FQD name of the tango device
        :param attr_name: The attribute of the device to listen to for events
        :param reduce_function: The user provided reduce function for tango events
        :param dev_factory: The device factory
        :return: None
        """
        self.attr_name = attr_name
        self.device_name = device_name
        self._reduce_function = reduce_function
        self._dev_factory = dev_factory
        self._poller = poller

    def reduce(self, state: STATE, event_or_action: GenericEvent) -> STATE:
        """Effects the reduction of the system by running the user provided reduce function.

        :param state: The current state of the system
        :param event_or_action: The event to be used as input to the reduce function
        :return: The updated state
        """
        event = cast(EventData, event_or_action)
        return self._reduce_function(state, event)

    def generate_subscription(self) -> BaseSubscription:
        """
        Generate a running subscription based on the inherent producer.
        :return: BaseSubscription
        """
        return EventsSubscription(
            self.device_name, self.attr_name, self._dev_factory, self._poller
        )

    @property
    def key(self):
        """
        Generate a unique key to identify the reducer in a dictionary.
        :return: the key
        """
        return event_key(self.device_name, self.attr_name)


def event_key(device_name: str, attr_name: str) -> str:
    """generate an unique name (for use in dicts) based on a device's name and its attribute.

    Note the purpose of this function is to ensure a user can globally lookup an subscription based on
    only the provided device name and attr name as this same method will be used to internally create
    ids within the module.

    :param device_name: The FDQ device name
    :param attr_name: The device attribute
    :return: The key uniquely identifying the event
    """
    return f"{device_name}:{attr_name}"


def explode_from_key(key: str) -> list[str]:
    """Do the inverse of generating a key (useful for printing out information of a given event.

    :param key: The key identifying the event
    :return: A list containing [<device name>, <device attribute>]
    """
    return key.split(":")


def get_event_key(event: Union[EventData, BaseAction[Any]]) -> str:
    """_summary_

    :param event: The event (tango based or action based) in question
    :return: A unique key to identify the event with
    """
    if isinstance(event, EventData):
        return event_key(event.device.name(), event.attr_name)
    else:
        return str(event.__hash__())


# type of user provided function that returns a particular value or interpretation from the given state
SelectorFunction = Callable[[STATE], VALUE]

# user provided function that does not return anything but simply just observes (e.g. logs or prints out or store)
# the current state of the system
ObserveFunction = Callable[[VALUE], None]


class Selector(Generic[STATE, VALUE]):
    """Object representing a user provided selection of state after it has been updated.

    There are two types of selector functions upon which this object will operate on:
        1. A global selector function in which the input to the function is the entire state of the system
        2. A derived selector function using inputs from pre-existing selector functions.

    A global selector function implies no inputs need to be provided.

    A derived selector function **does require** input selector functions. Derived selector functions will only be called
    if the inputs are not the same as previous, otherwise the previous result will simply be returned.

    """

    def __init__(
        self,
        selector_function: Union[Callable[..., VALUE], Callable[[STATE], VALUE]],
        *inputs: Union["Selector[STATE, Any]", Callable[[STATE], Any]],
    ) -> None:
        """Initialise the object.

        :param selector_function: The selector function upon which this object will operate on.
            There are two types of selector functions:
                1. A global selector function in which the input to the function is the entire state of the system
                2. A derived selector function using inputs from pre-existing selector functions.
        :param inputs: input selector functions (if of type 2) that will provide the input args to the selector
            function. Note the inputs selector function return types need to be of correct type and order.
            The selector function will return the previous result and not perform the actual calculation if the inputs are
            the same as previous.
        :return: None
        """
        self._selector_function = selector_function
        self._inputs: list[Union[Selector[Any, Any], Selector[STATE, Any]]] = []
        for input_args in inputs:
            if not isinstance(input_args, Selector):
                input_args = cast(Callable[[STATE], Any], input_args)  # type: ignore
                self._inputs.append(Selector(input_args))
            else:
                self._inputs.append(input_args)
        self._previous_result = None
        self._previous_input_values = None

    def select(self, state: STATE) -> VALUE:
        """Performs the selector function on the given state.

        Note the selector function will return the previous result and not perform the actual
        calculation if the inputs are the same as previous.

        :param state: The input state.
        :return: The derived or selected value. (this will be the same as previous if no inputs changed)
        """
        if self._inputs:
            input_values = [input.select(state) for input in self._inputs]
            if input_values != self._previous_input_values:
                self._previous_input_values = input_values
                self._previous_result = self._selector_function(*input_values)
            assert self._previous_result is not None
            return self._previous_result
        return self._selector_function(state)


class Publisher(Generic[STATE, VALUE]):
    """Object used to publish the results of selector functions to a given observe function.

    The object is basically just a wrapper over the Selector object with the difference that the,
    observer function will not be called with an value if the value did not change.
    """

    def __init__(self, selector: Selector[STATE, VALUE], observe: ObserveFunction[VALUE]) -> None:
        """Initialise the object.

        :param selector: The selector (with user provided selector function)
        :param observe: the observe function to be called when the state have changed
        :return: None

        """
        self._selector = selector
        self._observe = observe
        self._previous_result: VALUE | None = None

    def publish(self, state: STATE):
        """Publish a new selected value if the results are different from previous publish.

        By publish is meant the inherent observe function provided during initialisation will be called.

        :param state: _description_
        :type state: STATE
        :return: None
        """
        result = self._selector.select(state)
        if result != self._previous_result:
            self._previous_result = result
            self._observe(result)


class ReducerSpec(TypedDict):
    """Represents the reduce function to be operated on a given device attribute change event."""

    device_name: str
    attr_name: str
    reduce_function: ReduceFunction[Any]


class MonState(EventsPusher, Generic[STATE]):
    """A coordination object responsible for orchestrating the monitoring of events on a provided system.

    The object is initialised with a provided system state (in initialised condition), then a set of
    reducers are specified on the state (with subscriptions added if necessary to realise the reduction of
    state). Following that a set of observe functions on a set of selector functions is added to enable "listening" to specific
    changes in derived state of the system.
    After that the object listening can be activated, causing incoming events from publishers to update
    the state followed by the user provided observe functions to be called if their corresponding selector functions have
    a change in calculated value.
    """

    def __init__(self, initState: STATE) -> None:
        """
        Initialise the object
        :return: None
        """
        super().__init__()
        self.state = initState
        self._subscriptions: dict[str, BaseSubscription] = dict({})
        self._publishers: list[Publisher[STATE, Any]] = []
        self._reducers: dict[str, list[Reducer[STATE]]] = defaultdict(lambda: [])
        self._daemon: Union[Thread, None] = None
        self._running: Event = Event()

    def _add_generic_reducer(self, reducer: Reducer[STATE]):
        current_reducers = self._reducers[reducer.key]
        if current_reducers == []:
            # this means we have not yet created a subscription for this event

            self._subscriptions[reducer.key] = reducer.generate_subscription()
        self._reducers[reducer.key].append(reducer)

    def add_events_reducer(
        self,
        device_name: str,
        attr_name: str,
        reduce_function: EventsReducerFunction[STATE],
    ):
        """Add a reducer function operating on tango device attribute change events.

        :param device_name: The FDQ device name
        :param attr_name: The device attribute
        :param reduce_function: The function to update the state of the system when the attribute changes
        :return: None
        """
        reducer = EventsReducer(device_name, attr_name, reduce_function)
        self._add_generic_reducer(reducer)

    def add_action_reducer(
        self,
        producer: ActionProducer[ACTION],
        reduce_function: ActionReducerFunction[STATE, ACTION],
    ):
        """Add a reducer function operating on action events occurring on the application.

        :param producer: The action producer to be subscribed to for a particular event.
        :param reduce_function: The reduce function to be called by the provided producer.
        :return: None
        """
        reducer = ActionsReducer(producer, reduce_function)
        self._add_generic_reducer(reducer)

    def add_reducers(self, reducers: list[Reducer[STATE]]):
        """Add a list of predefined reducers to the monitor.
        This allows for separating the stage of creating reducers from initialising the monitoring object.

        :param reducers: The list of reducers to be added
        :return: None
        """
        for reducer in reducers:
            self._add_generic_reducer(reducer)

    def add_observer(
        self,
        observe_function: ObserveFunction[VALUE],
        selector: Selector[STATE, VALUE],
    ):
        """Add an observe function to a provided selector function.

        This will cause the observe function to be called whenever the selector function calculates
        an updated value.

        :param observe_function: The function to be called when the selector function calculation changed.
        :param selector: The selector object to be used for calculating a new value
        :return: None
        """
        self._publishers.append(Publisher(selector, observe_function))

    def add_publishers(self, publishers: list[Publisher[STATE, Any]]):
        """Add a list of publishers to th existing list of publishers.

        This can help to separate the creation of observers on selector functions from
        initialising the object.

        :param publishers: The list of publishers
        :return: None
        """
        self._publishers = [*self._publishers, *publishers]

    def start_subscriptions(self):
        """
        Start the subscriptions by actively starting to produce events on subscribers.

        Note an unsuccessful subscription that can not be started will cause the subscription and reducer to
        be removed.
        :return: None
        """
        items_to_pop: list[str] = []
        for key, subscription in self._subscriptions.items():
            try:
                subscription.start(self)
            except UnableToStartSubscription as exception:
                logging.exception(
                    "Unable to start subscription on %s for %s",
                    exception.device_name,
                    exception.attr,
                )
                items_to_pop.append(key)
        for key in items_to_pop:
            self._subscriptions.pop(key)
            self._reducers.pop(key)

    def _listening_daemon(self):
        """
        The daemon that listens for events and publishes them
        :return: None
        """
        counter = 0
        try:
            while self._running.is_set():
                try:
                    event = self._get()
                except CancelledError:
                    return
                state = self.state
                # first we reduce the state but we make it "unbreakable" since the thread must always run
                event_key_input = event.key
                reducers_to_remove: list[int] = []
                if reducers := self._reducers.get(event_key_input):
                    for index, reducer in enumerate(reducers):
                        try:
                            state = reducer.reduce(state, event)
                        except Exception as exception:  # pylint: disable=broad-exception-caught
                            logging.exception(exception.args)
                            reducers_to_remove.append(index)
                    for index in reducers_to_remove:
                        reducers.pop(index)
                # then whe publish results but we make it "unbreakable" since the thread must always run
                publishers_to_remove: list[int] = []
                for index, publisher in enumerate(self._publishers):
                    try:
                        publisher.publish(state)
                    except Exception as exception:  # pylint: disable=broad-exception-caught
                        logging.exception(exception.args)
                        publishers_to_remove.append(index)
                for index in publishers_to_remove:
                    self._publishers.pop(index)
                # then we save the state
                self.state = state
                self._task_done()
                time.sleep(0.5)
                counter += 1
            logging.info("exiting monitoring loop")
        except Exception as exception:
            logging.warning("exiting monitoring loop due to an unknown exception")
            raise exception

    def start_listening(self):
        """
        Active the monitoring of state by updating and publishing changes in state from incoming events.
        :return: None
        """
        self._daemon = Thread(target=self._listening_daemon, daemon=True)
        self._running.set()
        self._daemon.start()

    @property
    def listening_state(self) -> Literal["Running", "Aborted", "Not Started"]:
        """
        The state of the background thread
        :return: The state of the background thread
        """
        if self._daemon:
            if self._daemon.is_alive():
                return "Running"
            if self._running:
                return "Aborted"
        return "Not Started"

    def stop_listening(self, timeout: Union[None, float] = None):
        """Stop the background threads listening to events and updating the system state.

        Note this will cause the program to wait until the thread has been gracefully stopped
        and will timeout of the stopping failed to complete withing a given time if one
        is provided.

        :param timeout: the maximum time to wait for thread to finish (unless None), defaults to None
        :return: None
        """
        if self._daemon:
            self._running.clear()
            self.cancel_get()
            self._daemon.join(timeout=timeout)
