# pylint: disable=C,R
from typing import Literal

SubarrayResourceState = Literal["EMPTY", "RESOURCING", "COMPOSED"]
SubarrayConfigurationState = Literal["NOT_CONFIGURED", "CONFIGURING", "READY"]
SubarrayScanningState = Literal["NOT_SCANNING", "SCANNING"]
