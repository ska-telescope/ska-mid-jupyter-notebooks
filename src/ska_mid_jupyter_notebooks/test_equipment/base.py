from typing import Literal

TestDevice = Literal[
    "mid-itf/awg/1",
    "mid-itf/siggen/1",
    "mid-itf/skysimctl/4",
    "mid-itf/spectana/1",
    "mid-itf/progattenuator/1",
]

DeviceDevState = Literal["ON", "ERROR", "DISABLE", "OFF", "UNKNOWN", "FAULT", "ALARM"]
