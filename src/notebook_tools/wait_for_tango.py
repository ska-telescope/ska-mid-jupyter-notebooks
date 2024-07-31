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


def wait_for_state(device: DeviceProxy, desired_state: str, break_on_error: bool = True) -> None:
    """
    Poll a tango device until given observation state is reached, or throw an error.

    :param device: Tango Device to check
    :param desired_state: state which to break upon getting (number or state)
    :param break_on_error: if set to False, will keep running when getting an error status.
    """
    if desired_state not in allowed_states:
        raise TypeError("desired_state provided is not an known state.")
    spin_l = 0
    poll = 1
    while desired_state not in str(device.obsState.name):
        if spin_l < len(spinner) - 1:
            spin_l += 1
        else:
            spin_l = 0
        sleep(0.5)
        print(
            "\r",
            f"{spinner[spin_l]} Poll# {poll}: {device.obsState.name},"
            f" waiting for {desired_state}...",
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
    spin_l = 0
    poll = 1
    while desired_status not in str(device.status()):
        if spin_l < len(spinner) - 1:
            spin_l += 1
        else:
            spin_l = 0
        sleep(0.5)
        print(
            "\r",
            f"{spinner[spin_l]} Poll {poll}: Device is currently {device.status()},"
            f" waiting for {desired_status}...",
            end="",
        )
        poll += 1
    print("\r", "-------------------------------------", end="")
    print(f"\nFinished with: {device.status()}")
