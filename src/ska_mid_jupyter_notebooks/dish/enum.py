"""Stuff used for dish data."""

# Taken from
# https://gitlab.com/ska-telescope/ska-mid-dish-manager/-/blob/main/src/ska_mid_dish_manager/models/dish_enums.py
# Unfortunately, due to version incompatibilities we cannot pull this in directly.
import enum


class DishMode(enum.IntEnum):
    """Values for dish mode."""

    STARTUP = 0
    SHUTDOWN = 1
    STANDBY_LP = 2
    STANDBY_FP = 3
    MAINTENANCE = 4
    STOW = 5
    CONFIG = 6
    OPERATE = 7
    UNKNOWN = 8


class SPFOperatingMode(enum.IntEnum):
    """Values for SPF operating mode."""

    UNKNOWN = 0
    STARTUP = 1
    STANDBY_LP = 2
    OPERATE = 3
    MAINTENANCE = 4
    ERROR = 5


class SPFRxOperatingMode(enum.IntEnum):
    """Values for SPF receiver."""

    # enums are from ICD
    UNKNOWN = 0
    STARTUP = 1
    STANDBY = 2
    DATA_CAPTURE = 3
    CONFIGURE = 4
    MAINTENANCE = 5


class DSOperatingMode(enum.IntEnum):
    """Values for DS operating mode."""

    # enums are from dish lmc
    UNKNOWN = 0
    STARTUP = 1
    STANDBY_LP = 2
    STANDBY_FP = 3
    MAINTENANCE = 4
    STOW = 5
    ESTOP = 6
    POINT = 7


class PointingState(enum.IntEnum):
    """Values for pointing state."""

    READY = 0
    SLEW = 1
    TRACK = 2
    SCAN = 3
    UNKNOWN = 4


class Band(enum.IntEnum):
    """Values for band."""

    NONE = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    # pylint: disable=invalid-name
    B5a = 5
    B5b = 6
    UNKNOWN = 7


class IndexerPosition(enum.IntEnum):
    """Values for indexer position."""

    UNKNOWN = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5 = 5
    MOVING = 6
    ERROR = 7


class BandInFocus(enum.IntEnum):
    """Values for band in focus."""

    UNKNOWN = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5 = 5


# pylint: disable=invalid-name
class SPFBandInFocus(enum.IntEnum):
    """Values for SPF band in focus."""

    UNKNOWN = 0
    B1 = 1
    B2 = 2
    B3 = 3
    B4 = 4
    B5a = 5
    B5b = 6


class TrackInterpolationMode(enum.IntEnum):
    """Values for track interpolation mode."""

    NEWTON = 0
    SPLINE = 1


class TrackProgramMode(enum.IntEnum):
    """Values for track program mode."""

    TABLEA = 0
    TABLEB = 1
    POLY = 2


class TrackTableLoadMode(enum.IntEnum):
    """Values for track table load mode."""

    NEW = 0
    APPEND = 1
    RESET = 2


class PowerState(enum.IntEnum):
    """Values for power state."""

    UPS = 0
    LOW = 1
    FULL = 2


class SPFPowerState(enum.IntEnum):
    """Values for SPF power state."""

    # enums are from ICD
    UNKNOWN = 0
    LOW_POWER = 1
    FULL_POWER = 2


class DSPowerState(enum.IntEnum):
    """Values for DS power state."""

    # enums are from ICD
    OFF = 0
    UPS = 1
    FULL_POWER = 2
    LOW_POWER = 3
    UNKNOWN = 4


class CapabilityStates(enum.IntEnum):
    """Values for capability states."""

    UNAVAILABLE = 0
    STANDBY = 1
    CONFIGURING = 2
    OPERATE_DEGRADED = 3
    OPERATE_FULL = 4
    UNKNOWN = 5


class SPFCapabilityStates(enum.IntEnum):
    """Values for SPF capability states."""

    UNAVAILABLE = 0
    STANDBY = 1
    OPERATE_DEGRADED = 2
    OPERATE_FULL = 3


class SPFRxCapabilityStates(enum.IntEnum):
    """Values for SPF Rx capability states."""

    UNKNOWN = 0
    UNAVAILABLE = 1
    STANDBY = 2
    CONFIGURE = 3
    OPERATE = 4
