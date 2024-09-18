""" Helper functions to make checking device status and state neater."""

from queue import Empty, Queue
from time import sleep, time
from typing import Any

from tango import DeviceProxy, EventType

spinner = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]

allowed_states = [
    "EMPTY",
    "RESOURCING",
    "IDLE",
    "CONFIGURING",
    "READY",
    "SCANNING",
    "ABORTING",
    "ABORTED",
    "RESETTING",
    "FAULT",
    "RESTARTED",
]


def wait_for_state(device: DeviceProxy, desired_state: str | int, break_on_error=True) -> None:
    """Poll a tango device until either the given observation state is reached, or it throws
    an error.
    Arguments:
    device -- Tango Device to check
    desired_state -- The state which to break upon getting (number or state)
    break_on_error -- If set to False, will keeping running when getting an error status.
    """
    if isinstance(desired_state, int):
        if desired_state < 0 or desired_state > 10:
            raise TypeError("desired_state provided is not an known state.")
        desired_state = allowed_states[desired_state]
        print("Converted int, waiting for: ", desired_state)

    if desired_state not in allowed_states:
        raise TypeError("desired_state provided is not an known state.")
    spinL = 0
    poll = 1
    while desired_state not in str(device.obsState.name):
        if spinL < len(spinner) - 1:
            spinL += 1
        else:
            spinL = 0
        sleep(0.5)
        print(
            "\r",
            f"{spinner[spinL]} Poll# {poll}: {device.obsState.name}, \
            waiting for {desired_state}...",
            end="",
        )
        if device.obsState == 9 and break_on_error:
            break
        poll += 1
    print("\r", "---------------------------------------------", end="")
    print(f"\nFinished with: {device.obsState.name}")


def wait_for_status(device: DeviceProxy, desired_status: str) -> None:
    """Poll a tango device to wait until a desired status is reached, eg.ON
    Arguments:
    device -- Tango Device to check
    desired_state -- The status which to break upon getting (number or state)
    """
    spinL = 0
    poll = 1
    while desired_status not in str(device.status()):
        if spinL < len(spinner) - 1:
            spinL += 1
        else:
            spinL = 0
        sleep(0.5)
        print(
            "\r",
            f"{spinner[spinL]} Poll {poll}: Device is currently {device.status()},\
            waiting for {desired_status}...",
            end="",
        )
        poll += 1
    print("\r", "-------------------------------------", end="")
    print(f"\nFinished with: {device.status()}")


class EventWaitTimeout(Exception):
    """ Exception raised when a an event does not occur within a specified timeout"""

def wait_for_event(
    device_proxy: DeviceProxy,
    attr_name: str,
    desired_value: Any,
    event_type: EventType = EventType.CHANGE_EVENT,
    timeout: float = 150.0,
    print_event_details: bool = False,
) -> bool:
    """Wait for a specific type of attribute event to occur and check that the attribute
    changed to a specific value.

    :param device_proxy: Device proxy to be used for event subscription
    :type device_proxy: DeviceProxy
    :param attr_name: Attribute of interest
    :type attr_name: str
    :param desired_value: Expected value for attribute specified with attr_name
    :type desired_value: Any
    :param event_type: Tango event type to wait for
    :type event_type: EventType
    :param timeout: Maximum period in [s] to wait for desired event, defaults to 150.0
    :type timeout: float, optional
    :param print_event_details: Toggle printing of event data structure, defaults to False
    :type print_event_details: bool, optional
    :return: Success or failure flag indicating whether the attribute changed as desired or not
    :rtype: Bool
    """
    result = False

    event_queue = Queue()

    event_id = device_proxy.subscribe_event(attr_name, event_type, event_queue.put)

    time_start = time()
    while (time() - time_start) < timeout:
        if not event_queue.empty():
            try:
                event = event_queue.get(timeout=2)
                if print_event_details:
                    print(f"Received event: {event}")
                assert not event.err, "Event error"

                value = event.attr_value.value
                if value == desired_value:
                    print(
                        f"Device {device_proxy.name()} attribute {attr_name} changed "
                        f"to the following desired value: {desired_value}"
                    )
                    result = True
                    break
            except Empty:
                print("Event queue empty")

    device_proxy.unsubscribe_event(event_id)

    if not result:
        raise EventWaitTimeout("Desired event did not occur within the"
                               f"timeout period of {timeout}s")
    return result
