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

#
# CYCLOPS.py
# This program is used to control the RadioProcessor series of boards.
# This file contains constants and data structures used by CYCLOPS_nmr.py. 
#
# SpinCore Technologies, Inc.
# www.spincore.com
# 
#

NUM_ARGUMENTS = 33
FNAME_SIZE = 256
MAX_FFT = 32768

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

ADD = 1
SUB = 0
SWAP = 1
NO_SWAP = 0

# Error return values for spinnmr
INVALID_ARGUMENTS  =   -1
BOARD_NOT_DETECTED  =   -2
INVALID_NUM_ARGUMENTS = -3
RX_AND_TX_DISABLED    = -4
INVALID_DATA_FROM_BOARD = -5
PROGRAMMING_FAILED    =  -6

class SCANPARAMS:
    def __init__(self):
        self.outputFilename = None
        self.board_num = None
        self.nPoints = 0
        self.nScans = 0
        self.bypass_fir = 0
        self.use_shape = 0
        self.enable_rx = 0
        self.enable_tx = 0
        self.verbose = 0
        self.debug = 0
        self.spectrometerFrequency = None
        self.spectralWidth = 0.0
        self.actualSpectralWidth = 0.0
        self.pulseTime = 0.0
        self.transTime = 0.0
        self.repetitionDelay = 0.0
        self.adcFrequency = 0.0
        self.amplitude = 0.0
        self.tx_phase = 0.0
        self.wait_time = 0.0
        self.blankingEnable = None
        self.blankingBit = None
        self.blankingDelay = 0.0


# Define CYCLOPSPARAMS struct in Python
class CYCLOPSPARAMS:
    def __init__(self):
        self.phase_0 = 0
        self.add_sub_re_0 = 0
        self.add_sub_im_0 = 0
        self.swap_0 = 0

        self.phase_1 = 0
        self.add_sub_re_1 = 0
        self.add_sub_im_1 = 0
        self.swap_1 = 0

        self.phase_2 = 0
        self.add_sub_re_2 = 0
        self.add_sub_im_2 = 0
        self.swap_2 = 0

        self.phase_3 = 0
        self.add_sub_re_3 = 0
        self.add_sub_im_3 = 0
        self.swap_3 = 0
