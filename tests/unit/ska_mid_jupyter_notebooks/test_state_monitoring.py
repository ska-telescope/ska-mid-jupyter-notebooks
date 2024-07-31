"""Test monitoring of states."""

from enum import Enum
from typing import Any, Callable, Generator, cast
from unittest import mock

import pytest
from assertpy import assert_that

from ska_mid_jupyter_notebooks.cluster.cluster import TangoDeployment
from ska_mid_jupyter_notebooks.monitoring.statemonitoring import (
    STATE,
    ActionProducer,
    DeviceAttribute,
    EventData,
    EventsPusher,
    MonState,
    Selector,
)

# mypy: disable-error-code="import-untyped"


def test_selector_call_memorised() -> None:
    """Test memorised selector call."""
    state = {"foo": "bar", "bar": "foo"}

    def select_foo(_st: dict[str, str]) -> Any:  # pylint: disable=W0613
        """Test foo."""
        return state["foo"]

    def select_bar(_st: dict[str, str]) -> Any:  # pylint: disable=W0613
        """Test bar."""
        return state["bar"]

    def selector_function(f_x: str, f_y: str) -> str:
        """Select the thing."""
        return f"{f_x}/{f_y}"

    selector_spy = cast(Callable[[dict[str, str]], str], mock.Mock(wraps=selector_function))

    selector: Selector = Selector(selector_spy, select_foo, select_bar)

    result = selector.select(state)
    assert_that(result).is_equal_to("bar/foo")
    selector_spy.assert_called_once()  # type: ignore
    result = selector.select(state)
    assert_that(result).is_equal_to("bar/foo")
    selector_spy.assert_called_once()  # type: ignore


class Provider:
    """Provide the provisions."""

    def __init__(self) -> None:
        self.subscribers: list[EventsPusher] = []

    def add_subscriber(self, _: str, __: Any, pusher: EventsPusher) -> None:
        """Add a subscriber."""
        self.subscribers.append(pusher)

    def push_event(self, event: EventData) -> None:
        """
        Push an event.

        :param event: event to be pushed
        """
        for subscriber in self.subscribers:
            subscriber.push_event(event)


@pytest.fixture(name="mock_provider")
def fxt_mock_provider() -> Provider:
    """
    Get a fixture for a mock provider.

    :return: provider fixture
    """
    return Provider()


@pytest.fixture(name="mock_device")
def fxt_mock_device(mock_provider: Provider) -> Generator:
    """
    Get a fixture for a mock device.

    :param mock_provider: mock provider
    :return: fixture for provider
    """
    with mock.patch(
        "ska_mid_jupyter_notebooks.monitoring.statemonitoring.DeviceProxy"
    ) as mock_device:
        mock_impl = mock_device.return_value
        mock_impl.subscribe_event.side_effect = mock_provider.add_subscriber
        mock_impl.name.return_value = "mock_device"
        yield mock_impl


@pytest.fixture(name="mock_event")
def fxt_mock_event(mock_device: mock.Mock) -> EventData:
    """
    Test fixture for mock event.

    :param mock_device: mock device
    :return: event data
    """
    return EventData(
        "mock_attr",
        DeviceAttribute("value", "time", "type", "mock_attr"),
        mock_device,
        False,
        "errors",
        "event",
        "reception_date",
    )


# pylint: disable-next=too-few-public-methods
class Observer:
    """Make observations of stuff."""

    def __init__(self) -> None:
        """Rock and roll."""
        self.result: str | None = None

    def observe_function(self, value: str) -> None:
        """
        Observe that the function still functios.

        :param value: value to observe
        """
        self.result = value


@pytest.fixture(name="mock_observer")
def fxt_mock_observer() -> Observer:
    """
    Test fixture for mock observer.

    :return: observation
    """
    return Observer()


def test_state_monitoring_of_events(
    mock_provider: Provider, mock_event: EventData, mock_observer: Observer
) -> None:
    """
    Test state monitoring of events.

    :param mock_provider:  mock provider
    :param mock_event: mock event
    :param mock_observer: mock observer
    """
    init_state = {"foo": {"bar": "foo"}}
    monitor = MonState(init_state, TangoDeployment("test"))

    def reducer_set_foo_bar_to_value(state: dict[str, dict[str, str]], event: EventData) -> dict:
        """
        Set reducer value.

        :param state: state of affairs
        :param event: eventual thing
        :return: dictionary of events
        """
        state["foo"]["bar"] = event.attr_value.value
        return state

    def select_foo_bar(state: dict[str, dict[str, str]]) -> str:
        """
        Set things up.

        :param state: state of affairs
        :return:  dictionary of states
        """
        return state["foo"]["bar"]

    monitor.add_events_reducer("mock_device", "mock_attr", reducer_set_foo_bar_to_value)
    monitor.add_observer(mock_observer.observe_function, Selector(select_foo_bar))
    monitor.start_subscriptions()
    try:
        monitor.start_listening()
        mock_provider.push_event(mock_event)
        monitor.block_until_empty()
        assert_that(mock_observer.result).is_equal_to(mock_event.attr_value.value)
    finally:
        monitor.stop_listening(10)


def test_state_monitoring_of_actions(mock_observer: Observer) -> None:
    """
    Test state monitoring of actions.
    :param mock_observer: mock observer
    :return:
    """
    init_state: STATE = {"foo": {"bar": "foo"}}  # type: ignore[valid-type]
    monitor = MonState(init_state, TangoDeployment("test"))

    class ControlActions(Enum):
        """Store control actions."""

        ON = "ON"
        OFF = "OFF"

    def reducer_set_foo_bar_to_input_action(state: STATE, action: ControlActions) -> STATE:
        """
        Set reducer action.

        :param state: state of affairs
        :param action: control actions
        """
        state["foo"]["bar"] = action.value  # type: ignore[index]
        return state

    def select_foo_bar(state: STATE) -> str:  # type: ignore
        """
        Set things up.

        :param state: state of affairs
        :return:  dictionary of states
        """
        return state["foo"]["bar"]  # type: ignore[index]

    controller = ActionProducer[ControlActions]()

    monitor.add_action_reducer(controller, reducer_set_foo_bar_to_input_action)
    monitor.add_observer(mock_observer.observe_function, Selector(select_foo_bar))
    monitor.start_subscriptions()
    try:
        monitor.start_listening()
        controller.push_action(ControlActions.OFF)
        monitor.block_until_empty()
        assert_that(mock_observer.result).is_equal_to(ControlActions.OFF.value)
    finally:
        monitor.stop_listening(10)
