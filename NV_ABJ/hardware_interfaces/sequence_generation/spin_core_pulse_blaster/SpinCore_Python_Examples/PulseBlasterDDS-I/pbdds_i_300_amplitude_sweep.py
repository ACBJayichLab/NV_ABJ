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
# 1. The origin of this software must not be misrepresented   you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

##
# \file pbdds_i_300_amplitude_sweep.c 
# \brief This example program tests demonstrates an amplitude sweep using all the registers of the 
# PBDDS-I-300.
# \ingroup pbddsI
#

CLOCK_FREQ = 75.0

# User friendly names for the control bits
TX_ENABLE = 1
TX_DISABLE = 0
PHASE_RESET = 1
NO_PHASE_RESET = 0

FREQUENCY = 1.0   # The frequency of the output sine wave, in MHz.
NUM_AMPLITUDE_REGISTERS = 4 # Specify the number of registers your board has
RATE = 3.6  # Time (in milliseconds) between amplitude changes 

try:
    # Load spinapi.py in current folder
    from spinapi import *
except:
    # Load spinapi.py in the folder one level up 
    import sys
    sys.path.append('../')
    from spinapi import *

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

pb_set_defaults()
pb_core_clock(CLOCK_FREQ)

print("Clock frequency: %.2lf MHz\n" % CLOCK_FREQ)
print("This example program demonstrates an amplitude sweep using the PBDDS-I-300.\n")
print("This program has specified %d different amplitudes to sweep using a %.2f MHz " %(NUM_AMPLITUDE_REGISTERS, FREQUENCY))
print("sine wave. The sweep should go from maximum to minimum amplitude, and then "
    "from minimum to maximum amplitude indefinitely. The time between amplitude "
    "changes is %.2f ms." % RATE)

# Program the pulse program
pb_start_programming(FREQ_REGS)
pb_set_freq(FREQUENCY * MHz)
pb_stop_programming()

# Program the first 2 phase registers
pb_start_programming(TX_PHASE_REGS)
pb_set_phase(0.0)		# Register 0
pb_set_phase(0.0)		# Register 1
pb_stop_programming()

cur_amp = 1.0

for i in range(NUM_AMPLITUDE_REGISTERS):
    pb_set_amp(cur_amp, i)
    cur_amp -= 1.0 / NUM_AMPLITUDE_REGISTERS
    
# Write the pulse program
pb_start_programming(PULSE_PROGRAM)

start = pb_inst_dds(0,0, TX_DISABLE, PHASE_RESET, 0x000, CONTINUE, 0, 1.0 * us)

for i in range(NUM_AMPLITUDE_REGISTERS): # Program instructions (increasing)
    pb_inst_dds_shape(0,0, TX_ENABLE, NO_PHASE_RESET, 0, i, 0x1FF, CONTINUE, 0, RATE * ms)

for i in range(NUM_AMPLITUDE_REGISTERS - 1, 0, -1): # Program instructions (decreasing)
    pb_inst_dds_shape(0,0, TX_ENABLE, NO_PHASE_RESET, 0, i, 0x1FF, CONTINUE, 0, RATE * ms)  

pb_inst_dds(0,0, TX_ENABLE, NO_PHASE_RESET, 0x1FF, BRANCH, start, RATE * ms)  
	
pb_stop_programming()  

# Trigger the board
pb_reset()
pb_start()

# Release control of the board
pb_close()

pause()
