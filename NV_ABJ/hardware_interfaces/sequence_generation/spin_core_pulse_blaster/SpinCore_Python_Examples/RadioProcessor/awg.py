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
# \file awg.py
# \brief This program demonstrates the use of the shaped pulse feature of the 
# RadioProcessor
# \ingroup RP
#

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *
import math

CLOCK_FREQ = 75.0

# User friendly names for the control bits
TX_ENABLE = 1
TX_DISABLE = 0
PHASE_RESET = 1
NO_PHASE_RESET = 0
DO_TRIGGER = 1
NO_TRIGGER = 0
USE_SHAPE = 1
NO_SHAPE = 0

pi = 3.1415926

def program_and_start(amp1,amp2,freq):
    pb_set_amp(amp1, 0)
    pb_set_amp(amp2, 1)
    # There are two more amplitude registers that can be programmed, but are
    # not used for this demo program.
    #pb_set_amp(0.5, 2);
    #pb_set_amp(0.3, 3);

    # set the frequency for the sine wave
    pb_start_programming(FREQ_REGS)
    pb_set_freq(freq * MHz)
    pb_stop_programming()

    # Set the TX phase to 0.0
    pb_start_programming(TX_PHASE_REGS)  
    pb_set_phase(0.0)	# in degrees
    pb_stop_programming()

    print("Amplitude 1: %f" %amp1)
    print("Amplitude 2: %f" %amp2)
    print("Freqency:    %fMHz" %freq)

    pb_start_programming(PULSE_PROGRAM)
    
    # 10us shaped pulse, with amplitude set by register 0. TTL outputs on
    start = pb_inst_radio_shape(0, 0, 0, 0, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER, USE_SHAPE, 0, 0x0F, CONTINUE, 0, 10.0 * us)

	# 20us shaped pulse, with amplitude set by register 1. TTL outputs on
    pb_inst_radio_shape(0, 0, 0, 0, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER, USE_SHAPE, 1, 0x0F, CONTINUE, 0, 20.0 * us)

	# Output no pulse for 1ms. reset the phase. TTL outputs off. Execution
	# branches back to the beginning of the pulse program.
    pb_inst_radio_shape(0, 0, 0, 0, TX_DISABLE, PHASE_RESET, NO_TRIGGER, NO_SHAPE, 0, 0x00, BRANCH, start, 1.0 * ms) 
    
    pb_stop_programming()

    pb_reset();
    pb_start();
    
def pause():
    input("Press enter to continue...")

def detect_boards():
    global numBoards
    
    numBoards = pb_count_boards()
    
    if numBoards <= 0:
        print("No Boards were detected in your system. Verify that the board "
       "is firmly secured in the PCI slot.\n")
        pause()
        exit(-1)
        
def select_boards():
    while True:
        try:
            choice = int(input(f"Found {numBoards} boards in your system. Which board should be used? (0-{numBoards-1}): "))
            if choice < 0 or choice >= numBoards:
                print("Invalid Board Number (%d)." % choice)
            else:
                pb_select_board(choice)
                print("Board %d selected." % choice)
                break;
        except ValueError:
            print("Incorrect input. Please enter a valid board number.")
            
# The following functions show how to build up arrays with different shapes
# for use with the pb_dds_load() function.

# Make a sinc shape, for use in generating soft pulses.
def shape_make_sinc(shape_data, lobes):
    scale = lobes * 2.0 * pi

    for i in range(1024):
        x = (i - 512) * scale / 1024.0
        if x == 0:
            shape_data[i] = 1.0
        else:
            shape_data[i] = math.sin(x) / x;
 
# Make one period of a sinewave
def shape_make_sin(shape_data):
    for i in range(1024):
        shape_data[i] = math.sin (2.0 * pi * ( i / 1024.0))

# Make a ramp function. This is an example of a different kind of shape you
# could potentially for a shaped pulse
def shape_make_ramp():
    for i in range(1024):
        shape_data[i] = i / 1024.0   


dds_data = [0]*1024
shape_data = [0]*1024    

#Uncommenting the line below will generate a debug log in your current
#directory that can help debug any problems that you may be experiencing
#pb_set_debug(1)

print("Copyright (c) 2023 SpinCore Technologies, Inc.\n")

print("Using SpinAPI Library version %s" % pb_get_version())

# If there is more than one board in the system, have the user specify. 
detect_boards()

if numBoards > 1:
    select_boards()

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    pause()
    exit(-1)
    
pb_core_clock(CLOCK_FREQ)
pb_set_defaults()

#Set the contents of the arrays to the desired waveform
#(see below for the definition of these functions)
shape_make_sinc(shape_data, 3)
shape_make_sin(dds_data)

# And then load them on the board
pb_dds_load(shape_data, DEVICE_SHAPE)
pb_dds_load(dds_data, DEVICE_DDS)

print("\n")
print("This program demonstrates the shaped pulse feature of the RadioProcessor. It "
 "will output two sinc shaped pulses, with the amplitude you specify. You can "
 "also specify the RF frequency used. The TTL outputs are enabled during the "
 "pulse, and can be used to trigger your oscilloscope.\n"
 "This is is only the basics of what you can do. Please see the RadioProcessor "
 "documentation and source code of this program for more details.\n")

print("Press CTRL-C at any time to quit\n")

# Loop continuously, gathering parameters for the demo, and the programming
# the board appropriately.

while True:
    
    amp1 = float(input("Enter amplitude for pulse 1 (value from 0.0 to 1.0): "))

    amp2 = float(input("Enter amplitude for pulse 2 (value from 0.0 to 1.0): "))

    freq = float(input("Enter RF frequency (in MHz): "))

    program_and_start(amp1, amp2, freq)

print("\n")
pause()

# Stop the program
pb_stop();
    
# Release control of the board
pb_close()
