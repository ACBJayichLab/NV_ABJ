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
# 1. The origin of this software must not be misrepresented you must not
# claim that you wrote the original software. If you use this software in a
# product, an acknowledgment in the product documentation would be appreciated
# but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
# misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#

##
# \file pb24_ex3.py
# PulseBlaster24 Example 3
#
# \brief Example program for PulseBlaster24 boards
# 
# This demonstrates the ability to set the default flag states 
# on the certain PB24 designs.
# \ingroup pb24
#

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
            
def input_clock():
    global clock
    while True:
        try:
            clock = float(input("\nPlease enter internal clock frequency (MHz): "))
            break  # Break out of the loop if a valid number is entered
        except ValueError:
            print("Incorrect input. Please enter a valid clock frequency.")


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


# User input clock
input_clock()

# Tell the driver what clock frequency the board has (in MHz)
pb_core_clock(clock)

print("Clock frequency: %1fMHz\n" %clock)
print("TTL outputs 0-3 will generate a pulse with a period of "
    "100 ms.  The outputs will be high for 60 ms, low for 40 ms, and "
    "then program will repeat.\n")

# Prepare the board to receive pulse program instructions
pb_start_programming(PULSE_PROGRAM)

# Instruction 0 - Continue to instruction 1 in 20ns
# The lower 4 bits (all BNC connectors) will be driving high
# For PBESR-PRO boards, or-ing THREE_PERIOD with the flags
# causes a 3 period short pulse to be used. 
start = pb_inst_pbonly(0xF, CONTINUE, 0, 20.0 * ms)

# Instruction 1 - Continue to instruction 2 in 40ns
# The lower 4 bits (all BNC connectors) will be driving high
# the entire 40ns.
pb_inst_pbonly(0xF, CONTINUE, 0, 40.0 * ms)

# Instruction 2 - Branch to "start" (Instruction 0) in 40ns
# Outputs are off
pb_inst_pbonly(0, BRANCH, start, 40.0 * ms)

pb_stop_programming() # Finished sending instructions

# Trigger the board
pb_reset()
pb_start()

# End communication with the PulseBlaster24 board. The pulse program
# will continue to run even after this is called.
pb_close()
pause()
