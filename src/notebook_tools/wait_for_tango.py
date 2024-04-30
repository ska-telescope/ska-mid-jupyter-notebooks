""" Helper functions to make running notebooks simpler and easier."""
from time import sleep

def wait_for_state(device, desired_state, break_on_error=True):
    """Poll a tango device until either the given observation state is reached, or it throws an error.
    Arguments:
    device -- Tango Device to check
    desired_state -- The state which to break upon getting (number or state)
    break_on_error -- If set to False, will keeping running when getting an error status.
    """
    print(f"State: {device.obsState.name}")
    while device.obsState != desired_state:
        print(f"State: {device.obsState.name}")
        sleep(0.5)
        if device.obsState == 9 and break_on_error:
            break
    print(f"State: {device.obsState.name}")

def wait_for_status(device, desired_status):
    """Poll a tango device to wait until a desired status is reached, eg.ON
    Arguments:
    device -- Tango Device to check
    desired_state -- The status which to break upon getting (number or state)
    """
    while device.status() != desired_status:
        print(f"State: {device.status()}")
        sleep(0.5)
    print(f"State: {device.status()}")