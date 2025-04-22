# Copyright (c) 2023 SpinCore Technologies, Inc.
#   http://www.spincore.com
#
# This software is provided 'as-is', without any express or implied warranty. 
# In no event will the authors be held liable for any damages arising from the 
# use of this software.
#
# Permission is granted to anyone to use this software for any purpose, 
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

##
# singlepulse.py
# Modified from singlepulse_nmr.h
#
#	This program is used to control the RadioProcessor series of boards in conjuction with the iSpin setup.
#	It generates a single RF pulse of variable shape, frequency, amplitude, phase and duration.
#	It then acquires the NMR response of the perturbing pulse.
#
# SpinCore Technologies, Inc.
# www.spincore.com
# 

NUM_ARGUMENTS = 19
MAX_FFT = 48716
FNAME_SIZE = 256

BOARD_STATUS_IDLE = 0x3
BOARD_STATUS_BUSY = 0x6

# User friendly names for the phase registers of the cos and sin channels
PHASE000 = 0
PHASE090 = 1
PHASE180 = 2
PHASE270 = 3

# User friendly names for the control bits
TX_ENABLE = 1
TX_DISABLE = 0
PHASE_RESET = 1
NO_PHASE_RESET = 0
DO_TRIGGER = 1
NO_TRIGGER = 0
AMP0 = 0
BLANK_PA = 0x00

# Error return values for Hahn Echo
INVALID_ARGUMENTS = -1
BOARD_NOT_DETECTED = -2
INVALID_NUM_ARGUMENTS = -3
RX_AND_TX_DISABLED = -4
INVALID_DATA_FROM_BOARD = -5
PROGRAMMING_FAILED = -6
CONFIGURATION_FAILED = -7
ALLOCATION_FAILED = -8
DATA_RETRIEVAL_FAILED = -9

class SCANPARAMS:
    def __init__(self):
        self.file_name = None
        
        # Board Parameters
        self.board_num = 0
        self.deblank_bit_mask = None
        self.deblank_bit = 0
        self.debug = 0
        
        # Frequency Parameters
        self.ADC_frequency = 0.0    # MHz
        self.SF = 0.0               # MHz
        self.res_frequency = 0.0    # MHz
        self.SW = 0.0               # kHz
        self.actual_SW = 0.0        # kHz
        
        # Pulse Parameters
        self.enable_tx = 0
        self.use_shape = 0
        self.amplitude = 0.0
        self.p90_time = 0.0         # us
        self.p90_phase = 0.0        # degrees
        
        # Acquisition Parameters
        self.enable_rx = 0
        self.bypass_fir = 0
        self.num_points = 0
        self.num_scans = 0
        self.scan_time = 0.0       # ms
        
        # Delay Parameters
        self.deblank_delay = 0.0    # ms
        self.transient_delay = 0.0  # us
        self.repetition_delay = 0.0 # s
