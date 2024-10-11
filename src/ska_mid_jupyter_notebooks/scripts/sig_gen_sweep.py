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
import sys, os, socket
# import os
import time
import argparse
#import matplotlib.pyplot as plt

#sys.path.insert(0, os.path.abspath(os.path.join('..') + '/scripts/'))
#sys.path.append('.')
sys.path.append (os.path.join('/home/daveh/ska_mid_jupyter_notebooks/src/ska_mid_jupyter_notebooks/scripts/'))

from sg_smb100a_generate_frequency_sweep_2 import SG_SOCK # Import the Signal Generator Socket class from sig_gen folder

#%%
#-----------------------import libraries for Spectrum analyzer----------------#
#sys.path.insert(0, os.path.abspath(os.path.join('..') + '/spec_ana/ms2090a/'))
#from sa_ms2090a_set_maxhold_read_trace_1 import SA_SOCK        # Import the Spectrum Analyser Socket Function

#--------Import scpi database for Signal Generator and Spectrum analyzer ----------#
sys.path.insert(1, os.path.abspath(os.path.join('../../') + '/resources/'))
from scpi_database import SGCmds
#from scpi_database import SACmds

# -----------------Connection Settings----------------------
SG_PORT = 5025                    # default SMB R&S port 
SG_HOST = '10.20.7.1'             # smb100a signal generator IP
SG_ADDRESS = (SG_HOST, SG_PORT)
#SA_HOST = '10.20.7.4'             # Anritsu spectrum analyzer IP temporary
#SA_PORT = 9001                    # Anritsu spectrum analyzer port 18? 23?
#SA_ADDRESS = (SA_HOST, SA_PORT)
#-----------------------------------------------------------
# ----------------Constants---------------    
DEFAULT_TIMEOUT = 1        # Default socket timeout
RF_OFF = 0
RF_ON = 1

SHORT_DELAY = 0.1
LONG_DELAY = 1

#-----------------SA initialization Variables----------
NUMPOINTS = 631     # Number of measurement points (Max=625)
RBW = 3e6           # Resolution BW of spectrum analyser
VBW = 3e6           # Video BW of spectrum analyser
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
#------------------------SA_MS2090A Setup-------------------------#
# def setupSA():
#     print('/------Setup spectrum analyser---------/')
#     SA = SA_SOCK()
#     SA.connectSA((SA_ADDRESS))
#     SA.setSACmd(SACmds['reset_device'])
#     SA.setSACmd(SACmds['start_freq'], args.start_freq)
#     SA.setSACmd(SACmds['stop_freq'], args.stop_freq)
#     SA.setSACmd(SACmds['sweep_points'], NUMPOINTS)
#     SA.setSACmd(SACmds['rbw_auto'], 'off')
#     SA.setSACmd(SACmds['vbw_auto'], 'off')
#     SA.setSACmd(SACmds['att_level'], 10)
#     SA.setSACmd(SACmds['ref_level'], -10)
#     # SA.setSACmd(SACmds['det_auto_state'], 'OFF')
#     SA.setSACmd(SACmds['det_mode'], 'RMS') 
#     SA.setSACmd(SACmds['trace1_mode'], 'MAX')
#     # SA.setSACmd(SACmds['max_hold_state'], 'ON')
#     SA.setSACmd(SACmds['marker1-state'], 'ON')

#     print('/------End of Setup Spectrum Analyzer---------/\n\n')
#     return SA
        
#------------------------------ PLOT ---------------------------#
# def plotTrace(freq_values, power_values, ref_level): 
#     ''' Plot response

#     This function plots the power vs frequency filter response 

