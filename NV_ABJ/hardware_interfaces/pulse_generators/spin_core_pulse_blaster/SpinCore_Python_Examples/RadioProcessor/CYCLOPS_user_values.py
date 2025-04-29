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
# CYCLOPS_user_values.py
# This program contains a list of user defined variables to be used
# for the CYCLOPS_nmr.py example program. 
#
# SpinCore Technologies, Inc.
# www.spincore.com
# 
# Hardcoded argument values

#BOARD_NUMBER is the number of the board in your system to be used by spinnmr. If you have multiple boards attached to your system, please make sure this value is correct.
BOARD_NUMBER=0

#ADC_FREQUENCY (MHz) is the analog to digital converter frequency of the RadioProcessor board selected.
ADC_FREQUENCY=75.0

#If ENABLE_TX is set to 0, the transmitter is disabled. If it is set to 1, the transmitter is enabled.
ENABLE_TX=1

#If ENABLE_RX is set to 0, the receiver is disabled. If it is set to 1, the receiver is enabled.
ENABLE_RX=1

#REPETITION_DELAY (s)  is the time between each consecutive scan. It must be greater than 0.
REPETITION_DELAY=1.0

#NUMBER_OF_SCANS is the number of consecutive scans to run. There must be atleast one scan.
NUMBER_OF_SCANS=16

#NUMBER_POINTS is the number of NMR data points the board will acquire during the scan. It must be between 0 and 16384.
NUMBER_POINTS=16384

#SPECTROMETER_FREQUENCY (MHz) must be between 0 and 100.
SPECTROMETER_FREQUENCY=None

#SPECTRAL_WIDTH (kHz) must be between 0.150 and 10000
SPECTRAL_WIDTH=500

#PULSE_TIME (microseconds) must be atleast 0.065.
PULSE_TIME=14.0

#TRANS_TIME (microseconds) must be atleast 0.065.
TRANS_TIME=130

#TX_PHASE (degrees) must be greater than or equal to zero.
#this is the initial Tx Phase, successive scans will be offset by 90 degrees from the previous scan.
TX_PHASE=0

#AMPLITUDE of the excitation signal. Must be between 0.0 and 1.0.
AMPLITUDE=1.0

#SHAPED_PULSE will control the shaped pulse feature of the RadioProcessor. Setting SHAPED_PULSE to 1 will enable this feature. 0 will disabled this feature.
SHAPED_PULSE=0

#BYPASS_FIR will disabled the FIR filter if set to 1. Setting BYPASS_FIR to 0 will enable the FIR filter.
BYPASSFIR=1

#FNAME is the name of the output file the data will be acquired data will be stored in. File extensions will be appended automatically.
FNAME="cycnmr"

#DEBUG enables DEBUGGING output log.
DEBUG=0

REAL_ADD_SUB_0=1
IMAG_ADD_SUB_0=1
SWAP_0=0

REAL_ADD_SUB_1=1
IMAG_ADD_SUB_1=0
SWAP_1=1

REAL_ADD_SUB_2=0
IMAG_ADD_SUB_2=0
SWAP_2=0

REAL_ADD_SUB_3=0
IMAG_ADD_SUB_3=1
SWAP_3=1

#If verbose mode is disabled, the program will output nothing.
VERBOSE=1

#Use TTL Blanking
BLANKING_EN=1

#BLANKING_BIT specifies which TTL Flag to use for the power amplifier blanking signal.
#Refer to your products Owner's Manual for additional information
BLANKING_BITS=2

#TTL Blanking Delay (in milliseconds)
BLANKING_DELAY=5.00
