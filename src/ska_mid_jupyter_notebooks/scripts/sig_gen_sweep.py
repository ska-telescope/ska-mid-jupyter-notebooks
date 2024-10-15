#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Ben / Vhuli / Monde
@Date: xx-09-2022
@Affiliation: Test Engineer
@Functional Description:
    1. This script provides for setup of a frequency sweep on the SMB100A Signal Generator.
    2. Run the script by parsing the following arguments on the terminal (values are examples):
        - start frequency = 100000000 or 100e6, integer with no units [100 MHz]
        - stop frequency = 2000000000 or 2e9, integer with no units [2 GHz]
        - step frequency = 100000000 or 100e6, integer with no units [100 MHz]
        - dwell time = 1000, integer with no units [ms]
@Notes:
    1. This script was originally written for the SMB100A Signal Generator and MS2090A Spectrum Analyzer.
        Raw ethernet socket communication is used
        and thus VISA library/installation is not required
    2. This script uses scpi protocol for the automatic test equipment intended

@Revision: 1
@Modifier: Dave @Date xx-10-2024(copied from revision 1 in mid-itf repo - spectrum analyser part commented out, left other details unchanged)
'''
import time

from ska_mid_jupyter_notebooks.scripts.scpi_database import SGCmds

# Import the Signal Generator Socket class
from ska_mid_jupyter_notebooks.scripts.sg_smb100a_generate_frequency_sweep_2 import SG_SOCK

# -----------------Connection Settings----------------------
SG_PORT = 5025                    # default SMB R&S port
SG_HOST = '10.165.3.1'             # smb100a signal generator
SG_ADDRESS = (SG_HOST, SG_PORT)
# ----------------Constants---------------
DEFAULT_TIMEOUT = 1        # Default socket timeout
RF_OFF = 0
RF_ON = 1

SHORT_DELAY = 0.1
LONG_DELAY = 1
#-------------------SG_SMB100A Setup-------------------------#
def setupSG():
    print('/------Setup signal generator Class---------/\n')
    SG = SG_SOCK()                                 # Call main class
    SG.connectSG(SG_ADDRESS)
    print(f'Connected to: {SG.getSGCmd(SGCmds["device_id"]).decode()}')
    SG.setSGCmd(SGCmds['rf_state'], RF_ON)
    SG.setSGCmd(SGCmds['power'], -25)
    print('/------End of Setup signal generator---------/\n\n')
    return SG

def run_sig_gen_sweep(start_freq, stop_freq, dwel_time, step_freq):

    print('\n/--------- Running sig gen sweep ---------/')
    sg = setupSG()
    time.sleep(1)

    # Set Sig Gen to start freq, stop freq, step freq and dwell time
    print("/------Setup Signal Generator Sweep Parameters... ---------/")

    '''
        The following block of code generates a sweep frequency of the signal generator
        at 100MHz step
        @params:
            start_freq      : start frequency in Hz (not less than 9 kHz)
            stop_freq       : stop frequency in Hz (not more than 6 GHz)
            step_freq       : step frequency in Hz (default = 100 MHz)
            dwel_time       : duration of frequency output in ms (default=1000 ms)
        '''
    # 1. Select sweep mode, sweep trigger and freq mode
    sg.setSGCmd(SGCmds['sweep_freq_mode'], 'AUTO')
    sg.setSGCmd(SGCmds['sweep_freq_trig'], 'SING')
    sg.setSGCmd(SGCmds['freq_mode'], 'SWE')


    # 2. Set and Display SG start frequency
    sg.setSGCmd(SGCmds["start_freq"], start_freq)
    start_freq_recvd = sg.getSGCmd(SGCmds["start_freq"]).decode()
    print(f'Signal Generator Start Frequency = {float(start_freq_recvd) / 1e9} GHz')

    # 3. Set and Display SG stop frequency
    sg.setSGCmd(SGCmds["stop_freq"], stop_freq)
    stop_freq_recvd = int(sg.getSGCmd(SGCmds["stop_freq"]).decode())
    print(f'Signal Generator Stop Frequency = {float(stop_freq_recvd) / 1e9} GHz')

    # 4. Select linear or logarithmic spacing
    sg.setSGCmd(SGCmds['sweep_freq_spac_conf'], 'LIN')

    # 5. Set the step width and dwell time
    sg.setSGCmd(SGCmds['sweep_freq_step'], f'{step_freq}')
    step_freq_recvd = int(float(sg.getSGCmd(SGCmds['sweep_freq_step']).decode()))
    print(f"Step Frequency = {step_freq_recvd / 1e9} GHz")

    sg.setSGCmd(SGCmds['sweep_freq_dwell'], f'{dwel_time}')
    dwell_time_recvd = (float(sg.getSGCmd(SGCmds['sweep_freq_dwell']).decode()))
    print(f"Dwell time = {dwell_time_recvd} s")

    # 6. Turn off sig gen display updates
    time.sleep(1)
    #sg.setSGCmd(SGCmds['display-update'], 'OFF')
    time.sleep(1)
    # 7. Trigger the sweep
    sg.setSGCmd(SGCmds['sweep_freq_exec'])
    sg.setSGCmd(SGCmds['trigger_freq_sweep_imm'])
    print('Executing sweep...')


# ----------------End of Signal Generator Setup Sweep Parameters -----------------------

    # Wait until the sweep is finished
    run_time_delay = int((float(stop_freq) - float(start_freq)) * (float(dwel_time) / float(step_freq)))
    print (f"run time delay = {run_time_delay}")
    for count in range(0, run_time_delay, 10):
        print (f"count = {count}")
        time.sleep(10)          # wait for sweep to complete
        # print(f'count = {count}...')
        print('Sweeping...')
        # current_freq = sg.getSGCmd(SGCmds['current_freq'])
        # set_marker_freq = sa.setSACmd((SACmds['marker_frequency']), current_freq)
        # marker_freq_pow = sa.getSACmd(SACmds['marker_power'])
    print ("sweep should be finished")

    # 8. Turn back on sig gen display updates
    #sg.setSGCmd(SGCmds['display-update'], 'ON')
