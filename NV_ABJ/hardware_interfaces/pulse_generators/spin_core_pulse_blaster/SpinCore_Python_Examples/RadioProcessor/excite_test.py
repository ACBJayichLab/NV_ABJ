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
# 1. The origin of this software must not be misrepresented    you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#  
 
##
# \file excite_test.c
# \brief The example program tests the excitation portion of the RadioProcessor.
# This program will produce a 1MHz signal on the oscilloscope that is on
# for 10 microseconds, off for 1 milisecond, and the repeat this pattern.
# \ingroup RP
#  

CLOCK_FREQ = 75.0

# User friendly names for the control bits
TX_ENABLE = 1
TX_DISABLE = 0
PHASE_RESET = 1
NO_PHASE_RESET = 0
DO_TRIGGER = 1
NO_TRIGGER = 0

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

print("Clock frequency: %.2lfMHz\n" % CLOCK_FREQ)
print("The example program tests the excitation portion of the "
    "RadioProcessor.  This program will produce a 1MHz signal on the "
    "RF connector that is on for 10 microseconds, off for 1 "
    "milisecond, and will then repeat this pattern.\nAll TTL flags "
    "will be high during the RF signal and low while it is off.\n")

# Write 1 MHz to the first frequency register
pb_start_programming(FREQ_REGS)   
pb_set_freq(1.0 * MHz)   	  
pb_stop_programming()   

# Write 0.0 degrees to the first phase register of all channels
pb_start_programming(TX_PHASE_REGS)
pb_set_phase(0.0)
pb_stop_programming()

pb_start_programming(COS_PHASE_REGS)
pb_set_phase(0.0)
pb_stop_programming()

pb_start_programming(SIN_PHASE_REGS)
pb_set_phase(0.0)
pb_stop_programming()   

# Write the pulse program
pb_start_programming(PULSE_PROGRAM)   

# This instruction enables a 1 MHz analog output
start = pb_inst_radio(0, 0, 0, 0, TX_ENABLE, NO_PHASE_RESET, NO_TRIGGER, 0x3F, CONTINUE, 0, 10.0 * us);

# This instruction disables the analog output (and resets the phase in
# preparation for the next instruction)
pb_inst_radio(0, 0, 0, 0, TX_DISABLE, PHASE_RESET, NO_TRIGGER, 0x0, BRANCH, start, 1.0 * ms);

pb_stop_programming()   

# Trigger program
pb_reset()   
pb_start()   

# print warning and wait for user to press a key while board runs
print("***WARNING***\nIf the command line is closed without a preceeding "
 "key press, the board will continue to run until excite_test is run"
 " again and allowed to complete properly.");
pause()

# Stop the program
pb_stop()

# Release control of the board   
pb_close() 
