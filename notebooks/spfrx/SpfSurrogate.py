#!/usr/bin/env python3
from labjack import ljm
import time

MODE_INDEPENDENT = 0
MODE_COMBINED    = 1
CHANNEL_H        = 0
CHANNEL_V        = 1
SRC_SIG_GEN      = 0
SRC_NOISE        = 1

class SPFSurrogate:

    CTRL_RELAY    = "EIO4"
    CTRL_SIG_GEN  = "EIO3"
    CTRL_SRC      = "EIO2"
    CTRL_BAND     = ["EIO1", "EIO0"]

    def __init__(self, ip: str):

        self.handle = ljm.openS('T4', 'Ethernet', ip)
        info = ljm.getHandleInfo(self.handle)

        # If the FIO/EIO line is an analog input, it needs to first be changed to a
        # digital I/O by reading from the line or setting it to digital I/O with the
        # DIO_ANALOG_ENABLE register.
        for bit in [self.CTRL_RELAY, self.CTRL_SIG_GEN, self.CTRL_SRC,
                    self.CTRL_BAND[0], self.CTRL_BAND[1]]:
            ljm.eReadName(self.handle, bit)
            ljm.eWriteName(self.handle, bit, 0)

    def enableNoiseSource(self, enable: bool):
        logic = 0

        if enable:
            logic = 1
        
        ljm.eWriteName(self.handle, self.CTRL_RELAY, logic)

    def setSignalSource(self, mode):

        if mode == "SINE":
            ljm.eWriteName(self.handle, self.CTRL_RELAY,   0)
            ljm.eWriteName(self.handle, self.CTRL_SIG_GEN, 0)
            ljm.eWriteName(self.handle, self.CTRL_SRC,     0)
        elif mode == "DUALSINE":
            ljm.eWriteName(self.handle, self.CTRL_RELAY,   0)
            ljm.eWriteName(self.handle, self.CTRL_SIG_GEN, 1)
            ljm.eWriteName(self.handle, self.CTRL_SRC,     0)
        elif mode == "NOISE":
            ljm.eWriteName(self.handle, self.CTRL_RELAY,   1)
            ljm.eWriteName(self.handle, self.CTRL_SIG_GEN, 0)
            ljm.eWriteName(self.handle, self.CTRL_SRC,     1)
        elif mode == "NOISEOFF":
            ljm.eWriteName(self.handle, self.CTRL_RELAY,   0)
            ljm.eWriteName(self.handle, self.CTRL_SIG_GEN, 0)
            ljm.eWriteName(self.handle, self.CTRL_SRC,     1)
        else:
            raise ValueError(mode)

    def setBand(self, band):
        if band == 1:
            ljm.eWriteName(self.handle, self.CTRL_BAND[0], 0)
            ljm.eWriteName(self.handle, self.CTRL_BAND[1], 0)
        elif band == 2:
            ljm.eWriteName(self.handle, self.CTRL_BAND[0], 0)
            ljm.eWriteName(self.handle, self.CTRL_BAND[1], 1)
        elif band == 3:
            ljm.eWriteName(self.handle, self.CTRL_BAND[0], 1)
            ljm.eWriteName(self.handle, self.CTRL_BAND[1], 0)
        else:
            raise ValueError(band)


    def __del__(self):
        # Close handle
        ljm.close(self.handle)


if __name__ == '__main__':

    import sys
    env = EnviroControl('192.168.74.7')

    env.setTemp(float(sys.argv[1]))
    for i in range(1000):
        print('Current Temp is %.2f' %(env.getTemp()))
        time.sleep(2)
    del env