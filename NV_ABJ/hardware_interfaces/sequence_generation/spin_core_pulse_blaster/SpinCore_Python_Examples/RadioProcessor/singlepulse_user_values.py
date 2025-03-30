 #########################################################
 # singlepulse_user_values
 #	This file is intended to define the values used in singlepulse_nmr.py.

 # 	SpinCore Technologies, Inc.
 #	
 #########################################################


######################BOARD SETTINGS####################### 

# \file_NAME is the name of the output file the data will be acquired data will be stored in. File extensions will be appended automatically.
FILE_NAME = "spnmr"



# Board Parameters

# BOARD_NUMBER is the number of the board in your system to be used by spinnmr. If you have multiple boards attached to your system, please make sure this value is correct.
BOARD_NUMBER=0

# BLANK_BIT specifies which TTL Flag to use for the power amplifier blanking signal.
# Refer to your products Owner's Manual for additional information
BLANK_BIT=2

# DEBUG Enables the debug output log.
DEBUG=0



# Frequency Parameters

# ADC_FREQUENCY (MHz) is the analog to digital converter frequency of the RadioProcessor board selected.
ADC_FREQUENCY=75.0

# SPECTROMETER_FREQUENCY (MHz) must be between 0 and 100.
SPECTROMETER_FREQUENCY=None

# SPECTRAL_WIDTH (kHz) must be between 0.150 and 10000
SPECTRAL_WIDTH=200



# Pulse Parameters

# If ENABLE_TX is set to 0, the transmitter is disabled. If it is to 1, the transmitter is enabled.
ENABLE_TX=1

# USE_SHAPE will control the shaped pulse feature of the RadioProcessor. Setting SHAPED_PULSE to 1 will enable this feature. 0 will disabled this feature.
USE_SHAPE=0

# AMPLITUDE of the excitation signal. Must be between 0.0 and 1.0.
AMPLITUDE=1.0

# PULSE90_TIME (microseconds) must be atleast 0.065.
PULSE90_TIME=2

# PULSE_PHASE (degrees) must be greater than or equal to zero.
PULSE90_PHASE=0



# Acquisition Parameters

# If ENABLE_RX is set to 0, the receiver is disabled. If it is set to 1, the receiver is enabled.
ENABLE_RX=1

# BYPASS_FIR will disabled the FIR filter if set to 1. Setting BYPASS_FIR to 0 will enable the FIR filter.
ENABLE_BYPASS_FIR=1

# NUMBER_POINTS is the number of NMR data points the board will acquire during the scan. It must be between 0 and 16384. If it is not a power of 2, it will be rounded up to the nearest power of 2.
NUMBER_POINTS=1024

# NUMBER_OF_SCANS is the number of consecutive scans to run. There must be at least one scan. Due to latencies, scan count may not be consecutive.
NUMBER_OF_SCANS=1



# Delay Parameters

# TTL Blanking Delay (in milliseconds) must be atleast 0.000065.
BLANKING_DELAY=3.00

# TRANS_DELAY (microseconds) must be atleast 0.065.
TRANS_DELAY=150

# REPETITION_DELAY (s)  is the time between each consecutive scan. It must be greater than 0.
REPETITION_DELAY=1.0
