""" Helper functions to make checking device status and state neater."""

from time import sleep

from tango import DeviceProxy

spinner = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]


def wait_for_state(device: DeviceProxy, desired_state, break_on_error=True) -> None:
    """Poll a tango device until either the given observation state is reached, or it throws an error.
    Arguments:
    device -- Tango Device to check
    desired_state -- The state which to break upon getting (number or state)
    break_on_error -- If set to False, will keeping running when getting an error status.
    """
    spinL = 0
    poll = 1
    while device.obsState != desired_state:
        if spinL < len(spinner) - 1:
            spinL += 1
        else:
            spinL = 0
        sleep(0.5)
        print(
            "\r",
            f"{spinner[spinL]} Poll# {poll}: Current state is {device.obsState.name}, waiting for {desired_state}...",
            end="",
        )
        if device.obsState == 9 and break_on_error:
            break
        poll += 1
    print("\r", "-------------------------------------", end="")
    print(f"\nFinished with: {device.obsState.name}")


def wait_for_status(device: DeviceProxy, desired_status) -> None:
    """Poll a tango device to wait until a desired status is reached, eg.ON
    Arguments:
    device -- Tango Device to check
    desired_state -- The status which to break upon getting (number or state)
    """
    spinL = 0
    poll = 1
    while device.status() != desired_status:
        if spinL < len(spinner) - 1:
            spinL += 1
        else:
            spinL = 0
        sleep(0.5)
        print(
            "\r",
            f"{spinner[spinL]} Poll {poll}: Current status is {device.status()}, waiting for {desired_status}...",
            end="",
        )
        poll += 1
    print("\r", "-------------------------------------", end="")
    print(f"\nFinished with: {device.status()}")
