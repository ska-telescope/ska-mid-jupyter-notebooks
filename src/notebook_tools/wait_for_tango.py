""" Helper functions to make checking device status and state neater."""

from time import sleep

from tango import DeviceProxy

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


def wait_for_state(device: DeviceProxy, desired_state: str, break_on_error=True) -> None:
    """Poll a tango device until either the given observation state is reached, or it throws an error.
    Arguments:
    device -- Tango Device to check
    desired_state -- The state which to break upon getting (number or state)
    break_on_error -- If set to False, will keeping running when getting an error status.
    """
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
            f"{spinner[spinL]} Poll# {poll}: {device.obsState.name}, waiting for {desired_state}...",
            end="",
        )
        if device.obsState == 9 and break_on_error:
            break
        poll += 1
    print("\r", "-------------------------------------", end="")
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
            f"{spinner[spinL]} Poll {poll}: Device is currently {device.status()}, waiting for {desired_status}...",
            end="",
        )
        poll += 1
    print("\r", "-------------------------------------", end="")
    print(f"\nFinished with: {device.status()}")
