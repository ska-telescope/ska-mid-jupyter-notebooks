"""Test state monitoring."""

from enum import Enum
from typing import Any, Callable, cast
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


def test_selector_call_memoized():
    """Test memorised selector call."""
    state = {"foo": "bar", "bar": "foo"}

    def select_foo(_st: dict[str, str]):  # pylint: disable=W0613
        """Test foo."""
        return state["foo"]

    def select_bar(_st: dict[str, str]):  # pylint: disable=W0613
        """Test bar."""
        return state["bar"]

    def selector_function(f_x: str, f_y: str) -> str:
        """Select the thing."""
        return f"{f_x}/{f_y}"

    selector_spy = cast(Callable[[dict[str, str]], str], mock.Mock(wraps=selector_function))

    selector = Selector(selector_spy, select_foo, select_bar)

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
def fxt_mock_device(mock_provider: Provider):
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
    return EventData(
        "mock_attr",
        DeviceAttribute("value", "time", "type", "mock_attr"),
        mock_device,
        False,
        "errors",
        "event",
        "reception_date",
    )


class Observer:
    def __init__(self):
        self.result = None

    def observe_function(self, value: str):
        self.result = value


@pytest.fixture(name="mock_observer")
def fxt_mock_observer() -> Observer:
    return Observer()


def test_state_monitoring_of_events(
    mock_provider: Provider, mock_event: EventData, mock_observer: Observer
):
    init_state = {"foo": {"bar": "foo"}}
    monitor = MonState(init_state, TangoDeployment("test"))

    def reducer_set_foo_bar_to_value(state: dict[str, dict[str, str]], event: EventData):
        state["foo"]["bar"] = event.attr_value.value
        return state

    def select_foo_bar(state: dict[str, dict[str, str]]) -> str:
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


def test_state_monitoring_of_actions(mock_observer: Observer):
    init_state: STATE = {"foo": {"bar": "foo"}}
    monitor = MonState(init_state, TangoDeployment("test"))

    class ControlActions(Enum):
        ON = "ON"
        OFF = "OFF"

    def reducer_set_foo_bar_to_input_action(state: STATE, action: ControlActions):  # type: ignore
        state["foo"]["bar"] = action.value
        return state

    def select_foo_bar(state: STATE) -> str:  # type: ignore
        return state["foo"]["bar"]

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