#     @params:    
#         freq_values: integer list [in Hz]
#         power_value: integer list [in dBm]
#     '''
#     x_axis = freq_values
#     y_axis = power_values
#     print(f'x_axis before plot = {x_axis}')
#     print(f'y_axis before plot = {y_axis}')
#     plt.plot(x_axis, y_axis)
#     plt.xlabel('Frequency in GHz')
#     plt.ylabel('Power in dBm')
#     plt.title('Sweep Maxhold Plot')
#     plt.ylim(-110, ref_level)
#     plt.show()
   
# Main program
# -----------------------------------------------------------------------------   
if __name__ == '__main__':
    # Set up arguments to be parsed 
    parser = argparse.ArgumentParser(description = 'Specify Start and Stop Frequency')
    parser.add_argument('start_freq', type = str, help = 'the start frequency incl. units (Hz)')
    parser.add_argument('stop_freq', type = str, help = 'the stop frequency incl. units (Hz)')
    parser.add_argument('step_freq', type = str, help = 'the step frequency incl. units (Hz)')
    parser.add_argument('dwel_time', type = float, help = 'the sweep dwell time (ms)')
    args = parser.parse_args()

    print('\n/--------- Running main Code ---------/') 
    sg = setupSG()
    time.sleep(1) 
 #   sa = setupSA()
 #   time.sleep(1) 

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
    # Set and Display SG start frequency
    sg.setSGCmd(SGCmds["start_freq"], args.start_freq)
    start_freq_recvd = sg.getSGCmd(SGCmds["start_freq"]).decode()
    print(f'Signal Generator Start Frequency = {float(start_freq_recvd) / 1e9} GHz') 

    # Set and Display SG stop frequency
    sg.setSGCmd(SGCmds["stop_freq"], args.stop_freq)
    stop_freq_recvd = int(sg.getSGCmd(SGCmds["stop_freq"]).decode())
    print(f'Signal Generator Stop Frequency = {float(stop_freq_recvd) / 1e9} GHz')

    centFreq = (int(float(args.start_freq)) + int(float(args.stop_freq))) / 2
    span = int(float(args.stop_freq)) - int(float(args.start_freq))    
    span_recvd = int(sg.getSGCmd(SGCmds['span_freq']).decode())
    print(f"Sweep Span = {span_recvd / 1e9} GHz")

        # 1. Set the sweep range
    sg.setSGCmd(SGCmds['cent_freq'], centFreq)
    centFreq_recvd = int(sg.getSGCmd(SGCmds['cent_freq']).decode())
    print(f"Sweep Center Frequency = {centFreq_recvd / 1e9} GHz")
    sg.setSGCmd(SGCmds['span_freq'], span)

        # 2. Select linear or logarithmic spacing
    sg.setSGCmd(SGCmds['sweep_freq_spac_conf'], 'LIN')

        # 3. Set the step width and dwell time
    sg.setSGCmd(SGCmds['sweep_freq_step'], f'{args.step_freq}')
    step_freq_recvd = int(float(sg.getSGCmd(SGCmds['step_freq']).decode()))
    print(f"Step Frequency = {step_freq_recvd / 1e9} GHz")
    sg.setSGCmd(SGCmds['sweep_freq_dwell'], f'{args.dwel_time}')

        # 4. Select the trigger mode
    sg.setSGCmd(SGCmds['sweep_freq_trig'], 'SING')

        # 5. Select sweep mode and activate the sweep
    sg.setSGCmd(SGCmds['sweep_freq_mode'], 'AUTO')
    sg.setSGCmd(SGCmds['freq_mode'], 'SWE')

        # 6. Trigger the sweep     
    sg.setSGCmd(SGCmds['sweep_freq_exec'])
    print('Executing sweep...')
