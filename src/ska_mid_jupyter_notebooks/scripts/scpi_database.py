#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ben/Vhuli/Monde 
@Date: 26-09-2022
@Affiliation: Test Engineers
@Functional Description: 
    - This script implements a look-up-table that maps MID ITF Test Equipment SCPI commands to natural
      language for the ease of readability.
    - The mapping is implemented as dictionary key-value pairs
 
@Revision: 1
"""

# Signal Generator Commands

SGCmds = {
    # Common commands
    'reset_device': '*RST', 
    'device_id': '*IDN',
    'oper_complete': '*OPC',
    'clear_status': '*CLS',

    # Frequency Commands
    'start_freq': 'SOUR:FREQ:STAR',         # pass start frequency e.g. SOUR:FREQ:STAR 100e6 
    'stop_freq': 'SOUR:FREQ:STOP',          # pass stop frequency e.g. SOUR:FREQ:STOP 2e9 Hz
    'step_freq': 'SOUR:FREQ:STEP',           # pass step frequency e.g. SOUR:FREQ:STEP 100e6 
    'current_freq': 'FREQ',                  # pass single FREQ value e.g. FREQ 2e9 Hz
    'cent_freq': 'FREQ:CENT',                # pass center freq FREQ:CENT {centFreq} Hz 
    'span_freq': 'FREQ:SPAN',                # pass span freq e.g. FREQ:SPAN {span} Hz
    'freq_mode': 'SOUR:FREQ:MODE',           # pass freq mode e.g. SOUR:FREQ:MODE SWE

    # Sweep Settings Commands
    'sweep_freq_mode': 'SWE:FREQ:MODE',      # pass sweep mode e.g. SWE:FREQ:MODE AUTO
    
    'sweep_freq_spac_conf': 'SWE:FREQ:SPAC', # pass sweep freq spacing e.g. SWE:FREQ:SPAC LIN
    'sweep_freq_step': 'SWE:FREQ:STEP:LIN',  # pass sweep step freq e.g. SWE:FREQ:STEP:LIN {step_freq}
    'sweep_freq_dwell': 'SWE:FREQ:DWEL',     # pass sweep dwell time SWE:FREQ:DWEL {dwel_time}
    'sweep_freq_trig': 'TRIG:FSW:SOUR',      # pass freq sweep trig e.g. TRIG:FSW:SOUR SING
    'sweep_freq_exec': 'SWE:FREQ:EXEC', # no paramater passed

    # RF 
    'rf_state': 'OUTP',

    # Power
    'power': 'POW',
    'set_start_pow': 'SOUR:POW:STAR',

    # Display Settings
    'display-update': 'SYST:DISP:UPD',          # pass ON / OFF parameter e.g. SYSTem:DISPlay:UPDate OFF 

}

# Spectrum Analyzer Commands

SACmds = {
    # Common commands
    'reset_device': '*RST', 
    'device_id': '*IDN',
    'oper_complete': '*OPC',
    'clear_status': '*CLS',

    # Frequency Commands
    'start_freq': ':FREQ:STAR',
    'stop_freq': ':FREQ:STOP',

    # Bandwidth Commands
    'res_bw': 'BAND:RES',               # pass rbw value e.g. BAND:RES 30e3
    'vid_bw': 'BAND:VID',               # pass rbw value e.g. BAND:VID 30e3 
    'rbw_auto': 'BAND:RES:AUTO',        # pass rbw value e.g. BAND:RES:AUTO off
    'vbw_auto': 'BAND:VID:AUTO',        # pass rbw value e.g. BAND:VID:AUTO off 

    # Amplitude Commands
    'ref_level': 'DISP:WIND:TRAC:Y:SCAL:RLEV',  # pass reflevel value e.g. DISP:WIND:TRAC:Y:SCAL:RLEV -30
    
    # Power Commands
    'att_level': 'POW:RF:ATT',                  # pass atten. level value e.g. POW:RF:ATT 10 
    
    # Sweep Commands
    'sweep_points': 'DISP:POIN',            # pass number of sweep points e.g. DISP:POIN 631
    'sing_sweep_state': 'INIT:CONT',        # pass single sweep state e.g. INIT:CONT OFF

    # System Settings Commands
    'device_mode': 'MODE',                  # pass device mode e.g. MODE SPEC for spectrum analyzer

    # Trace Commands
    'trace': 'TRACE',                           # read trace, no param require 
    'trace_data': 'TRACE:DATA',                 # pass trace no. parameter e.g. TRACE:DATA? 1
    'trace1_state': 'DISP:TRAC1',               # pass trace no. and state e.g. DISP:TRAC1 ON
    'trace1_mode': 'TRACE1:TYPE',               # pass trace mode e.g. TRACE1:TYPE MAX
    'max_hold_state': 'MAXH:STAT',              # pass maxhold state parameter e.g. MAXH:STAT ON
    'scale_per_div': 'DISP:WIND:TRACE:Y:PDIV',  # pass scale / div parameter e.g. DISP:WIND:TRACE:Y:PDIV 5
    
    # Detector commands
    'det_auto_state': 'DET:AUTO',           # pass ON or OFF e.g. DET:AUTO OFF
    'det_mode': 'DET',                      # pass APE, RMS e.g. DET APE      

    # Data commands
    'data_format': 'FORM:DATA',             # pass data format mode e.g.FORM:DATA ASC
    'marker1_state': 'CALC:MARK1:STAT',     # pass marker state e.g. CALCulate:MARKer<n>:STATe OFF
    'marker2_state': 'CALC:MARK2:STAT',     # pass marker state e.g. CALCulate:MARKer<n>:STATe OFF
    'marker3_state': 'CALC:MARK3:STAT',     # pass marker state e.g. CALCulate:MARKer<n>:STATe OFF
    'marker4_state': 'CALC:MARK4:STAT',     # pass marker state e.g. CALCulate:MARKer<n>:STATe OFF
    'marker5_state': 'CALC:MARK5:STAT',     # pass marker state e.g. CALCulate:MARKer<n>:STATe OFF
    'marker6_state': 'CALC:MARK6:STAT',     # pass marker state e.g. CALCulate:MARKer<n>:STATe OFF
    'marker1_frequency': 'CALC:MARK1:X',     # pass frequency value e.g. CALC:MARK1:X 10 MHz
    'marker2_frequency': 'CALC:MARK2:X',     # pass frequency value e.g. CALC:MARK1:X 10 MHz
    'marker3_frequency': 'CALC:MARK3:X',     # pass frequency value e.g. CALC:MARK1:X 10 MHz
    'marker4_frequency': 'CALC:MARK4:X',     # pass frequency value e.g. CALC:MARK1:X 10 MHz
    'marker5_frequency': 'CALC:MARK5:X',     # pass frequency value e.g. CALC:MARK1:X 10 MHz
    'marker6_frequency': 'CALC:MARK6:X',     # pass frequency value e.g. CALC:MARK1:X 10 MHz
    'marker1_power': 'CALC:MARK1:Y',        # no par, query only e.g. :CALC:MARK1:Y?
    'marker2_power': 'CALC:MARK2:Y',        # no par, query only e.g. :CALC:MARK2:Y?
    'marker3_power': 'CALC:MARK3:Y',        # no par, query only e.g. :CALC:MARK3:Y?
    'marker4_power': 'CALC:MARK4:Y',        # no par, query only e.g. :CALC:MARK4:Y?
    'marker5_power': 'CALC:MARK5:Y',        # no par, query only e.g. :CALC:MARK5:Y?
    'marker6_power': 'CALC:MARK6:Y',        # no par, query only e.g. :CALC:MARK6:Y?
    'marker_table': 'CALC1:MARK:TABL:STAT', # pass marker table state e.g. :CALCulate<n>:MARKer:TABLe ON
    'marker1-function': 'CALC:MARK1:FUNC',  # pass marker function e.g. CALC:MARK1:FUNC NOIS
    'marker1-mode': 'CALC:MARK1:MODE'       # pass marker mode e.g. CALC:MARK:MODE DELT
    
}