# ----------------End of Signal Generator Setup Sweep Parameters -----------------------

    # Wait until the sweep is finished
    run_time_delay = int((float(args.stop_freq) - float(args.start_freq)) * (float(args.dwel_time) / float(args.step_freq)))
    for count in range(0, run_time_delay, 10):
        time.sleep(10)          # wait for sweep to complete  
        # print(f'count = {count}...')
        print('Sweeping...')
        # current_freq = sg.getSGCmd(SGCmds['current_freq'])
        # set_marker_freq = sa.setSACmd((SACmds['marker_frequency']), current_freq)
        # marker_freq_pow = sa.getSACmd(SACmds['marker_power'])
    print ("sweep should be finished")

    # ''' Read trace data
        
    # This block of code reads the power trace data and calculates the 
    # trace frequency points

    # '''         
    
    # freq_values = []
    # power_values = [] 

    # # Read and print Spectrum Analyzer start frequency
    # start_freq = sa.getSACmd(SACmds["start_freq"])
    # print(f'Spectrum Analyzer Start Frequency = {float(start_freq) / 1e6} MHz') 

    # # Read and print SA stop frequency
    # stop_freq = int(sa.getSACmd(SACmds["stop_freq"]).decode())
    # print(f'Spectrum Analyzer Stop Frequency = {float(stop_freq) / 1e9} GHz')

    # # Confugure trace data format to be Ascii
    # sa.setSACmd(SACmds['data_format'], 'ASC')
    # print('Trace data formatted to Ascii')   

    # # Set single sweep
    # sa.setSACmd((SACmds['sing_sweep_state']), 'OFF')

    # # --------------- Get trace data power values ------------------  
    # # sa.getSACmd((SACmds['trace_data']), 1)     # Command not working, replaced by the chunk of code below
    # sa.sendall(bytes('TRACE:DATA? 1\n', encoding = 'utf8'))
    # time.sleep(SHORT_DELAY)
    # try:
    #     return_str = sa.recv(8092)
    # except socket.timeout:
    #     raise StopIteration('No data received from instrument') 
    # #print(f'return_str = {return_str} and return_str type = {type(return_str)}\n')
    # # -------------------- End of trace data power values reading -------


    # # --------------- Trace data power values conditioning -------------------
    # power_data = return_str
    # power_data = power_data.decode()
    # #print(f'decoded power_data = {power_data} and power_data type = {type(power_data)}\n')
    # power_data = str(power_data)
    # power_data = power_data.split(',')              # Makes variable a list
    # #print(f'decode list power_data = {power_data}')
    # power_data.pop(0)
    # power_data = [float(x) for x in power_data]
    # #print(f'final list power_data = {power_data} and power_data type = {type(power_data)}')
    
    # No_of_Sweep_Points = int(sa.getSACmd(SACmds['sweep_points']).decode())   # Get No. of Sweep Points
    # #print(f'No of Sweep Points = {No_of_Sweep_Points}, No_of_Sweep_Points type = {type(No_of_Sweep_Points)}')
    # #for s in power_data:
    # #    power_values.append(power_data)
    # power_values = power_data
    # # -------------------- End of trace data power values conditioning -------

    # #freq_step_size = int((float(args.stop_freq) - int(float(args.start_freq))) / (No_of_Sweep_Points - 1))
    # freq_step_size = int((float(args.stop_freq) - float(args.start_freq)) / (No_of_Sweep_Points))
    # for i in range(0, (No_of_Sweep_Points - 1), 1):
    #     freq_values.append(int(float(args.start_freq)) + (i * freq_step_size))

    # #print(f'final list freq_values = {freq_values} and freq_values type = {type(freq_values)}')

    # #print(f'length of freq_values = {len(freq_values)} and length of power_values = {len(power_values)}')    
    # print('Power and Frequency Values acquired...')

    # ref_level = int(sa.getSACmd(SACmds['ref_level']).decode())
    # print(f'Ref Level = {ref_level}')

    # plotTrace(freq_values, power_values, ref_level)

    # # sg.setSGCmd(SGCmds['rf_state'], RF_OFF)
    # sg.closeSGSock()
    # sa.closeSASock()

    # # plotTrace(freq_values, power_values)
    
    # print('Displayed plot...')
    # print('End of program.')
